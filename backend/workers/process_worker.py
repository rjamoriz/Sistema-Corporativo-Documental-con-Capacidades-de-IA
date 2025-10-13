"""
Worker de Procesamiento
Procesa documentos: transformación, extracción, clasificación, evaluación de riesgos
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
from models.database_models import Document, DocumentStatus, DocumentChunk
from services.ingest_service import ingest_service
from services.transform_service import transform_service
from services.extract_service import extract_service
from services.classification_service import classification_service
from services.risk_service import risk_service
from services.compliance_service import compliance_service
from middleware.validation_middleware import validation_middleware
from sqlalchemy import select


class ProcessWorker:
    """Worker para procesamiento completo de documentos"""
    
    def __init__(self):
        self.consumer = None
        self.producer = None
        self.topic_transform = "document.to_transform"
        self.topic_index = "document.to_index"
        self.running = False
    
    async def start(self):
        """Inicia el worker"""
        logger.info("Starting Process Worker...")
        
        # Inicializar consumer
        self.consumer = AIOKafkaConsumer(
            self.topic_transform,
            bootstrap_servers=f"{settings.KAFKA_BOOTSTRAP_SERVERS}",
            group_id="process-worker-group",
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
        logger.info("Process Worker started successfully")
        
        try:
            await self._consume_messages()
        finally:
            await self.stop()
    
    async def stop(self):
        """Detiene el worker"""
        logger.info("Stopping Process Worker...")
        self.running = False
        
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        
        logger.info("Process Worker stopped")
    
    async def _consume_messages(self):
        """Consume mensajes del topic"""
        async for message in self.consumer:
            try:
                event = message.value
                logger.info(f"Processing transform event: {event}")
                
                await self._process_document(event)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    
    async def _process_document(self, event: Dict):
        """
        Procesa completamente un documento
        
        Pipeline:
        1. Transformación (OCR, extracción de texto)
        2. Extracción (NER, embeddings, chunking)
        3. Clasificación
        4. Evaluación de riesgos
        5. Verificación de cumplimiento
        6. Envío a indexación
        
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
                
                logger.info(f"Starting processing pipeline for document {document_id}")
                
                # 1. TRANSFORMACIÓN: Extraer texto del documento
                logger.info(f"Step 1/5: Transforming document {document_id}")
                content = await ingest_service.get_document_content(document)
                transform_result = await transform_service.transform_document(document, content)
                
                extracted_text = transform_result.get("text", "")
                if not extracted_text:
                    raise ValueError("No text extracted from document")
                
                logger.info(
                    f"Transformation completed: {len(extracted_text)} chars, "
                    f"{transform_result.get('page_count', 0)} pages"
                )
                
                # Guardar metadata de transformación
                document.metadata_["transformation"] = {
                    "method": transform_result.get("method"),
                    "page_count": transform_result.get("page_count"),
                    "has_images": transform_result.get("has_images"),
                    "char_count": len(extracted_text)
                }
                await db.commit()
                
                # 2. EXTRACCIÓN: NER, embeddings, chunking
                logger.info(f"Step 2/5: Extracting information from document {document_id}")
                extract_result = await extract_service.extract_information(
                    document=document,
                    text=extracted_text,
                    db=db
                )
                
                logger.info(
                    f"Extraction completed: {extract_result['chunk_count']} chunks, "
                    f"{extract_result['entity_count']} entities"
                )
                
                # 3. VALIDACIÓN AUTOMÁTICA: Terceros, sanciones, registros
                logger.info(f"Step 3/6: Validating entities for document {document_id}")
                validation_result = None
                if await validation_middleware.should_validate(document):
                    # Obtener entidades extraídas
                    entities_result = await db.execute(
                        select(DocumentChunk).where(DocumentChunk.document_id == document_id)
                    )
                    chunks = entities_result.scalars().all()
                    
                    # Extraer entidades de los chunks
                    all_entities = []
                    for chunk in chunks:
                        if chunk.metadata_ and "entities" in chunk.metadata_:
                            all_entities.extend(chunk.metadata_["entities"])
                    
                    # Ejecutar validación
                    validation_result = await validation_middleware.validate_document(
                        document=document,
                        extracted_text=extracted_text,
                        entities=all_entities,
                        db=db
                    )
                    
                    # Guardar resultado de validación
                    document.metadata_["validation"] = validation_result
                    document.metadata_["validation_completed"] = True
                    await db.commit()
                    
                    logger.info(
                        f"Validation completed: {len(validation_result.get('flagged_entities', []))} entities flagged"
                    )
                else:
                    logger.info(f"Skipping validation for document {document_id}")
                
                # 4. CLASIFICACIÓN: Determinar categoría del documento
                logger.info(f"Step 4/6: Classifying document {document_id}")
                classification_result = await classification_service.classify_document(
                    document=document,
                    text=extracted_text,
                    db=db
                )
                
                logger.info(
                    f"Classification completed: {classification_result['category'].value} "
                    f"(confidence: {classification_result['confidence']:.2f})"
                )
                
                # 5. EVALUACIÓN DE RIESGOS: Análisis multidimensional
                logger.info(f"Step 5/6: Assessing risks for document {document_id}")
                risk_assessment = await risk_service.assess_risk(
                    document=document,
                    text=extracted_text,
                    db=db
                )
                
                logger.info(
                    f"Risk assessment completed: {risk_assessment.risk_level} "
                    f"(score: {risk_assessment.overall_risk_score:.2f})"
                )
                
                # 6. VERIFICACIÓN DE CUMPLIMIENTO: GDPR, etc.
                logger.info(f"Step 6/6: Checking compliance for document {document_id}")
                compliance_result = await compliance_service.run_compliance_checks(
                    document=document,
                    db=db
                )
                
                logger.info(
                    f"Compliance check completed: {'COMPLIANT' if compliance_result.is_compliant else 'NON-COMPLIANT'} "
                    f"(score: {compliance_result.compliance_score:.2f})"
                )
                
                # Actualizar estado final
                document.status = DocumentStatus.PROCESSED
                await db.commit()
                await db.refresh(document)
                
                # Enviar evento de indexación
                index_event = {
                    "document_id": str(document_id),
                    "chunk_count": extract_result['chunk_count'],
                    "classification": document.classification.value,
                    "risk_level": risk_assessment.risk_level,
                    "is_compliant": compliance_result.is_compliant,
                    "validation_completed": validation_result is not None,
                    "entities_flagged": len(validation_result.get("flagged_entities", [])) if validation_result else 0
                }
                
                await self.producer.send(self.topic_index, value=index_event)
                
                logger.info(f"✅ Document {document_id} processed successfully - sent to indexing")
                
                # Log de auditoría
                audit_logger.info(
                    "Document processing completed",
                    extra={
                        "action": "document_processed",
                        "document_id": str(document_id),
                        "filename": document.filename,
                        "classification": document.classification.value,
                        "chunk_count": extract_result['chunk_count'],
                        "entity_count": extract_result['entity_count'],
                        "risk_level": risk_assessment.risk_level,
                        "risk_score": risk_assessment.overall_risk_score,
                        "is_compliant": compliance_result.is_compliant,
                        "validation_completed": validation_result is not None,
                        "entities_flagged": len(validation_result.get("flagged_entities", [])) if validation_result else 0
                    }
                )
                
            except Exception as e:
                logger.error(f"Error processing document {document_id}: {e}", exc_info=True)
                
                # Marcar documento como fallido
                if 'document' in locals() and document:
                    document.status = DocumentStatus.FAILED
                    document.metadata_["processing_error"] = {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    await db.commit()
                    
                    audit_logger.error(
                        "Document processing failed",
                        extra={
                            "action": "document_processing_failed",
                            "document_id": str(document_id),
                            "error": str(e)
                        }
                    )


async def main():
    """Función principal"""
    worker = ProcessWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
