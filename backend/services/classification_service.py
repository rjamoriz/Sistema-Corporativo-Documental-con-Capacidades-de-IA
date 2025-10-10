"""
Servicio de Clasificación de Documentos
Híbrido ML + Ontología: clasificación con transformers y refinamiento semántico con OWL
"""
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

from backend.core.logging_config import logger
from backend.core.config import settings
from backend.models.database_models import Document, DocumentClassification, DocumentStatus
from backend.services.ontology_service import ontology_service


class ClassificationService:
    """Servicio para clasificación de documentos"""
    
    def __init__(self):
        # Cargar modelo de clasificación
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(settings.CLASSIFICATION_MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(settings.CLASSIFICATION_MODEL)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            logger.info(f"Loaded classification model: {settings.CLASSIFICATION_MODEL} on {self.device}")
        except Exception as e:
            logger.warning(f"Could not load custom model, using default: {e}")
            self.classifier = pipeline("text-classification", model="dccuchile/bert-base-spanish-wwm-uncased")
        
        # Mapeo de categorías
        self.category_mapping = {
            "LEGAL": DocumentClassification.LEGAL,
            "FINANCIAL": DocumentClassification.FINANCIAL,
            "HR": DocumentClassification.HR,
            "TECHNICAL": DocumentClassification.TECHNICAL,
            "MARKETING": DocumentClassification.MARKETING,
            "OPERATIONS": DocumentClassification.OPERATIONS,
            "COMPLIANCE": DocumentClassification.COMPLIANCE,
            "SENSITIVE": DocumentClassification.SENSITIVE,
            "UNCLASSIFIED": DocumentClassification.UNCLASSIFIED
        }
        
        # Palabras clave para clasificación basada en reglas (fallback)
        self.keyword_rules = {
            DocumentClassification.LEGAL: [
                "contrato", "acuerdo", "demanda", "sentencia", "tribunal", "juzgado",
                "artículo", "ley", "normativa", "reglamento", "decreto", "resolución",
                "litigio", "arbitraje", "cláusula", "firmante", "notario"
            ],
            DocumentClassification.FINANCIAL: [
                "factura", "presupuesto", "balance", "cuenta", "ingreso", "gasto",
                "iva", "importe", "precio", "coste", "inversión", "beneficio",
                "pérdida", "activo", "pasivo", "patrimonio", "auditoría", "fiscal"
            ],
            DocumentClassification.HR: [
                "nómina", "empleado", "trabajador", "salario", "contratación", "despido",
                "vacaciones", "permiso", "baja", "convenio colectivo", "recursos humanos",
                "formación", "evaluación", "rendimiento", "puesto", "cargo"
            ],
            DocumentClassification.TECHNICAL: [
                "especificación", "manual", "arquitectura", "diseño", "desarrollo",
                "implementación", "código", "sistema", "software", "hardware",
                "servidor", "base de datos", "api", "protocolo", "algoritmo"
            ],
            DocumentClassification.COMPLIANCE: [
                "rgpd", "gdpr", "lopd", "protección de datos", "consentimiento",
                "responsable del tratamiento", "encargado del tratamiento", "dpo",
                "delegado de protección", "impacto", "riesgo", "cumplimiento",
                "auditoría", "certificación", "iso", "norma"
            ],
            DocumentClassification.SENSITIVE: [
                "confidencial", "secreto", "reservado", "privado", "clasificado",
                "datos personales", "datos sensibles", "salud", "ideología",
                "afiliación sindical", "religión", "orientación sexual", "origen racial"
            ]
        }
    
    async def classify_document(
        self,
        document: Document,
        text: str,
        db: AsyncSession,
        use_ontology: bool = True
    ) -> Dict:
        """
        Clasifica un documento automáticamente con enfoque híbrido ML + Ontología
        
        Pipeline:
        1. Clasificación ML inicial (rápida)
        2. Refinamiento semántico con ontología OWL (si use_ontology=True)
        3. Validación de metadatos contra restricciones OWL
        4. Inferencia automática de riesgo
        
        Args:
            document: Documento a clasificar
            text: Texto del documento
            db: Sesión de base de datos
            use_ontology: Si True, usa refinamiento con ontología OWL
            
        Returns:
            Dict: Resultado de clasificación con categoría, confianza, validación y riesgo
        """
        try:
            # Limitar texto para clasificación (primeros 512 tokens aprox)
            text_sample = text[:2000]
            
            # PASO 1: Clasificación ML inicial
            if hasattr(self, 'model'):
                classification = await self._classify_with_model(text_sample)
            else:
                classification = await self._classify_with_pipeline(text_sample)
            
            # Si la confianza es baja, aplicar reglas
            if classification["confidence"] < 0.6:
                rule_based = self._classify_with_rules(text)
                if rule_based["confidence"] > classification["confidence"]:
                    classification = rule_based
            
            # PASO 2: Refinamiento semántico con ontología OWL (si habilitado)
            ontology_result = None
            if use_ontology:
                try:
                    ontology_result = ontology_service.classify_document(
                        content=text,
                        metadata=document.metadata_ or {}
                    )
                    
                    if ontology_result and ontology_result.get("confidence", 0) > 0.5:
                        # Enriquecer con clasificación ontológica
                        classification["ontology_class"] = ontology_result["class_name"]
                        classification["ontology_label"] = ontology_result["class_label"]
                        classification["ontology_confidence"] = ontology_result["confidence"]
                        classification["matched_keywords"] = ontology_result["matched_keywords"]
                        
                        # Si la ontología tiene alta confianza, ajustar categoría ML
                        if ontology_result["confidence"] > classification["confidence"]:
                            classification["confidence"] = (
                                classification["confidence"] * 0.4 + 
                                ontology_result["confidence"] * 0.6
                            )
                            classification["method"] = f"{classification['method']}+ontology"
                        
                        logger.info(
                            f"Ontology refinement: {ontology_result['class_label']} "
                            f"(confidence: {ontology_result['confidence']:.2f})"
                        )
                        
                except Exception as e:
                    logger.warning(f"Ontology classification failed: {e}")
                    classification["ontology_error"] = str(e)
            
            # PASO 3: Validación de metadatos contra restricciones OWL
            validation_result = None
            if use_ontology and ontology_result:
                try:
                    class_uri = ontology_service.TF[ontology_result["class_name"]]
                    is_valid, errors = ontology_service.validate_metadata(
                        class_uri,
                        document.metadata_ or {}
                    )
                    
                    validation_result = {
                        "is_valid": is_valid,
                        "errors": errors,
                        "required_fields": ontology_service.get_required_fields(class_uri)
                    }
                    
                    classification["metadata_validation"] = validation_result
                    
                    if not is_valid:
                        logger.warning(
                            f"Metadata validation failed for {ontology_result['class_name']}: "
                            f"{len(errors)} errors"
                        )
                        
                except Exception as e:
                    logger.warning(f"Metadata validation failed: {e}")
                    classification["validation_error"] = str(e)
            
            # PASO 4: Inferencia automática de nivel de riesgo
            risk_level = None
            if use_ontology and ontology_result:
                try:
                    class_uri = ontology_service.TF[ontology_result["class_name"]]
                    risk_level = ontology_service.infer_risk_level(
                        class_uri,
                        document.metadata_ or {}
                    )
                    
                    classification["inferred_risk_level"] = risk_level
                    
                    logger.info(
                        f"Risk inference: {risk_level} for {ontology_result['class_name']}"
                    )
                    
                except Exception as e:
                    logger.warning(f"Risk inference failed: {e}")
                    classification["risk_error"] = str(e)
            
            # Actualizar documento con metadata enriquecida
            category = classification["category"]
            document.classification = category
            document.metadata_["classification_confidence"] = classification["confidence"]
            document.metadata_["classification_method"] = classification["method"]
            
            # Guardar resultados de ontología
            if ontology_result:
                document.metadata_["ontology_class"] = ontology_result["class_name"]
                document.metadata_["ontology_label"] = ontology_result["class_label"]
                document.metadata_["ontology_confidence"] = ontology_result["confidence"]
                document.metadata_["matched_keywords"] = ontology_result["matched_keywords"]
            
            # Guardar validación
            if validation_result:
                document.metadata_["metadata_valid"] = validation_result["is_valid"]
                document.metadata_["metadata_errors"] = validation_result["errors"]
                document.metadata_["required_fields"] = validation_result["required_fields"]
            
            # Guardar riesgo inferido
            if risk_level:
                document.metadata_["inferred_risk_level"] = risk_level
            
            await db.commit()
            
            logger.info(
                f"Document {document.id} classified as {category} "
                f"(ML confidence: {classification['confidence']:.2f}, "
                f"Ontology: {ontology_result['class_label'] if ontology_result else 'N/A'}, "
                f"Risk: {risk_level or 'N/A'})"
            )
            
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying document {document.id}: {e}", exc_info=True)
            return {
                "category": DocumentClassification.UNCLASSIFIED,
                "confidence": 0.0,
                "method": "error",
                "error": str(e)
            }
    
    async def _classify_with_model(self, text: str) -> Dict:
        """Clasifica usando modelo transformer"""
        try:
            # Tokenizar
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Inferencia
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Obtener predicción más probable
            confidence, predicted_class = torch.max(predictions, dim=1)
            
            # Mapear a categoría
            class_labels = list(self.category_mapping.keys())
            predicted_label = class_labels[predicted_class.item()] if predicted_class.item() < len(class_labels) else "UNCLASSIFIED"
            category = self.category_mapping.get(predicted_label, DocumentClassification.UNCLASSIFIED)
            
            return {
                "category": category,
                "confidence": confidence.item(),
                "method": "transformer_model"
            }
            
        except Exception as e:
            logger.error(f"Model classification failed: {e}", exc_info=True)
            return {
                "category": DocumentClassification.UNCLASSIFIED,
                "confidence": 0.0,
                "method": "model_error"
            }
    
    async def _classify_with_pipeline(self, text: str) -> Dict:
        """Clasifica usando pipeline de Hugging Face"""
        try:
            result = self.classifier(text[:512])
            
            # Mapear resultado a categoría
            label = result[0]["label"].upper()
            category = self.category_mapping.get(label, DocumentClassification.UNCLASSIFIED)
            
            return {
                "category": category,
                "confidence": result[0]["score"],
                "method": "huggingface_pipeline"
            }
            
        except Exception as e:
            logger.error(f"Pipeline classification failed: {e}", exc_info=True)
            return {
                "category": DocumentClassification.UNCLASSIFIED,
                "confidence": 0.0,
                "method": "pipeline_error"
            }
    
    def _classify_with_rules(self, text: str) -> Dict:
        """Clasifica usando reglas basadas en palabras clave"""
        text_lower = text.lower()
        scores = {}
        
        # Contar coincidencias de palabras clave por categoría
        for category, keywords in self.keyword_rules.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return {
                "category": DocumentClassification.UNCLASSIFIED,
                "confidence": 0.0,
                "method": "rule_based_no_match"
            }
        
        # Categoría con más coincidencias
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        
        # Normalizar confianza (max 0.8 para reglas)
        confidence = min(0.8, max_score / 20)
        
        return {
            "category": best_category,
            "confidence": confidence,
            "method": "rule_based",
            "keyword_matches": max_score
        }
    
    async def batch_classify(
        self,
        documents: List[Document],
        texts: List[str],
        db: AsyncSession
    ) -> List[Dict]:
        """
        Clasifica múltiples documentos en batch
        
        Args:
            documents: Lista de documentos
            texts: Lista de textos correspondientes
            db: Sesión de base de datos
            
        Returns:
            List[Dict]: Lista de resultados de clasificación
        """
        results = []
        
        for document, text in zip(documents, texts):
            result = await self.classify_document(document, text, db)
            results.append(result)
        
        return results
    
    def get_classification_explanation(self, document: Document, text: str) -> Dict:
        """
        Proporciona explicación de por qué se asignó una clasificación
        Incluye tanto evidencias ML como semánticas de la ontología
        
        Args:
            document: Documento clasificado
            text: Texto del documento
            
        Returns:
            Dict: Explicación con evidencias ML y ontológicas
        """
        category = document.classification
        text_lower = text.lower()
        
        # Encontrar palabras clave que coinciden (ML)
        keywords = self.keyword_rules.get(category, [])
        matched_keywords = [kw for kw in keywords if kw in text_lower]
        
        # Extractos de texto donde aparecen las palabras clave
        evidence = []
        for keyword in matched_keywords[:5]:  # Top 5 coincidencias
            idx = text_lower.find(keyword)
            if idx != -1:
                start = max(0, idx - 50)
                end = min(len(text), idx + len(keyword) + 50)
                excerpt = text[start:end].strip()
                evidence.append({
                    "keyword": keyword,
                    "excerpt": f"...{excerpt}...",
                    "source": "ml_rules"
                })
        
        # Añadir evidencias de ontología si están disponibles
        if "ontology_class" in document.metadata_:
            ontology_keywords = document.metadata_.get("matched_keywords", [])
            for keyword in ontology_keywords[:5]:
                idx = text_lower.find(keyword.lower())
                if idx != -1:
                    start = max(0, idx - 50)
                    end = min(len(text), idx + len(keyword) + 50)
                    excerpt = text[start:end].strip()
                    evidence.append({
                        "keyword": keyword,
                        "excerpt": f"...{excerpt}...",
                        "source": "ontology"
                    })
        
        explanation = {
            "category": category.value,
            "confidence": document.metadata_.get("classification_confidence", 0.0),
            "method": document.metadata_.get("classification_method", "unknown"),
            "matched_keywords": matched_keywords,
            "evidence": evidence
        }
        
        # Añadir información ontológica si está disponible
        if "ontology_class" in document.metadata_:
            explanation["ontology"] = {
                "class_name": document.metadata_.get("ontology_class"),
                "class_label": document.metadata_.get("ontology_label"),
                "confidence": document.metadata_.get("ontology_confidence"),
                "matched_keywords": document.metadata_.get("matched_keywords", [])
            }
        
        # Añadir validación de metadatos
        if "metadata_valid" in document.metadata_:
            explanation["validation"] = {
                "is_valid": document.metadata_.get("metadata_valid"),
                "errors": document.metadata_.get("metadata_errors", []),
                "required_fields": document.metadata_.get("required_fields", [])
            }
        
        # Añadir nivel de riesgo inferido
        if "inferred_risk_level" in document.metadata_:
            explanation["risk"] = {
                "level": document.metadata_.get("inferred_risk_level"),
                "method": "ontology_inference"
            }
        
        return explanation
    
    async def get_ontology_hierarchy(self, document: Document) -> Optional[Dict]:
        """
        Obtiene la jerarquía ontológica completa para la clase del documento
        
        Args:
            document: Documento con clasificación ontológica
            
        Returns:
            Dict: Jerarquía con ancestros, hermanos y descendientes
        """
        if "ontology_class" not in document.metadata_:
            return None
        
        try:
            class_name = document.metadata_["ontology_class"]
            class_uri = ontology_service.TF[class_name]
            
            # Obtener info completa de la clase
            class_info = ontology_service.get_class_info(class_uri)
            
            # Obtener jerarquía completa
            hierarchy = ontology_service.get_hierarchy(class_uri)
            
            # Obtener documentos relacionados
            related_docs = ontology_service.get_related_documents(class_uri)
            
            # Obtener regulaciones aplicables
            regulations = ontology_service.get_compliance_regulations(class_uri)
            
            return {
                "class_info": class_info,
                "hierarchy": hierarchy,
                "related_documents": related_docs,
                "compliance_regulations": regulations
            }
            
        except Exception as e:
            logger.error(f"Error getting ontology hierarchy: {e}", exc_info=True)
            return None


# Instancia singleton del servicio
classification_service = ClassificationService()
