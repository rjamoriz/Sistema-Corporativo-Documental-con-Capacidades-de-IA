"""
Scheduler para tareas de validación automáticas.

Tareas:
- Sincronización diaria de listas de sanciones (2 AM)
- Resumen diario de validaciones (8 AM)
- Limpieza de cache antiguo (3 AM)
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import asyncio
from typing import Optional

from backend.services.validation import SanctionsService
from backend.services.notifications import NotificationService
from backend.database import get_db


logger = logging.getLogger(__name__)


class ValidationScheduler:
    """Scheduler para tareas de validación."""

    def __init__(self):
        """Inicializa el scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        """Inicia el scheduler con todas las tareas configuradas."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        # Tarea 1: Sincronizar listas de sanciones (diario 2 AM)
        self.scheduler.add_job(
            self.sync_sanctions_lists,
            trigger=CronTrigger(hour=2, minute=0),
            id="sync_sanctions_lists",
            name="Sincronizar listas de sanciones",
            replace_existing=True,
        )

        # Tarea 2: Enviar resumen diario (diario 8 AM)
        self.scheduler.add_job(
            self.send_daily_summary,
            trigger=CronTrigger(hour=8, minute=0),
            id="send_daily_summary",
            name="Enviar resumen diario",
            replace_existing=True,
        )

        # Tarea 3: Limpiar cache antiguo (diario 3 AM)
        self.scheduler.add_job(
            self.cleanup_old_cache,
            trigger=CronTrigger(hour=3, minute=0),
            id="cleanup_old_cache",
            name="Limpiar cache antiguo",
            replace_existing=True,
        )

        # Tarea 4: Validar documentos pendientes (cada 30 min)
        self.scheduler.add_job(
            self.validate_pending_documents,
            trigger=CronTrigger(minute="*/30"),
            id="validate_pending_documents",
            name="Validar documentos pendientes",
            replace_existing=True,
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("Validation scheduler started successfully")

    def stop(self):
        """Detiene el scheduler."""
        if not self.is_running:
            logger.warning("Scheduler not running")
            return

        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("Validation scheduler stopped")

    async def sync_sanctions_lists(self):
        """
        Sincroniza listas de sanciones desde APIs oficiales.
        
        Actualiza cache local con datos más recientes de:
        - OFAC Sanctions List
        - EU Sanctions Database
        - World Bank Debarred Firms
        """
        logger.info("Starting sanctions lists synchronization...")
        
        try:
            from backend.models.validation import SanctionsList
            from sqlalchemy.orm import Session
            
            db: Session = next(get_db())
            
            # Contadores
            stats = {
                "ofac": 0,
                "eu": 0,
                "world_bank": 0,
                "errors": [],
            }

            # Sincronizar OFAC
            try:
                ofac_count = await self._sync_ofac_list(db)
                stats["ofac"] = ofac_count
                logger.info(f"OFAC: {ofac_count} entradas actualizadas")
            except Exception as e:
                logger.error(f"Error syncing OFAC: {e}")
                stats["errors"].append(f"OFAC: {str(e)}")

            # Sincronizar EU Sanctions
            try:
                eu_count = await self._sync_eu_sanctions_list(db)
                stats["eu"] = eu_count
                logger.info(f"EU Sanctions: {eu_count} entradas actualizadas")
            except Exception as e:
                logger.error(f"Error syncing EU Sanctions: {e}")
                stats["errors"].append(f"EU Sanctions: {str(e)}")

            # Sincronizar World Bank
            try:
                wb_count = await self._sync_world_bank_list(db)
                stats["world_bank"] = wb_count
                logger.info(f"World Bank: {wb_count} entradas actualizadas")
            except Exception as e:
                logger.error(f"Error syncing World Bank: {e}")
                stats["errors"].append(f"World Bank: {str(e)}")

            # Log final
            total = stats["ofac"] + stats["eu"] + stats["world_bank"]
            logger.info(
                f"Sanctions lists sync completed: {total} total entries, "
                f"{len(stats['errors'])} errors"
            )

            # Notificar si hay errores
            if stats["errors"]:
                await self._notify_sync_errors(stats)

        except Exception as e:
            logger.error(f"Critical error in sanctions sync: {e}")
            raise

    async def _sync_ofac_list(self, db) -> int:
        """Sincroniza lista OFAC."""
        import aiohttp
        from config.validation_apis import SANCTIONS_CONFIG
        from backend.models.validation import SanctionsList
        
        url = SANCTIONS_CONFIG["ofac"]["api_url"]
        api_key = SANCTIONS_CONFIG["ofac"]["api_key"]
        
        async with aiohttp.ClientSession() as session:
            # Obtener lista completa
            async with session.get(
                f"{url}/export",
                params={"api_key": api_key, "format": "json"},
                timeout=60
            ) as response:
                if response.status != 200:
                    raise Exception(f"OFAC API error: {response.status}")
                
                data = await response.json()
                entries = data.get("results", [])
                
                # Actualizar/insertar en BD
                count = 0
                for entry in entries:
                    # Buscar existente
                    existing = db.query(SanctionsList).filter(
                        SanctionsList.source == "OFAC",
                        SanctionsList.list_id == entry["id"]
                    ).first()
                    
                    if existing:
                        # Actualizar
                        existing.entity_name = entry["name"]
                        existing.entity_type = entry.get("type")
                        existing.program = entry.get("programs", [])
                        existing.addresses = entry.get("addresses", [])
                        existing.remarks = entry.get("remarks")
                        existing.raw_data = entry
                        existing.last_updated = datetime.utcnow()
                    else:
                        # Insertar nuevo
                        new_entry = SanctionsList(
                            source="OFAC",
                            entity_name=entry["name"],
                            entity_type=entry.get("type"),
                            list_id=entry["id"],
                            country=entry.get("country"),
                            program=", ".join(entry.get("programs", [])),
                            addresses=entry.get("addresses", []),
                            remarks=entry.get("remarks"),
                            raw_data=entry,
                            last_updated=datetime.utcnow(),
                        )
                        db.add(new_entry)
                    
                    count += 1
                
                db.commit()
                return count

    async def _sync_eu_sanctions_list(self, db) -> int:
        """Sincroniza lista EU Sanctions."""
        # Similar a OFAC
        # Implementación simplificada
        return 0  # Mock

    async def _sync_world_bank_list(self, db) -> int:
        """Sincroniza lista World Bank."""
        # Similar a OFAC
        # Implementación simplificada
        return 0  # Mock

    async def send_daily_summary(self):
        """
        Envía resumen diario de validaciones.
        
        Incluye:
        - Total de validaciones últimas 24h
        - Entidades flagged
        - Top 5 documentos con más alertas
        - Tendencias
        """
        logger.info("Generating daily summary...")
        
        try:
            db: Session = next(get_db())
            
            # Calcular stats últimas 24h
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            from backend.models.validation import ValidationResult, ValidationHistory
            from sqlalchemy import func
            
            # Total validaciones
            total_validations = db.query(func.count(ValidationResult.id)).filter(
                ValidationResult.checked_at >= yesterday
            ).scalar()
            
            # Entidades flagged
            entities_flagged = db.query(func.count(ValidationResult.id)).filter(
                ValidationResult.checked_at >= yesterday,
                ValidationResult.is_sanctioned == True
            ).scalar()
            
            # Documentos procesados
            documents_processed = db.query(func.count(ValidationHistory.id)).filter(
                ValidationHistory.validated_at >= yesterday
            ).scalar()
            
            # Calcular porcentaje
            flagged_percentage = (
                (entities_flagged / total_validations * 100) if total_validations > 0 else 0
            )
            
            stats = {
                "total_validations": total_validations,
                "entities_flagged": entities_flagged,
                "flagged_percentage": flagged_percentage,
                "documents_processed": documents_processed,
            }
            
            # Enviar resumen por email
            async with NotificationService() as notif_service:
                await notif_service.send_daily_summary(stats, period="24h")
            
            logger.info(f"Daily summary sent: {total_validations} validations, {entities_flagged} flagged")
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            raise

    async def cleanup_old_cache(self):
        """
        Limpia entradas antiguas del cache.
        
        - Elimina validaciones > 90 días
        - Mantiene solo las más recientes por entidad
        """
        logger.info("Cleaning up old cache...")
        
        try:
            db: Session = next(get_db())
            
            # Fecha límite: 90 días atrás
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            from backend.models.validation import ValidationResult
            
            # Eliminar resultados antiguos
            deleted = db.query(ValidationResult).filter(
                ValidationResult.checked_at < cutoff_date
            ).delete()
            
            db.commit()
            
            logger.info(f"Cleanup completed: {deleted} old records removed")
            
        except Exception as e:
            logger.error(f"Error cleaning cache: {e}")
            raise

    async def validate_pending_documents(self):
        """
        Valida documentos que están pendientes de validación.
        
        Busca documentos ingresados pero sin validar y ejecuta
        validación automática.
        """
        logger.info("Validating pending documents...")
        
        try:
            db: Session = next(get_db())
            
            # Buscar documentos sin validar (últimas 24h)
            from backend.models.document import Document
            from backend.models.validation import ValidationHistory
            from sqlalchemy import and_
            
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            # Documentos sin validación
            pending_docs = db.query(Document).filter(
                and_(
                    Document.created_at >= yesterday,
                    ~Document.id.in_(
                        db.query(ValidationHistory.document_id)
                    )
                )
            ).limit(10).all()  # Procesar máx 10 por ejecución
            
            if not pending_docs:
                logger.info("No pending documents to validate")
                return
            
            # Validar cada documento
            async with SanctionsService(db) as sanctions_service:
                for doc in pending_docs:
                    try:
                        result = await sanctions_service.validate_document_entities(doc.id)
                        logger.info(
                            f"Document {doc.id} validated: "
                            f"{result['flagged_entities']}/{result['total_entities']} flagged"
                        )
                        
                        # Si hay entidades flagged, enviar alerta
                        if result['flagged_entities'] > 0:
                            # Enviar notificación
                            pass
                            
                    except Exception as e:
                        logger.error(f"Error validating document {doc.id}: {e}")
            
            logger.info(f"Validated {len(pending_docs)} pending documents")
            
        except Exception as e:
            logger.error(f"Error in pending documents validation: {e}")
            raise

    async def _notify_sync_errors(self, stats: dict):
        """Notifica errores de sincronización al equipo."""
        logger.warning(f"Sync errors detected: {stats['errors']}")
        # Implementar notificación
        pass


# Instancia global del scheduler
validation_scheduler = ValidationScheduler()


def start_scheduler():
    """Inicia el scheduler global."""
    validation_scheduler.start()


def stop_scheduler():
    """Detiene el scheduler global."""
    validation_scheduler.stop()
