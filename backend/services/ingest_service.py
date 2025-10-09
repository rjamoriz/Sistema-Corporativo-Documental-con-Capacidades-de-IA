"""
Servicio de Ingesta de Documentos
Maneja la carga inicial de documentos, validación y almacenamiento en MinIO
"""
import hashlib
import mimetypes
from datetime import datetime
from typing import BinaryIO, Dict, Optional
from uuid import UUID

from minio import Minio
from minio.error import S3Error
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.config import settings
from backend.core.logging_config import logger, audit_logger
from backend.models.database_models import Document, DocumentStatus, DocumentClassification
from backend.models.schemas import DocumentCreate


class IngestService:
    """Servicio para ingesta de documentos"""
    
    def __init__(self):
        self.minio_client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Crea el bucket si no existe"""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                logger.info(f"Bucket {self.bucket_name} created")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise
    
    async def ingest_document(
        self,
        file: BinaryIO,
        filename: str,
        user_id: UUID,
        db: AsyncSession,
        metadata: Optional[Dict] = None
    ) -> Document:
        """
        Ingesta un documento completo
        
        Args:
            file: Archivo binario
            filename: Nombre del archivo
            user_id: ID del usuario que sube el documento
            db: Sesión de base de datos
            metadata: Metadata adicional opcional
            
        Returns:
            Document: Documento creado en la base de datos
        """
        try:
            # Leer contenido del archivo
            content = file.read()
            file_size = len(content)
            
            # Validar tamaño
            max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
            if file_size > max_size:
                raise ValueError(f"File size exceeds maximum of {settings.MAX_FILE_SIZE_MB}MB")
            
            # Detectar tipo MIME
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Validar tipo de archivo permitido
            allowed_types = settings.ALLOWED_FILE_TYPES
            if mime_type not in allowed_types:
                raise ValueError(f"File type {mime_type} not allowed")
            
            # Calcular hash del archivo
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Verificar duplicados
            existing_doc = await self._check_duplicate(db, file_hash)
            if existing_doc:
                logger.warning(f"Duplicate document detected: {file_hash}")
                return existing_doc
            
            # Generar ruta en MinIO
            object_name = f"{user_id}/{datetime.utcnow().strftime('%Y/%m/%d')}/{file_hash}_{filename}"
            
            # Subir a MinIO
            from io import BytesIO
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=BytesIO(content),
                length=file_size,
                content_type=mime_type
            )
            
            logger.info(f"File uploaded to MinIO: {object_name}")
            
            # Crear registro en base de datos
            document = Document(
                filename=filename,
                file_path=object_name,
                file_size=file_size,
                mime_type=mime_type,
                file_hash=file_hash,
                uploaded_by=user_id,
                status=DocumentStatus.PENDING,
                classification=DocumentClassification.UNCLASSIFIED,
                metadata_=metadata or {}
            )
            
            db.add(document)
            await db.commit()
            await db.refresh(document)
            
            # Log de auditoría
            audit_logger.info(
                "Document ingested",
                extra={
                    "action": "document_ingest",
                    "user_id": str(user_id),
                    "document_id": str(document.id),
                    "filename": filename,
                    "file_size": file_size,
                    "mime_type": mime_type,
                    "file_hash": file_hash
                }
            )
            
            logger.info(f"Document ingested successfully: {document.id}")
            return document
            
        except Exception as e:
            logger.error(f"Error ingesting document: {e}", exc_info=True)
            raise
    
    async def _check_duplicate(self, db: AsyncSession, file_hash: str) -> Optional[Document]:
        """Verifica si un documento con el mismo hash ya existe"""
        result = await db.execute(
            select(Document).where(Document.file_hash == file_hash)
        )
        return result.scalar_one_or_none()
    
    async def get_document_content(self, document: Document) -> bytes:
        """
        Obtiene el contenido binario de un documento desde MinIO
        
        Args:
            document: Documento del que obtener contenido
            
        Returns:
            bytes: Contenido del archivo
        """
        try:
            response = self.minio_client.get_object(
                bucket_name=self.bucket_name,
                object_name=document.file_path
            )
            content = response.read()
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            logger.error(f"Error retrieving document from MinIO: {e}")
            raise
    
    async def delete_document(self, document: Document, db: AsyncSession) -> bool:
        """
        Elimina un documento de MinIO y marca como eliminado en BD
        
        Args:
            document: Documento a eliminar
            db: Sesión de base de datos
            
        Returns:
            bool: True si la eliminación fue exitosa
        """
        try:
            # Eliminar de MinIO
            self.minio_client.remove_object(
                bucket_name=self.bucket_name,
                object_name=document.file_path
            )
            
            # Marcar como eliminado en BD (soft delete)
            document.deleted_at = datetime.utcnow()
            document.status = DocumentStatus.DELETED
            
            await db.commit()
            
            audit_logger.info(
                "Document deleted",
                extra={
                    "action": "document_delete",
                    "document_id": str(document.id),
                    "filename": document.filename
                }
            )
            
            logger.info(f"Document deleted: {document.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}", exc_info=True)
            return False
    
    def get_presigned_url(self, document: Document, expires: int = 3600) -> str:
        """
        Genera URL prefirmada para descarga directa
        
        Args:
            document: Documento para el que generar URL
            expires: Tiempo de expiración en segundos (default: 1 hora)
            
        Returns:
            str: URL prefirmada
        """
        try:
            from datetime import timedelta
            url = self.minio_client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=document.file_path,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise


# Instancia singleton del servicio
ingest_service = IngestService()
