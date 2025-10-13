"""
Servicio de Evaluación de Riesgos
Análisis multidimensional de riesgos con 6 dimensiones
"""
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.logging_config import logger, audit_logger
from core.config import settings
from models.database_models import Document, RiskAssessment, Entity
from models.schemas import RiskScore, RiskDimension


class RiskService:
    """Servicio para evaluación de riesgos en documentos"""
    
    def __init__(self):
        # Pesos de las dimensiones (deben sumar 1.0)
        self.dimension_weights = {
            "legal": settings.RISK_WEIGHT_LEGAL,           # 0.25
            "financial": settings.RISK_WEIGHT_FINANCIAL,   # 0.30
            "operational": settings.RISK_WEIGHT_OPERATIONAL, # 0.20
            "esg": settings.RISK_WEIGHT_ESG,               # 0.10
            "privacy": settings.RISK_WEIGHT_PRIVACY,       # 0.10
            "cybersecurity": settings.RISK_WEIGHT_CYBER    # 0.05
        }
        
        # Umbrales de riesgo
        self.threshold_low = 0.3
        self.threshold_medium = 0.6
        self.threshold_high = 0.8
        
        # Patrones de riesgo por dimensión
        self._init_risk_patterns()
    
    def _init_risk_patterns(self):
        """Inicializa patrones de detección de riesgo"""
        
        # LEGAL
        self.legal_patterns = {
            "litigation": [
                r"demanda", r"litigio", r"pleito", r"querella", r"denuncia",
                r"juicio", r"tribunal", r"sentencia", r"indemnización"
            ],
            "contract_breach": [
                r"incumplimiento", r"breach", r"violación", r"infracción",
                r"cláusula[\s\w]+incumplida", r"resolver el contrato"
            ],
            "regulatory": [
                r"sanción", r"multa", r"infracción normativa", r"incumplimiento legal",
                r"regulación[\s\w]+incumplida", r"requisito legal no cumplido"
            ],
            "intellectual_property": [
                r"propiedad intelectual", r"patente[\s\w]+infringida", r"plagio",
                r"derecho de autor", r"copyright", r"marca registrada"
            ]
        }
        
        # FINANCIAL
        self.financial_patterns = {
            "high_amounts": r"(?:€|EUR|USD|\$)\s*[1-9]\d{5,}",  # >100k
            "debt": [
                r"deuda", r"pasivo", r"préstamo", r"crédito", r"aval",
                r"garantía", r"hipoteca", r"insolvencia", r"impago"
            ],
            "fraud": [
                r"fraude", r"malversación", r"desfalco", r"apropiación indebida",
                r"blanqueo", r"evasión fiscal", r"corrupción"
            ],
            "budget_overrun": [
                r"sobrecost[eo]", r"presupuesto excedido", r"déficit",
                r"pérdidas", r"impacto negativo[\s\w]+resultados"
            ]
        }
        
        # OPERATIONAL
        self.operational_patterns = {
            "service_disruption": [
                r"interrupción", r"caída del sistema", r"downtime", r"indisponibilidad",
                r"fallo", r"avería", r"parada", r"suspensión del servicio"
            ],
            "quality_issues": [
                r"defecto", r"no conformidad", r"rechazo", r"deficiencia",
                r"calidad[\s\w]+inferior", r"no cumple[\s\w]+estándares"
            ],
            "supply_chain": [
                r"retraso en[\s\w]+entrega", r"proveedor[\s\w]+incumple",
                r"escasez", r"falta de suministro", r"cadena[\s\w]+suministro[\s\w]+rota"
            ]
        }
        
        # ESG (Environmental, Social, Governance)
        self.esg_patterns = {
            "environmental": [
                r"contaminación", r"emisiones", r"residuos", r"impacto ambiental",
                r"daño ecológico", r"vertido", r"polución"
            ],
            "social": [
                r"accidente laboral", r"discriminación", r"acoso", r"explotación",
                r"condiciones[\s\w]+trabajo[\s\w]+inseguras", r"violación[\s\w]+derechos humanos"
            ],
            "governance": [
                r"conflicto de interés", r"falta de transparencia", r"mala praxis",
                r"gobernanza[\s\w]+deficiente", r"ética[\s\w]+comprometida"
            ]
        }
        
        # PRIVACY (GDPR/LOPDGDD)
        self.privacy_patterns = {
            "data_breach": [
                r"fuga de datos", r"brecha de seguridad", r"datos[\s\w]+expuestos",
                r"acceso no autorizado", r"filtración"
            ],
            "consent_issues": [
                r"sin consentimiento", r"consentimiento[\s\w]+no[\s\w]+obtenido",
                r"base legal[\s\w]+inexistente", r"falta[\s\w]+legitimación"
            ],
            "rights_violation": [
                r"derecho[\s\w]+acceso[\s\w]+denegado", r"rectificación[\s\w]+no[\s\w]+atendida",
                r"supresión[\s\w]+no[\s\w]+efectuada", r"portabilidad[\s\w]+rechazada"
            ],
            "sensitive_data": [
                r"datos sensibles", r"categorías especiales", r"salud", r"ideología",
                r"afiliación sindical", r"orientación sexual", r"origen racial"
            ]
        }
        
        # CYBERSECURITY
        self.cyber_patterns = {
            "attack": [
                r"ciberataque", r"ransomware", r"malware", r"phishing",
                r"ddos", r"intrusión", r"vulnerabilidad explotada"
            ],
            "credential_compromise": [
                r"credenciales[\s\w]+comprometidas", r"contraseñas[\s\w]+robadas",
                r"acceso[\s\w]+no[\s\w]+autorizado", r"cuenta[\s\w]+vulnerada"
            ],
            "infrastructure": [
                r"sistema[\s\w]+comprometido", r"servidor[\s\w]+infectado",
                r"red[\s\w]+insegura", r"firewall[\s\w]+desactivado"
            ]
        }
    
    async def assess_risk(
        self,
        document: Document,
        text: str,
        db: AsyncSession
    ) -> RiskAssessment:
        """
        Evalúa el riesgo multidimensional de un documento
        
        Args:
            document: Documento a evaluar
            text: Texto del documento
            db: Sesión de base de datos
            
        Returns:
            RiskAssessment: Evaluación completa de riesgos
        """
        try:
            # Evaluar cada dimensión
            legal_score, legal_evidence = self._assess_legal_risk(text)
            financial_score, financial_evidence = self._assess_financial_risk(text)
            operational_score, operational_evidence = self._assess_operational_risk(text)
            esg_score, esg_evidence = self._assess_esg_risk(text)
            privacy_score, privacy_evidence = self._assess_privacy_risk(text, db, document.id)
            cyber_score, cyber_evidence = self._assess_cybersecurity_risk(text)
            
            # Calcular score global ponderado
            overall_score = (
                legal_score * self.dimension_weights["legal"] +
                financial_score * self.dimension_weights["financial"] +
                operational_score * self.dimension_weights["operational"] +
                esg_score * self.dimension_weights["esg"] +
                privacy_score * self.dimension_weights["privacy"] +
                cyber_score * self.dimension_weights["cybersecurity"]
            )
            
            # Determinar nivel de riesgo
            risk_level = self._get_risk_level(overall_score)
            
            # Consolidar evidencias
            all_evidence = {
                "legal": legal_evidence,
                "financial": financial_evidence,
                "operational": operational_evidence,
                "esg": esg_evidence,
                "privacy": privacy_evidence,
                "cybersecurity": cyber_evidence
            }
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(all_evidence, overall_score)
            
            # Crear registro en base de datos
            assessment = RiskAssessment(
                document_id=document.id,
                overall_risk_score=overall_score,
                legal_risk=legal_score,
                financial_risk=financial_score,
                operational_risk=operational_score,
                esg_risk=esg_score,
                privacy_risk=privacy_score,
                cybersecurity_risk=cyber_score,
                risk_level=risk_level,
                evidence=all_evidence,
                recommendations=recommendations
            )
            
            db.add(assessment)
            await db.commit()
            await db.refresh(assessment)
            
            # Log de auditoría
            audit_logger.info(
                "Risk assessment completed",
                extra={
                    "action": "risk_assessment",
                    "document_id": str(document.id),
                    "overall_score": overall_score,
                    "risk_level": risk_level,
                    "dimensions": {
                        "legal": legal_score,
                        "financial": financial_score,
                        "operational": operational_score,
                        "esg": esg_score,
                        "privacy": privacy_score,
                        "cybersecurity": cyber_score
                    }
                }
            )
            
            logger.info(
                f"Risk assessment for document {document.id}: "
                f"overall={overall_score:.2f}, level={risk_level}"
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing risk for document {document.id}: {e}", exc_info=True)
            raise
    
    def _assess_legal_risk(self, text: str) -> tuple[float, List[str]]:
        """Evalúa riesgo legal"""
        score = 0.0
        evidence = []
        text_lower = text.lower()
        
        for category, patterns in self.legal_patterns.items():
            if isinstance(patterns, list):
                for pattern in patterns:
                    matches = re.findall(pattern, text_lower)
                    if matches:
                        score += 0.2
                        evidence.append(f"{category}: {', '.join(set(matches[:3]))}")
        
        return min(1.0, score), evidence
    
    def _assess_financial_risk(self, text: str) -> tuple[float, List[str]]:
        """Evalúa riesgo financiero"""
        score = 0.0
        evidence = []
        text_lower = text.lower()
        
        # Detectar montos altos
        high_amounts = re.findall(self.financial_patterns["high_amounts"], text)
        if high_amounts:
            score += 0.3
            evidence.append(f"Montos elevados detectados: {', '.join(high_amounts[:3])}")
        
        # Otros patrones financieros
        for category, patterns in self.financial_patterns.items():
            if category == "high_amounts":
                continue
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += 0.25
                    evidence.append(f"{category}: {', '.join(set(matches[:3]))}")
        
        return min(1.0, score), evidence
    
    def _assess_operational_risk(self, text: str) -> tuple[float, List[str]]:
        """Evalúa riesgo operacional"""
        score = 0.0
        evidence = []
        text_lower = text.lower()
        
        for category, patterns in self.operational_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += 0.25
                    evidence.append(f"{category}: {', '.join(set(matches[:3]))}")
        
        return min(1.0, score), evidence
    
    def _assess_esg_risk(self, text: str) -> tuple[float, List[str]]:
        """Evalúa riesgo ESG"""
        score = 0.0
        evidence = []
        text_lower = text.lower()
        
        for category, patterns in self.esg_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += 0.3
                    evidence.append(f"{category}: {', '.join(set(matches[:3]))}")
        
        return min(1.0, score), evidence
    
    async def _assess_privacy_risk(self, text: str, db: AsyncSession, document_id: UUID) -> tuple[float, List[str]]:
        """Evalúa riesgo de privacidad (GDPR)"""
        score = 0.0
        evidence = []
        text_lower = text.lower()
        
        # Detectar patrones de privacidad
        for category, patterns in self.privacy_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += 0.3
                    evidence.append(f"{category}: {', '.join(set(matches[:3]))}")
        
        # Verificar entidades de tipo PER (personas)
        result = await db.execute(
            select(Entity).where(
                Entity.document_id == document_id,
                Entity.entity_type == "PER"
            )
        )
        persons = result.scalars().all()
        if len(persons) > 5:
            score += 0.2
            evidence.append(f"Alto número de personas identificadas: {len(persons)}")
        
        return min(1.0, score), evidence
    
    def _assess_cybersecurity_risk(self, text: str) -> tuple[float, List[str]]:
        """Evalúa riesgo de ciberseguridad"""
        score = 0.0
        evidence = []
        text_lower = text.lower()
        
        for category, patterns in self.cyber_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += 0.35
                    evidence.append(f"{category}: {', '.join(set(matches[:3]))}")
        
        return min(1.0, score), evidence
    
    def _get_risk_level(self, score: float) -> str:
        """Determina el nivel de riesgo"""
        if score < self.threshold_low:
            return "LOW"
        elif score < self.threshold_medium:
            return "MEDIUM"
        elif score < self.threshold_high:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_recommendations(self, evidence: Dict, overall_score: float) -> List[str]:
        """Genera recomendaciones basadas en la evaluación"""
        recommendations = []
        
        # Recomendaciones generales según nivel
        if overall_score >= self.threshold_high:
            recommendations.append("🔴 CRÍTICO: Requiere revisión inmediata por equipo legal y DPO")
            recommendations.append("Suspender cualquier acción hasta evaluación completa")
        elif overall_score >= self.threshold_medium:
            recommendations.append("🟠 ALTO: Revisión obligatoria antes de proceder")
        
        # Recomendaciones específicas por dimensión
        if evidence["legal"]:
            recommendations.append("⚖️ Legal: Consultar con departamento jurídico")
        
        if evidence["financial"]:
            recommendations.append("💰 Financiero: Validar con departamento financiero y auditoría")
        
        if evidence["privacy"]:
            recommendations.append("🔒 Privacidad: Evaluación DPIA requerida - contactar DPO")
            recommendations.append("Verificar bases legales de tratamiento de datos personales")
        
        if evidence["cybersecurity"]:
            recommendations.append("🛡️ Ciberseguridad: Notificar a equipo de seguridad IT inmediatamente")
        
        if evidence["esg"]:
            recommendations.append("🌍 ESG: Revisar con comité de sostenibilidad")
        
        if evidence["operational"]:
            recommendations.append("⚙️ Operacional: Implementar plan de contingencia")
        
        return recommendations
    
    async def get_risk_dashboard(self, db: AsyncSession, user_id: Optional[UUID] = None) -> Dict:
        """
        Genera dashboard de riesgos agregado
        
        Args:
            db: Sesión de base de datos
            user_id: Filtrar por usuario (opcional)
            
        Returns:
            Dict: Estadísticas de riesgos
        """
        query = select(RiskAssessment)
        if user_id:
            query = query.join(Document).where(Document.uploaded_by == user_id)
        
        result = await db.execute(query)
        assessments = result.scalars().all()
        
        if not assessments:
            return {"total": 0, "by_level": {}, "avg_scores": {}}
        
        # Agregaciones
        risk_levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        dimension_totals = {
            "legal": 0, "financial": 0, "operational": 0,
            "esg": 0, "privacy": 0, "cybersecurity": 0
        }
        
        for assessment in assessments:
            risk_levels[assessment.risk_level] += 1
            dimension_totals["legal"] += assessment.legal_risk
            dimension_totals["financial"] += assessment.financial_risk
            dimension_totals["operational"] += assessment.operational_risk
            dimension_totals["esg"] += assessment.esg_risk
            dimension_totals["privacy"] += assessment.privacy_risk
            dimension_totals["cybersecurity"] += assessment.cybersecurity_risk
        
        count = len(assessments)
        avg_scores = {k: v / count for k, v in dimension_totals.items()}
        
        return {
            "total": count,
            "by_level": risk_levels,
            "avg_scores": avg_scores,
            "overall_avg": sum(a.overall_risk_score for a in assessments) / count
        }


# Instancia singleton del servicio
risk_service = RiskService()
