"""
Base Connector - Abstract Base Class for Enterprise Connectors

Todos los conectores deben heredar de esta clase y implementar los métodos abstractos.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ConnectorDocument(BaseModel):
    """Modelo estándar para documentos de conectores"""
    
    id: str
    name: str
    size: int
    mime_type: str
    created_at: datetime
    modified_at: datetime
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    path: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    content: Optional[bytes] = None


class ConnectorConfig(BaseModel):
    """Configuración base para conectores"""
    
    enabled: bool = False
    name: str
    type: str
    sync_schedule: Optional[str] = None
    retry_attempts: int = 3
    timeout_seconds: int = 300
    batch_size: int = 100


class BaseConnector(ABC):
    """
    Clase base abstracta para todos los conectores enterprise.
    
    Define la interfaz común que deben implementar todos los conectores
    para garantizar consistencia y facilitar el mantenimiento.
    """
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._authenticated = False
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Autenticarse con el sistema externo.
        
        Returns:
            bool: True si autenticación exitosa, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Probar conexión con el sistema externo.
        
        Returns:
            bool: True si conexión exitosa, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def list_repositories(self) -> List[Dict[str, Any]]:
        """
        Listar repositorios/sitios/bibliotecas disponibles.
        
        Returns:
            List[Dict]: Lista de repositorios con metadata
        """
        pass
    
    @abstractmethod
    async def list_documents(
        self,
        repository_id: str,
        path: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ConnectorDocument]:
        """
        Listar documentos en un repositorio.
        
        Args:
            repository_id: ID del repositorio
            path: Ruta específica (opcional)
            filters: Filtros de búsqueda (opcional)
            
        Returns:
            List[ConnectorDocument]: Lista de documentos
        """
        pass
    
    @abstractmethod
    async def get_document(self, document_id: str) -> ConnectorDocument:
        """
        Obtener un documento específico con metadata completa.
        
        Args:
            document_id: ID del documento
            
        Returns:
            ConnectorDocument: Documento con metadata
        """
        pass
    
    @abstractmethod
    async def download_document(self, document_id: str) -> bytes:
        """
        Descargar contenido de un documento.
        
        Args:
            document_id: ID del documento
            
        Returns:
            bytes: Contenido del documento
        """
        pass
    
    @abstractmethod
    async def upload_document(
        self,
        repository_id: str,
        filename: str,
        content: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConnectorDocument:
        """
        Subir un documento al sistema externo.
        
        Args:
            repository_id: ID del repositorio destino
            filename: Nombre del archivo
            content: Contenido del archivo
            metadata: Metadata adicional (opcional)
            
        Returns:
            ConnectorDocument: Documento creado
        """
        pass
    
    async def sync_to_financia(
        self,
        repository_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sincronizar documentos desde sistema externo a FinancIA.
        
        Este método provee una implementación base que puede ser
        sobrescrita por conectores específicos si necesitan lógica custom.
        
        Args:
            repository_id: ID del repositorio a sincronizar
            filters: Filtros para documentos a sincronizar
            
        Returns:
            Dict: Estadísticas de sincronización
        """
        from backend.services.ingest_service import IngestService
        
        self.logger.info(f"Starting sync from {repository_id}")
        
        stats = {
            "total_documents": 0,
            "synced": 0,
            "skipped": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat(),
        }
        
        try:
            # Listar documentos
            documents = await self.list_documents(repository_id, filters=filters)
            stats["total_documents"] = len(documents)
            
            ingest_service = IngestService()
            
            # Procesar cada documento
            for doc in documents:
                try:
                    # Descargar contenido
                    content = await self.download_document(doc.id)
                    
                    # Preparar metadata
                    metadata = {
                        "source": self.config.type,
                        "source_id": doc.id,
                        "source_url": doc.url,
                        **doc.metadata
                    }
                    
                    # Ingerir en FinancIA
                    await ingest_service.upload(
                        filename=doc.name,
                        content=content,
                        metadata=metadata
                    )
                    
                    stats["synced"] += 1
                    self.logger.debug(f"Synced document: {doc.name}")
                    
                except Exception as e:
                    stats["errors"] += 1
                    self.logger.error(f"Error syncing {doc.name}: {e}")
            
            stats["end_time"] = datetime.now().isoformat()
            self.logger.info(
                f"Sync completed: {stats['synced']}/{stats['total_documents']} documents"
            )
            
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            stats["error"] = str(e)
        
        return stats
    
    def _map_metadata(self, source_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapear metadata del sistema externo a formato FinancIA.
        
        Este método puede ser sobrescrito por conectores específicos.
        
        Args:
            source_metadata: Metadata del sistema externo
            
        Returns:
            Dict: Metadata en formato FinancIA
        """
        return source_metadata
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
