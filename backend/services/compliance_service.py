"""
Servicio de Cumplimiento Normativo
Verifica cumplimiento GDPR/LOPDGDD, gestiona DSR y auditorías
"""
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from core.logging_config import logger, audit_logger
from core.config import settings
from models.database_models import (
    Document, ComplianceCheck, DataSubjectRequest, AuditLog,
    DSRType, DSRStatus, Entity
)
from models.schemas import ComplianceResult, DSRCreate


class ComplianceRule(str, Enum):
    """Reglas de cumplimiento"""
    GDPR_CONSENT = "gdpr_consent"
    GDPR_DATA_MINIMIZATION = "gdpr_data_minimization"
    GDPR_RETENTION = "gdpr_retention"
    GDPR_SECURITY = "gdpr_security"
    GDPR_ACCOUNTABILITY = "gdpr_accountability"
    NIS2_INCIDENT_REPORTING = "nis2_incident_reporting"
    NIS2_SECURITY_MEASURES = "nis2_security_measures"
    EU_AI_ACT_TRANSPARENCY = "eu_ai_act_transparency"
    EU_AI_ACT_RISK_MANAGEMENT = "eu_ai_act_risk_management"


class ComplianceService:
    """Servicio para verificación de cumplimiento normativo"""
    
    def __init__(self):
        # Configuración de retención de datos (días)
        self.retention_periods = {
            "LEGAL": 3650,      # 10 años
            "FINANCIAL": 2555,  # 7 años (fiscal)
            "HR": 1825,         # 5 años
            "TECHNICAL": 1095,  # 3 años
            "MARKETING": 730,   # 2 años
            "OPERATIONS": 1095, # 3 años
            "COMPLIANCE": 3650, # 10 años
            "SENSITIVE": 1095,  # 3 años (salvo requisito legal)
            "UNCLASSIFIED": 730 # 2 años (por defecto)
        }
        
        # Plazos DSR (días)
        self.dsr_response_deadline = 30  # GDPR: 1 mes
        self.dsr_extension_max = 60      # Extensión máxima: 2 meses adicionales
    
    async def run_compliance_checks(
        self,
        document: Document,
        db: AsyncSession
    ) -> ComplianceResult:
        """
        Ejecuta verificaciones de cumplimiento en un documento
        
        Args:
            document: Documento a verificar
            db: Sesión de base de datos
            
        Returns:
            ComplianceResult: Resultado de las verificaciones
        """
        try:
            checks = []
            issues = []
            warnings = []
            
            # 1. Verificar consentimiento para datos personales
            consent_check = await self._check_consent(document, db)
            checks.append(consent_check)
            if not consent_check["passed"]:
                issues.append(consent_check["message"])
            
            # 2. Verificar minimización de datos
            minimization_check = await self._check_data_minimization(document, db)
            checks.append(minimization_check)
            if not minimization_check["passed"]:
                warnings.append(minimization_check["message"])
            
            # 3. Verificar período de retención
            retention_check = self._check_retention_period(document)
            checks.append(retention_check)
            if not retention_check["passed"]:
                issues.append(retention_check["message"])
            
            # 4. Verificar medidas de seguridad
            security_check = self._check_security_measures(document)
            checks.append(security_check)
            if not security_check["passed"]:
                issues.append(security_check["message"])
            
            # 5. Verificar accountability (trazabilidad)
            accountability_check = await self._check_accountability(document, db)
            checks.append(accountability_check)
            if not accountability_check["passed"]:
                warnings.append(accountability_check["message"])
            
            # 6. Verificar transparencia (EU AI Act)
            if document.metadata_.get("ai_processed"):
                transparency_check = self._check_ai_transparency(document)
                checks.append(transparency_check)
                if not transparency_check["passed"]:
                    issues.append(transparency_check["message"])
            
            # Determinar estado global
            is_compliant = len(issues) == 0
            compliance_score = sum(1 for c in checks if c["passed"]) / len(checks)
            
            # Crear registro de compliance
            compliance_check = ComplianceCheck(
                document_id=document.id,
                check_type="full_compliance_audit",
                is_compliant=is_compliant,
                compliance_score=compliance_score,
                findings={
                    "checks": checks,
                    "issues": issues,
                    "warnings": warnings
                }
            )
            
            db.add(compliance_check)
            await db.commit()
            await db.refresh(compliance_check)
            
            # Log de auditoría
            audit_logger.info(
                "Compliance check executed",
                extra={
                    "action": "compliance_check",
                    "document_id": str(document.id),
                    "is_compliant": is_compliant,
                    "compliance_score": compliance_score,
                    "issues_count": len(issues),
                    "warnings_count": len(warnings)
                }
            )
            
            logger.info(
                f"Compliance check for document {document.id}: "
                f"compliant={is_compliant}, score={compliance_score:.2f}"
            )
            
            return ComplianceResult(
                document_id=document.id,
                is_compliant=is_compliant,
                compliance_score=compliance_score,
                checks=checks,
                issues=issues,
                warnings=warnings,
                checked_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error running compliance checks: {e}", exc_info=True)
            raise
    
    async def _check_consent(self, document: Document, db: AsyncSession) -> Dict:
        """Verifica consentimiento para tratamiento de datos personales"""
        # Verificar si el documento contiene datos personales
        result = await db.execute(
            select(Entity).where(
                and_(
                    Entity.document_id == document.id,
                    Entity.entity_type.in_(["PER", "EMAIL", "PHONE"])
                )
            )
        )
        personal_data_entities = result.scalars().all()
        
        if not personal_data_entities:
            return {
                "rule": ComplianceRule.GDPR_CONSENT,
                "passed": True,
                "message": "No personal data detected"
            }
        
        # Verificar base legal en metadata
        legal_basis = document.metadata_.get("legal_basis")
        if not legal_basis:
            return {
                "rule": ComplianceRule.GDPR_CONSENT,
                "passed": False,
                "message": f"Document contains personal data ({len(personal_data_entities)} entities) but lacks legal basis",
                "severity": "HIGH"
            }
        
        # Validar tipos de base legal aceptables
        valid_bases = ["consent", "contract", "legal_obligation", "legitimate_interest", "public_interest", "vital_interest"]
        if legal_basis not in valid_bases:
            return {
                "rule": ComplianceRule.GDPR_CONSENT,
                "passed": False,
                "message": f"Invalid legal basis: {legal_basis}",
                "severity": "HIGH"
            }
        
        return {
            "rule": ComplianceRule.GDPR_CONSENT,
            "passed": True,
            "message": f"Legal basis present: {legal_basis}",
            "entities_count": len(personal_data_entities)
        }
    
    async def _check_data_minimization(self, document: Document, db: AsyncSession) -> Dict:
        """Verifica principio de minimización de datos"""
        # Verificar si hay demasiadas entidades personales
        result = await db.execute(
            select(func.count(Entity.id)).where(Entity.document_id == document.id)
        )
        entity_count = result.scalar()
        
        # Umbral arbitrario: más de 100 entidades puede indicar exceso
        if entity_count > 100:
            return {
                "rule": ComplianceRule.GDPR_DATA_MINIMIZATION,
                "passed": False,
                "message": f"High number of extracted entities ({entity_count}). Review data necessity.",
                "severity": "MEDIUM"
            }
        
        return {
            "rule": ComplianceRule.GDPR_DATA_MINIMIZATION,
            "passed": True,
            "message": "Data collection appears proportionate"
        }
    
    def _check_retention_period(self, document: Document) -> Dict:
        """Verifica cumplimiento del período de retención"""
        classification = document.classification.value
        retention_days = self.retention_periods.get(classification, 730)
        
        document_age = (datetime.utcnow() - document.uploaded_at).days
        
        if document_age > retention_days:
            return {
                "rule": ComplianceRule.GDPR_RETENTION,
                "passed": False,
                "message": f"Document exceeds retention period ({document_age}/{retention_days} days)",
                "severity": "HIGH",
                "action_required": "Review for deletion or justify extended retention"
            }
        
        # Advertencia si está cerca del límite (90%)
        if document_age > retention_days * 0.9:
            return {
                "rule": ComplianceRule.GDPR_RETENTION,
                "passed": True,
                "message": f"Document approaching retention limit ({document_age}/{retention_days} days)",
                "severity": "LOW",
                "action_required": "Schedule retention review"
            }
        
        return {
            "rule": ComplianceRule.GDPR_RETENTION,
            "passed": True,
            "message": f"Within retention period ({document_age}/{retention_days} days)"
        }
    
    def _check_security_measures(self, document: Document) -> Dict:
        """Verifica medidas de seguridad aplicadas"""
        security_measures = document.metadata_.get("security_measures", {})
        
        required_measures = ["encryption_at_rest", "access_control", "audit_logging"]
        missing_measures = [m for m in required_measures if not security_measures.get(m)]
        
        if missing_measures:
            return {
                "rule": ComplianceRule.GDPR_SECURITY,
                "passed": False,
                "message": f"Missing security measures: {', '.join(missing_measures)}",
                "severity": "HIGH"
            }
        
        return {
            "rule": ComplianceRule.GDPR_SECURITY,
            "passed": True,
            "message": "All required security measures in place"
        }
    
    async def _check_accountability(self, document: Document, db: AsyncSession) -> Dict:
        """Verifica trazabilidad y accountability"""
        # Verificar que existan registros de auditoría
        result = await db.execute(
            select(func.count(AuditLog.id)).where(
                AuditLog.metadata_["document_id"].astext == str(document.id)
            )
        )
        audit_count = result.scalar()
        
        if audit_count == 0:
            return {
                "rule": ComplianceRule.GDPR_ACCOUNTABILITY,
                "passed": False,
                "message": "No audit trail found for document",
                "severity": "MEDIUM"
            }
        
        return {
            "rule": ComplianceRule.GDPR_ACCOUNTABILITY,
            "passed": True,
            "message": f"Audit trail present ({audit_count} entries)"
        }
    
    def _check_ai_transparency(self, document: Document) -> Dict:
        """Verifica transparencia en procesamiento con IA (EU AI Act)"""
        ai_metadata = document.metadata_.get("ai_metadata", {})
        
        required_fields = ["model_name", "model_version", "processing_purpose", "explainability_available"]
        missing_fields = [f for f in required_fields if f not in ai_metadata]
        
        if missing_fields:
            return {
                "rule": ComplianceRule.EU_AI_ACT_TRANSPARENCY,
                "passed": False,
                "message": f"Missing AI transparency information: {', '.join(missing_fields)}",
                "severity": "HIGH"
            }
        
        return {
            "rule": ComplianceRule.EU_AI_ACT_TRANSPARENCY,
            "passed": True,
            "message": "AI processing transparency requirements met"
        }
    
    async def create_dsr(
        self,
        dsr_data: DSRCreate,
        db: AsyncSession
    ) -> DataSubjectRequest:
        """
        Crea una solicitud de derecho de interesado (DSR)
        
        Args:
            dsr_data: Datos de la solicitud
            db: Sesión de base de datos
            
        Returns:
            DataSubjectRequest: Solicitud creada
        """
        try:
            # Calcular deadline
            deadline = datetime.utcnow() + timedelta(days=self.dsr_response_deadline)
            
            dsr = DataSubjectRequest(
                request_type=dsr_data.request_type,
                subject_email=dsr_data.subject_email,
                subject_details=dsr_data.subject_details,
                status=DSRStatus.PENDING,
                deadline=deadline
            )
            
            db.add(dsr)
            await db.commit()
            await db.refresh(dsr)
            
            # Log de auditoría
            audit_logger.info(
                "DSR created",
                extra={
                    "action": "dsr_create",
                    "dsr_id": str(dsr.id),
                    "request_type": dsr_data.request_type.value,
                    "subject_email": dsr_data.subject_email,
                    "deadline": deadline.isoformat()
                }
            )
            
            logger.info(f"DSR created: {dsr.id}, type={dsr_data.request_type}, deadline={deadline}")
            
            return dsr
            
        except Exception as e:
            logger.error(f"Error creating DSR: {e}", exc_info=True)
            raise
    
    async def process_dsr(
        self,
        dsr_id: UUID,
        db: AsyncSession
    ) -> Dict:
        """
        Procesa una solicitud DSR
        
        Args:
            dsr_id: ID de la solicitud
            db: Sesión de base de datos
            
        Returns:
            Dict: Resultado del procesamiento
        """
        try:
            # Obtener DSR
            result = await db.execute(
                select(DataSubjectRequest).where(DataSubjectRequest.id == dsr_id)
            )
            dsr = result.scalar_one_or_none()
            
            if not dsr:
                raise ValueError(f"DSR {dsr_id} not found")
            
            # Buscar documentos relacionados con el interesado
            email = dsr.subject_email
            result = await db.execute(
                select(Document).join(Entity).where(
                    and_(
                        Entity.entity_type == "EMAIL",
                        Entity.entity_value == email
                    )
                )
            )
            related_documents = result.scalars().all()
            
            response_data = {}
            
            # Procesar según tipo de solicitud
            if dsr.request_type == DSRType.ACCESS:
                # Derecho de acceso: listar documentos
                response_data = {
                    "documents": [
                        {
                            "id": str(doc.id),
                            "filename": doc.filename,
                            "uploaded_at": doc.uploaded_at.isoformat(),
                            "classification": doc.classification.value
                        }
                        for doc in related_documents
                    ],
                    "total_documents": len(related_documents)
                }
            
            elif dsr.request_type == DSRType.RECTIFICATION:
                # Derecho de rectificación: identificar documentos a corregir
                response_data = {
                    "documents_to_rectify": [str(doc.id) for doc in related_documents],
                    "action_required": "Manual rectification needed"
                }
            
            elif dsr.request_type == DSRType.ERASURE:
                # Derecho al olvido: marcar documentos para eliminación
                for doc in related_documents:
                    doc.deleted_at = datetime.utcnow()
                    doc.metadata_["deletion_reason"] = f"DSR {dsr_id} - Right to erasure"
                
                response_data = {
                    "documents_deleted": len(related_documents),
                    "deleted_ids": [str(doc.id) for doc in related_documents]
                }
            
            elif dsr.request_type == DSRType.PORTABILITY:
                # Derecho a la portabilidad: preparar exportación
                response_data = {
                    "export_ready": True,
                    "documents_count": len(related_documents),
                    "format": "JSON",
                    "download_link": f"/api/v1/compliance/dsr/{dsr_id}/export"
                }
            
            elif dsr.request_type == DSRType.OBJECTION:
                # Derecho de oposición: detener procesamiento
                for doc in related_documents:
                    doc.metadata_["processing_objection"] = True
                    doc.metadata_["objection_date"] = datetime.utcnow().isoformat()
                
                response_data = {
                    "processing_stopped": len(related_documents),
                    "affected_documents": [str(doc.id) for doc in related_documents]
                }
            
            elif dsr.request_type == DSRType.RESTRICT:
                # Derecho de limitación: restringir procesamiento
                for doc in related_documents:
                    doc.metadata_["processing_restricted"] = True
                    doc.metadata_["restriction_date"] = datetime.utcnow().isoformat()
                
                response_data = {
                    "documents_restricted": len(related_documents),
                    "restricted_ids": [str(doc.id) for doc in related_documents]
                }
            
            # Actualizar DSR
            dsr.status = DSRStatus.COMPLETED
            dsr.completed_at = datetime.utcnow()
            dsr.response_data = response_data
            
            await db.commit()
            
            # Log de auditoría
            audit_logger.info(
                "DSR processed",
                extra={
                    "action": "dsr_process",
                    "dsr_id": str(dsr_id),
                    "request_type": dsr.request_type.value,
                    "affected_documents": len(related_documents),
                    "response_data": response_data
                }
            )
            
            logger.info(f"DSR {dsr_id} processed successfully")
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing DSR {dsr_id}: {e}", exc_info=True)
            # Marcar DSR como fallido
            if 'dsr' in locals():
                dsr.status = DSRStatus.REJECTED
                dsr.response_data = {"error": str(e)}
                await db.commit()
            raise
    
    async def get_audit_report(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_filter: Optional[str] = None
    ) -> Dict:
        """
        Genera reporte de auditoría
        
        Args:
            db: Sesión de base de datos
            start_date: Fecha inicio
            end_date: Fecha fin
            action_filter: Filtro por tipo de acción
            
        Returns:
            Dict: Reporte de auditoría
        """
        try:
            query = select(AuditLog)
            
            if start_date:
                query = query.where(AuditLog.created_at >= start_date)
            if end_date:
                query = query.where(AuditLog.created_at <= end_date)
            if action_filter:
                query = query.where(AuditLog.action == action_filter)
            
            query = query.order_by(AuditLog.created_at.desc())
            
            result = await db.execute(query)
            logs = result.scalars().all()
            
            # Agregaciones
            action_counts = {}
            user_actions = {}
            
            for log in logs:
                action = log.action
                user = log.user_id or "system"
                
                action_counts[action] = action_counts.get(action, 0) + 1
                user_actions[user] = user_actions.get(user, 0) + 1
            
            return {
                "total_events": len(logs),
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "by_action": action_counts,
                "by_user": user_actions,
                "events": [
                    {
                        "id": str(log.id),
                        "action": log.action,
                        "user_id": str(log.user_id) if log.user_id else None,
                        "timestamp": log.created_at.isoformat(),
                        "metadata": log.metadata_
                    }
                    for log in logs[:100]  # Limitar a 100 eventos más recientes
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating audit report: {e}", exc_info=True)
            raise


# Instancia singleton del servicio
compliance_service = ComplianceService()
