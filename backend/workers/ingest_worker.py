"""
Worker de Ingesta
Procesa eventos de documentos nuevos y dispara el pipeline de procesamiento
"""
import asyncio
import json
from typing import Dict
from uuid import UUID

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import async_session_maker
from core.logging_config import logger, audit_logger
from models.database_models import Document, DocumentStatus
from services.ingest_service import ingest_service
from sqlalchemy import select


class IngestWorker:
    """Worker para procesar eventos de ingesta de documentos"""
    
    def __init__(self):
        self.consumer = None
        self.producer = None
        self.topic_ingest = "document.ingested"
        self.topic_transform = "document.to_transform"
        self.running = False
    
    async def start(self):
        """Inicia el worker"""
        logger.info("Starting Ingest Worker...")
        
        # Inicializar consumer
        self.consumer = AIOKafkaConsumer(
            self.topic_ingest,
            bootstrap_servers=f"{settings.KAFKA_BOOTSTRAP_SERVERS}",
            group_id="ingest-worker-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        
        # Inicializar producer
        self.producer = AIOKafkaProducer(
            bootstrap_servers=f"{settings.KAFKA_BOOTSTRAP_SERVERS}",
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        await self.consumer.start()
        await self.producer.start()
        
        self.running = True
        logger.info("Ingest Worker started successfully")
        
        try:
            await self._consume_messages()
        finally:
            await self.stop()
    
    async def stop(self):
        """Detiene el worker"""
        logger.info("Stopping Ingest Worker...")
        self.running = False
        
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        
        logger.info("Ingest Worker stopped")
    
    async def _consume_messages(self):
        """Consume mensajes del topic"""
        async for message in self.consumer:
            try:
                event = message.value
                logger.info(f"Processing ingest event: {event}")
                
                await self._process_ingest_event(event)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    
    async def _process_ingest_event(self, event: Dict):
        """
        Procesa un evento de ingesta
        
        Args:
            event: Evento con document_id y metadata
        """
        document_id = UUID(event["document_id"])
        
        async with async_session_maker() as db:
            try:
                # Obtener documento
                result = await db.execute(
                    select(Document).where(Document.id == document_id)
                )
                document = result.scalar_one_or_none()
                
                if not document:
                    logger.error(f"Document {document_id} not found")
                    return
                
                # Verificar que el documento esté en estado PENDING
                if document.status != DocumentStatus.PENDING:
                    logger.warning(f"Document {document_id} is not in PENDING state: {document.status}")
                    return
                
                # Obtener contenido del documento desde MinIO
                content = await ingest_service.get_document_content(document)
                
                # Actualizar estado a PROCESSING
                document.status = DocumentStatus.PROCESSING
                await db.commit()
                
                logger.info(f"Document {document_id} status updated to PROCESSING")
                
                # Enviar evento al siguiente stage (transformación)
                transform_event = {
                    "document_id": str(document_id),
                    "filename": document.filename,
                    "mime_type": document.mime_type,
                    "file_size": document.file_size,
                    "uploaded_by": str(document.uploaded_by)
                }
                
                await self.producer.send(self.topic_transform, value=transform_event)
                
                logger.info(f"Sent transform event for document {document_id}")
                
                # Log de auditoría
                audit_logger.info(
                    "Document ingestion processed",
                    extra={
                        "action": "ingest_processed",
                        "document_id": str(document_id),
                        "filename": document.filename
                    }
                )
                
            except Exception as e:
                logger.error(f"Error processing ingest event for {document_id}: {e}", exc_info=True)
                
                # Marcar documento como fallido
                if 'document' in locals() and document:
                    document.status = DocumentStatus.FAILED
                    document.metadata_["error"] = str(e)
                    await db.commit()


async def main():
    """Función principal"""
    worker = IngestWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
