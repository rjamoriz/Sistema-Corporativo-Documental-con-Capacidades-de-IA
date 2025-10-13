"""
Validation Middleware
Middleware para validación automática de documentos contra terceros
"""
import asyncio
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.logging_config import logger
from models.database_models import Document, DocumentStatus
from services.validation.sanctions_service import sanctions_service
from services.validation.business_registry_service import business_registry_service
from services.validation.esg_service import esg_service
from services.notifications.notification_service import NotificationService, AlertPriority


class ValidationMiddleware:
    """
    Middleware para validación automática de documentos
    
    Se ejecuta automáticamente después de la extracción de texto
    para validar entidades contra listas de sanciones, registros
    mercantiles y bases de datos ESG.
    """
    
    def __init__(self):
        """Inicializa el middleware de validación"""
        self.notification_service = NotificationService()
        
        # Configuración de validación por tipo de documento
        self.validation_rules = {
            "contracts": {
                "sanctions": True,
                "business_registry": True,
                "esg": True,
                "auto_alert": True,
                "priority_threshold": 0.85  # Alerta si confidence >= 85%
            },
            "invoices": {
                "sanctions": True,
                "business_registry": True,
                "esg": False,
                "auto_alert": True,
                "priority_threshold": 0.90
            },
            "agreements": {
                "sanctions": True,
                "business_registry": True,
                "esg": True,
                "auto_alert": True,
                "priority_threshold": 0.80
            },
            "default": {
                "sanctions": True,
                "business_registry": False,
                "esg": False,
                "auto_alert": False,
                "priority_threshold": 0.95
            }
        }
    
    async def validate_document(
        self,
        document: Document,
        extracted_text: str,
        entities: List[Dict],
        db: AsyncSession
    ) -> Dict:
        """
        Valida un documento contra servicios de terceros
        
        Args:
            document: Documento a validar
            extracted_text: Texto extraído del documento
            entities: Lista de entidades extraídas (nombres, organizaciones)
            db: Sesión de base de datos
            
        Returns:
            Dict: Resultado de la validación con todas las verificaciones
        """
        try:
            logger.info(f"Starting automatic validation for document {document.id}")
            
            # Obtener reglas de validación según categoría del documento
            category = self._get_document_category(document)
            rules = self.validation_rules.get(category, self.validation_rules["default"])
            
            validation_results = {
                "document_id": str(document.id),
                "category": category,
                "rules_applied": rules,
                "sanctions_check": None,
                "business_registry_check": None,
                "esg_check": None,
                "flagged_entities": [],
                "total_entities_checked": len(entities),
                "alerts_sent": []
            }
            
            # Extraer nombres de personas y organizaciones
            person_names = [e["text"] for e in entities if e.get("type") == "PERSON"]
            org_names = [e["text"] for e in entities if e.get("type") == "ORGANIZATION"]
            
            all_entities = person_names + org_names
            
            if not all_entities:
                logger.info(f"No entities found in document {document.id}, skipping validation")
                return validation_results
            
            # Ejecutar validaciones en paralelo según las reglas
            tasks = []
            
            if rules["sanctions"]:
                tasks.append(self._check_sanctions(all_entities, document))
            
            if rules["business_registry"]:
                tasks.append(self._check_business_registry(org_names, document))
            
            if rules["esg"]:
                tasks.append(self._check_esg(org_names, document))
            
            # Ejecutar todas las validaciones
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Validation task {i} failed: {result}")
                    continue
                
                if i == 0 and rules["sanctions"]:
                    validation_results["sanctions_check"] = result
                    if result.get("flagged"):
                        validation_results["flagged_entities"].extend(result["matches"])
                
                elif i == 1 and rules["business_registry"]:
                    validation_results["business_registry_check"] = result
                    if result.get("issues_found"):
                        validation_results["flagged_entities"].extend(result["issues"])
                
                elif i == 2 and rules["esg"]:
                    validation_results["esg_check"] = result
                    if result.get("high_risk"):
                        validation_results["flagged_entities"].extend(result["risks"])
            
            # Enviar alertas automáticas si es necesario
            if rules["auto_alert"] and validation_results["flagged_entities"]:
                await self._send_alerts(
                    document=document,
                    flagged_entities=validation_results["flagged_entities"],
                    priority_threshold=rules["priority_threshold"]
                )
                validation_results["alerts_sent"] = True
            
            logger.info(
                f"Validation completed for document {document.id}: "
                f"{len(validation_results['flagged_entities'])} entities flagged"
            )
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in validation middleware for document {document.id}: {e}", exc_info=True)
            return {
                "document_id": str(document.id),
                "error": str(e),
                "flagged_entities": []
            }
    
    async def _check_sanctions(self, entities: List[str], document: Document) -> Dict:
        """Valida entidades contra listas de sanciones"""
        try:
            all_matches = []
            flagged = False
            
            for entity_name in entities:
                # Verificar contra todas las fuentes
                ofac_result = await sanctions_service.check_ofac(entity_name)
                eu_result = await sanctions_service.check_eu_sanctions(entity_name)
                wb_result = await sanctions_service.check_world_bank(entity_name)
                
                # Consolidar matches
                matches = []
                if ofac_result["match"]:
                    matches.extend(ofac_result["matches"])
                    flagged = True
                
                if eu_result["match"]:
                    matches.extend(eu_result["matches"])
                    flagged = True
                
                if wb_result["match"]:
                    matches.extend(wb_result["matches"])
                    flagged = True
                
                if matches:
                    all_matches.append({
                        "entity_name": entity_name,
                        "entity_type": "UNKNOWN",
                        "matches": matches,
                        "highest_confidence": max([m.get("confidence", 0) for m in matches])
                    })
            
            return {
                "checked": True,
                "flagged": flagged,
                "total_checked": len(entities),
                "matches_found": len(all_matches),
                "matches": all_matches
            }
            
        except Exception as e:
            logger.error(f"Sanctions check failed: {e}")
            return {
                "checked": False,
                "error": str(e)
            }
    
    async def _check_business_registry(self, org_names: List[str], document: Document) -> Dict:
        """Valida organizaciones contra registros mercantiles"""
        try:
            issues = []
            issues_found = False
            
            for org_name in org_names:
                result = await business_registry_service.verify_company(org_name)
                
                if not result.get("exists", False):
                    issues.append({
                        "entity_name": org_name,
                        "issue": "Company not found in registry",
                        "confidence": 0.9
                    })
                    issues_found = True
                
                elif result.get("status") not in ["ACTIVE", "ACTIVA"]:
                    issues.append({
                        "entity_name": org_name,
                        "issue": f"Company status: {result.get('status')}",
                        "confidence": 0.85
                    })
                    issues_found = True
            
            return {
                "checked": True,
                "issues_found": issues_found,
                "total_checked": len(org_names),
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"Business registry check failed: {e}")
            return {
                "checked": False,
                "error": str(e)
            }
    
    async def _check_esg(self, org_names: List[str], document: Document) -> Dict:
        """Valida organizaciones contra bases de datos ESG"""
        try:
            risks = []
            high_risk = False
            
            for org_name in org_names:
                result = await esg_service.get_esg_rating(org_name)
                
                if result.get("rating"):
                    esg_score = result["rating"].get("overall_score", 50)
                    
                    # Considerar alto riesgo si score < 30
                    if esg_score < 30:
                        risks.append({
                            "entity_name": org_name,
                            "risk_type": "ESG",
                            "esg_score": esg_score,
                            "issues": result.get("issues", []),
                            "confidence": 0.85
                        })
                        high_risk = True
            
            return {
                "checked": True,
                "high_risk": high_risk,
                "total_checked": len(org_names),
                "risks": risks
            }
            
        except Exception as e:
            logger.error(f"ESG check failed: {e}")
            return {
                "checked": False,
                "error": str(e)
            }
    
    async def _send_alerts(
        self,
        document: Document,
        flagged_entities: List[Dict],
        priority_threshold: float
    ):
        """Envía alertas automáticas para entidades flagged"""
        try:
            # Determinar prioridad basada en la confidence más alta
            max_confidence = 0
            if flagged_entities:
                max_confidence = max([
                    entity.get("highest_confidence", entity.get("confidence", 0))
                    for entity in flagged_entities
                ])
            
            # Determinar prioridad de alerta
            if max_confidence >= 0.95:
                priority = AlertPriority.CRITICAL
            elif max_confidence >= priority_threshold:
                priority = AlertPriority.HIGH
            elif max_confidence >= 0.70:
                priority = AlertPriority.MEDIUM
            else:
                priority = AlertPriority.LOW
            
            # Enviar alerta para cada entidad flagged
            async with self.notification_service as notif:
                for entity in flagged_entities[:5]:  # Limitar a 5 alertas por documento
                    await notif.send_sanctions_alert(
                        entity_name=entity.get("entity_name", "Unknown"),
                        entity_type=entity.get("entity_type", "UNKNOWN"),
                        matches=entity.get("matches", []),
                        confidence=entity.get("highest_confidence", entity.get("confidence", 0)),
                        document_id=document.id,
                        priority=priority
                    )
            
            logger.info(f"Sent {len(flagged_entities[:5])} alerts for document {document.id}")
            
        except Exception as e:
            logger.error(f"Failed to send alerts: {e}")
    
    def _get_document_category(self, document: Document) -> str:
        """Determina la categoría del documento para aplicar reglas"""
        # Intentar obtener categoría de metadata
        if document.metadata_:
            category = document.metadata_.get("category", "").lower()
            if category in self.validation_rules:
                return category
        
        # Inferir de filename
        filename_lower = document.filename.lower()
        
        if any(word in filename_lower for word in ["contract", "contrato"]):
            return "contracts"
        elif any(word in filename_lower for word in ["invoice", "factura"]):
            return "invoices"
        elif any(word in filename_lower for word in ["agreement", "acuerdo", "convenio"]):
            return "agreements"
        
        return "default"
    
    async def should_validate(self, document: Document) -> bool:
        """
        Determina si un documento debe ser validado automáticamente
        
        Args:
            document: Documento a evaluar
            
        Returns:
            bool: True si debe validarse
        """
        # Validar solo documentos procesados exitosamente
        if document.status != DocumentStatus.COMPLETED:
            return False
        
        # No re-validar documentos ya validados
        if document.metadata_ and document.metadata_.get("validation_completed"):
            return False
        
        return True


# Instancia singleton del middleware
validation_middleware = ValidationMiddleware()
