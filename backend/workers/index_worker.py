"""
Worker de Indexación
Indexa documentos procesados en OpenSearch y actualiza vectores en PostgreSQL
"""
import asyncio
import json
from typing import Dict
from uuid import UUID

from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import async_session_maker
from core.logging_config import logger, audit_logger
from models.database_models import Document, DocumentChunk, DocumentStatus
from services.search_service import search_service
from sqlalchemy import select


class IndexWorker:
    """Worker para indexación de documentos en OpenSearch"""
    
    def __init__(self):
        self.consumer = None
        self.topic_index = "document.to_index"
        self.running = False
    
    async def start(self):
        """Inicia el worker"""
        logger.info("Starting Index Worker...")
        
        # Inicializar consumer
        self.consumer = AIOKafkaConsumer(
            self.topic_index,
            bootstrap_servers=f"{settings.KAFKA_BOOTSTRAP_SERVERS}",
            group_id="index-worker-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        
        await self.consumer.start()
        
        self.running = True
        logger.info("Index Worker started successfully")
        
        try:
            await self._consume_messages()
        finally:
            await self.stop()
    
    async def stop(self):
        """Detiene el worker"""
        logger.info("Stopping Index Worker...")
        self.running = False
        
        if self.consumer:
            await self.consumer.stop()
        
        logger.info("Index Worker stopped")
    
    async def _consume_messages(self):
        """Consume mensajes del topic"""
        async for message in self.consumer:
            try:
                event = message.value
                logger.info(f"Processing index event: {event}")
                
                await self._index_document(event)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    
    async def _index_document(self, event: Dict):
        """
        Indexa un documento en OpenSearch
        
        Args:
            event: Evento con document_id
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
                
                # Verificar que el documento esté procesado
                if document.status != DocumentStatus.PROCESSED:
                    logger.warning(f"Document {document_id} is not in PROCESSED state: {document.status}")
                    return
                
                logger.info(f"Starting indexation for document {document_id}")
                
                # Obtener chunks del documento
                result = await db.execute(
                    select(DocumentChunk)
                    .where(DocumentChunk.document_id == document_id)
                    .order_by(DocumentChunk.chunk_index)
                )
                chunks = result.scalars().all()
                
                if not chunks:
                    logger.warning(f"No chunks found for document {document_id}")
                    return
                
                # Indexar en OpenSearch
                await search_service.index_document(document, chunks)
                
                logger.info(
                    f"Document {document_id} indexed successfully: "
                    f"{len(chunks)} chunks indexed in OpenSearch"
                )
                
                # Actualizar estado del documento
                document.status = DocumentStatus.INDEXED
                document.metadata_["indexed_at"] = asyncio.get_event_loop().time()
                document.metadata_["indexed_chunks"] = len(chunks)
                await db.commit()
                
                # Log de auditoría
                audit_logger.info(
                    "Document indexed",
                    extra={
                        "action": "document_indexed",
                        "document_id": str(document_id),
                        "filename": document.filename,
                        "chunk_count": len(chunks),
                        "classification": document.classification.value
                    }
                )
                
                logger.info(f"✅ Document {document_id} indexation completed successfully")
                
            except Exception as e:
                logger.error(f"Error indexing document {document_id}: {e}", exc_info=True)
                
                # Actualizar metadata con error (pero mantener PROCESSED)
                if 'document' in locals() and document:
                    document.metadata_["indexation_error"] = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    await db.commit()
                    
                    audit_logger.error(
                        "Document indexation failed",
                        extra={
                            "action": "document_indexation_failed",
                            "document_id": str(document_id),
                            "error": str(e)
                        }
                    )


async def main():
    """Función principal"""
    worker = IndexWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
