"""
SAP DMS Connector - Integration with SAP Document Management Service

Conecta con SAP DMS para:
- Listar repositorios de documentos
- Buscar documentos por metadata
- Descargar documentos
- Subir documentos
- Sincronización bidireccional
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import logging
import requests
from requests.auth import HTTPBasicAuth
import json

from .base_connector import (
    BaseConnector,
    ConnectorDocument,
    ConnectorConfig
)

logger = logging.getLogger(__name__)


class SAPDMSConfig(ConnectorConfig):
    """Configuración específica para SAP DMS"""
    
    url: str
    auth_type: str = "basic"  # "basic" or "oauth2"
    username: Optional[str] = None
    password: Optional[str] = None
    client: Optional[str] = "100"
    repositories: List[Dict[str, Any]] = []


class SAPDMSConnector(BaseConnector):
    """
    Conector para SAP Document Management Service.
    
    Utiliza la API REST de SAP DMS para acceder a repositorios
    y documentos almacenados en SAP.
    
    Example:
        ```python
        config = SAPDMSConfig(
            enabled=True,
            name="SAP DMS Production",
            type="sap_dms",
            url="https://sap-dms.company.com",
            username="dms_user",
            password="password",
            client="100"
        )
        
        async with SAPDMSConnector(config) as connector:
            repos = await connector.list_repositories()
            for repo in repos:
                print(f"Repository: {repo['name']}")
        ```
    """
    
    def __init__(self, config: SAPDMSConfig):
        super().__init__(config)
        self.config: SAPDMSConfig = config
        self.session: Optional[requests.Session] = None
        
        # Mapeo de campos SAP a FinancIA
        self.SAP_TO_FINANCIA_MAPPING = {
            "DOKNR": "sap_document_number",
            "DOKAR": "sap_document_type",
            "DOKVR": "sap_version",
            "DOKTL": "sap_part",
            "DOKST": "sap_status",
            "ERNAM": "sap_created_by",
            "ERDAT": "sap_created_date",
            "AENAM": "sap_modified_by",
            "AEDAT": "sap_modified_date",
            "DKTXT": "description",
            "DOKOB": "sap_object_type",
        }
    
    async def authenticate(self) -> bool:
        """
        Autenticarse con SAP DMS.
        
        Soporta autenticación básica y OAuth2.
        
        Returns:
            bool: True si autenticación exitosa
        """
        try:
            self.logger.info(f"Authenticating with SAP DMS at {self.config.url}")
            
            # Crear sesión HTTP
            self.session = requests.Session()
            
            if self.config.auth_type == "basic":
                # Autenticación básica
                if not self.config.username or not self.config.password:
                    raise ValueError("Username and password required for basic auth")
                
                self.session.auth = HTTPBasicAuth(
                    self.config.username,
                    self.config.password
                )
                
                # Headers comunes SAP
                self.session.headers.update({
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "sap-client": self.config.client or "100"
                })
                
                # Probar autenticación con endpoint de prueba
                test_url = f"{self.config.url}/sap/bc/srt/scs_ext/sap/managedocumentcontentservice"
                response = self.session.get(test_url, timeout=30)
                
                if response.status_code == 401:
                    self.logger.error("Authentication failed: Invalid credentials")
                    return False
                
                self._authenticated = True
                self.logger.info("Authentication successful")
                return True
                
            elif self.config.auth_type == "oauth2":
                # TODO: Implementar OAuth2 para SAP
                raise NotImplementedError("OAuth2 authentication not yet implemented")
            
            else:
                raise ValueError(f"Unknown auth type: {self.config.auth_type}")
                
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Probar conexión con SAP DMS.
        
        Returns:
            bool: True si conexión exitosa
        """
        try:
            if not self.session:
                return False
            
            # Intentar listar repositorios
            repos = await self.list_repositories()
            
            self.logger.info(f"Connection test successful. Found {len(repos)} repositories")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    async def list_repositories(self) -> List[Dict[str, Any]]:
        """
        Listar repositorios SAP DMS disponibles.
        
        En SAP, los repositorios son normalmente configurados
        y se acceden por ID predefinido.
        
        Returns:
            List[Dict]: Lista de repositorios configurados
        """
        try:
            if not self.session:
                raise Exception("Not authenticated")
            
            self.logger.info("Listing SAP DMS repositories")
            
            # Si hay repositorios configurados, devolverlos
            if self.config.repositories:
                repositories = []
                for repo_config in self.config.repositories:
                    repositories.append({
                        "id": repo_config.get("id"),
                        "name": repo_config.get("name"),
                        "type": "sap_dms_repository",
                        "sync_filters": repo_config.get("sync_filters", {})
                    })
                
                self.logger.info(f"Found {len(repositories)} configured repositories")
                return repositories
            
            # Si no hay configuración, intentar obtener de SAP
            # Endpoint para listar repositorios (puede variar según versión SAP)
            endpoint = f"{self.config.url}/sap/opu/odata/sap/DOCUMENTSERVICE/Repositories"
            
            response = self.session.get(endpoint, timeout=30)
            
            if response.status_code == 404:
                # Endpoint no disponible, usar configuración
                self.logger.warning("Repositories endpoint not available, using configuration")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            repositories = []
            if "d" in data and "results" in data["d"]:
                for repo in data["d"]["results"]:
                    repositories.append({
                        "id": repo.get("RepositoryId"),
                        "name": repo.get("RepositoryName"),
                        "description": repo.get("Description"),
                        "type": "sap_dms_repository"
                    })
            
            self.logger.info(f"Found {len(repositories)} repositories")
            return repositories
            
        except Exception as e:
            self.logger.error(f"Error listing repositories: {e}")
            # En caso de error, devolver repositorios configurados
            if self.config.repositories:
                return [{"id": r["id"], "name": r["name"], "type": "sap_dms_repository"} 
                        for r in self.config.repositories]
            return []
    
    async def search_documents(
        self,
        repository_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ConnectorDocument]:
        """
        Buscar documentos en SAP DMS por metadata.
        
        Args:
            repository_id: ID del repositorio
            filters: Filtros de búsqueda (status, document_type, etc)
            
        Returns:
            List[ConnectorDocument]: Lista de documentos encontrados
        """
        try:
            if not self.session:
                raise Exception("Not authenticated")
            
            self.logger.info(f"Searching documents in repository {repository_id}")
            
            # Construir query OData
            endpoint = f"{self.config.url}/sap/opu/odata/sap/DOCUMENTSERVICE/Documents"
            
            # Construir filtros OData
            odata_filters = []
            
            if filters:
                if "status" in filters:
                    statuses = filters["status"]
                    if isinstance(statuses, list):
                        status_filter = " or ".join([f"DOKST eq '{s}'" for s in statuses])
                        odata_filters.append(f"({status_filter})")
                    else:
                        odata_filters.append(f"DOKST eq '{statuses}'")
                
                if "document_type" in filters:
                    doc_types = filters["document_type"]
                    if isinstance(doc_types, list):
                        type_filter = " or ".join([f"DOKAR eq '{t}'" for t in doc_types])
                        odata_filters.append(f"({type_filter})")
                    else:
                        odata_filters.append(f"DOKAR eq '{doc_types}'")
            
            # Agregar filtro de repositorio si es necesario
            # odata_filters.append(f"RepositoryId eq '{repository_id}'")
            
            # Construir URL con filtros
            params = {}
            if odata_filters:
                params["$filter"] = " and ".join(odata_filters)
            
            params["$top"] = self.config.batch_size or 100
            params["$format"] = "json"
            
            self.logger.debug(f"OData query: {params}")
            
            response = self.session.get(endpoint, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            documents = []
            if "d" in data and "results" in data["d"]:
                for doc_data in data["d"]["results"]:
                    doc = self._parse_sap_document(doc_data, repository_id)
                    documents.append(doc)
            
            self.logger.info(f"Found {len(documents)} documents")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            return []
    
    async def list_documents(
        self,
        repository_id: str,
        path: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ConnectorDocument]:
        """
        Listar documentos en un repositorio SAP.
        
        En SAP DMS, list_documents es similar a search_documents.
        
        Args:
            repository_id: ID del repositorio
            path: No usado en SAP (compatibilidad con BaseConnector)
            filters: Filtros de búsqueda
            
        Returns:
            List[ConnectorDocument]: Lista de documentos
        """
        return await self.search_documents(repository_id, filters)
    
    def _parse_sap_document(
        self,
        doc_data: Dict[str, Any],
        repository_id: str
    ) -> ConnectorDocument:
        """
        Parsear documento SAP a ConnectorDocument.
        
        Args:
            doc_data: Datos del documento desde SAP OData
            repository_id: ID del repositorio
            
        Returns:
            ConnectorDocument: Documento parseado
        """
        # Extraer campos principales
        doc_number = doc_data.get("DOKNR", "")
        doc_type = doc_data.get("DOKAR", "")
        doc_version = doc_data.get("DOKVR", "00")
        doc_part = doc_data.get("DOKTL", "000")
        
        # Construir ID único
        document_id = f"{repository_id}|{doc_type}|{doc_number}|{doc_version}|{doc_part}"
        
        # Construir nombre de archivo
        filename = doc_data.get("DKTXT", f"{doc_number}.bin")
        if not filename.endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
            filename = f"{filename}.pdf"  # Default a PDF
        
        # Parsear fechas
        created_date = self._parse_sap_date(doc_data.get("ERDAT"))
        modified_date = self._parse_sap_date(doc_data.get("AEDAT"))
        
        # Metadata SAP
        metadata = {}
        for sap_field, financia_field in self.SAP_TO_FINANCIA_MAPPING.items():
            if sap_field in doc_data:
                metadata[financia_field] = doc_data[sap_field]
        
        metadata["repository_id"] = repository_id
        
        return ConnectorDocument(
            id=document_id,
            name=filename,
            size=doc_data.get("FILE_SIZE", 0),
            mime_type=doc_data.get("MIMETYPE", "application/pdf"),
            created_at=created_date,
            modified_at=modified_date,
            created_by=doc_data.get("ERNAM"),
            modified_by=doc_data.get("AENAM"),
            path=f"{repository_id}/{doc_type}/{doc_number}",
            url=f"{self.config.url}/document/{doc_number}",
            metadata=metadata
        )
    
    def _parse_sap_date(self, sap_date: Optional[str]) -> datetime:
        """
        Parsear fecha SAP (formato YYYYMMDD) a datetime.
        
        Args:
            sap_date: Fecha en formato SAP (YYYYMMDD)
            
        Returns:
            datetime: Fecha parseada
        """
        if not sap_date:
            return datetime.now()
        
        try:
            # SAP usa formato YYYYMMDD
            if len(sap_date) == 8:
                year = int(sap_date[0:4])
                month = int(sap_date[4:6])
                day = int(sap_date[6:8])
                return datetime(year, month, day)
            else:
                return datetime.now()
        except Exception:
            return datetime.now()
    
    async def get_document(self, document_id: str) -> ConnectorDocument:
        """
        Obtener metadata completa de un documento.
        
        Args:
            document_id: ID en formato "repo|type|number|version|part"
            
        Returns:
            ConnectorDocument: Documento con metadata
        """
        try:
            if not self.session:
                raise Exception("Not authenticated")
            
            # Parsear document_id
            parts = document_id.split("|")
            if len(parts) != 5:
                raise ValueError("Invalid document_id format. Expected: repo|type|number|version|part")
            
            repository_id, doc_type, doc_number, doc_version, doc_part = parts
            
            self.logger.info(f"Getting document {doc_number} from SAP")
            
            # Endpoint para obtener documento específico
            endpoint = f"{self.config.url}/sap/opu/odata/sap/DOCUMENTSERVICE/Documents(DocumentType='{doc_type}',DocumentNumber='{doc_number}',DocumentVersion='{doc_version}',DocumentPart='{doc_part}')"
            
            params = {"$format": "json"}
            
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "d" in data:
                doc = self._parse_sap_document(data["d"], repository_id)
                return doc
            else:
                raise Exception("Document not found")
                
        except Exception as e:
            self.logger.error(f"Error getting document: {e}")
            raise
    
    async def download_document(self, document_id: str) -> bytes:
        """
        Descargar contenido de un documento desde SAP.
        
        Args:
            document_id: ID en formato "repo|type|number|version|part"
            
        Returns:
            bytes: Contenido del documento
        """
        try:
            if not self.session:
                raise Exception("Not authenticated")
            
            # Parsear document_id
            parts = document_id.split("|")
            if len(parts) != 5:
                raise ValueError("Invalid document_id format")
            
            repository_id, doc_type, doc_number, doc_version, doc_part = parts
            
            self.logger.info(f"Downloading document {doc_number} from SAP")
            
            # Endpoint para descargar contenido
            # Nota: Este endpoint puede variar según la versión de SAP DMS
            endpoint = f"{self.config.url}/sap/opu/odata/sap/DOCUMENTSERVICE/Documents(DocumentType='{doc_type}',DocumentNumber='{doc_number}',DocumentVersion='{doc_version}',DocumentPart='{doc_part}')/$value"
            
            response = self.session.get(endpoint, timeout=300)  # 5 min timeout para archivos grandes
            response.raise_for_status()
            
            content = response.content
            
            self.logger.info(f"Downloaded {len(content)} bytes")
            return content
            
        except Exception as e:
            self.logger.error(f"Error downloading document: {e}")
            raise
    
    async def upload_document(
        self,
        repository_id: str,
        filename: str,
        content: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConnectorDocument:
        """
        Subir un documento a SAP DMS.
        
        Args:
            repository_id: ID del repositorio
            filename: Nombre del archivo
            content: Contenido del archivo
            metadata: Metadata adicional (SAP fields)
            
        Returns:
            ConnectorDocument: Documento creado
        """
        try:
            if not self.session:
                raise Exception("Not authenticated")
            
            self.logger.info(f"Uploading document {filename} to SAP repository {repository_id}")
            
            # Preparar metadata SAP
            sap_metadata = metadata or {}
            
            # Documento tipo por defecto
            doc_type = sap_metadata.get("DOKAR", "DWS")  # Document Workspace
            
            # Crear documento en SAP
            endpoint = f"{self.config.url}/sap/opu/odata/sap/DOCUMENTSERVICE/Documents"
            
            # Datos del documento
            doc_data = {
                "DocumentType": doc_type,
                "Description": sap_metadata.get("DKTXT", filename),
                "StatusInternal": sap_metadata.get("DOKST", ""),
            }
            
            # Crear documento
            headers = {"Content-Type": "application/json"}
            response = self.session.post(
                endpoint,
                json=doc_data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            created_doc = response.json()["d"]
            doc_number = created_doc["DocumentNumber"]
            doc_version = created_doc["DocumentVersion"]
            doc_part = created_doc["DocumentPart"]
            
            # Subir contenido
            content_endpoint = f"{endpoint}(DocumentType='{doc_type}',DocumentNumber='{doc_number}',DocumentVersion='{doc_version}',DocumentPart='{doc_part}')/$value"
            
            content_response = self.session.put(
                content_endpoint,
                data=content,
                headers={"Content-Type": "application/octet-stream"},
                timeout=300
            )
            content_response.raise_for_status()
            
            # Construir document_id
            document_id = f"{repository_id}|{doc_type}|{doc_number}|{doc_version}|{doc_part}"
            
            # Obtener documento completo
            doc = await self.get_document(document_id)
            
            self.logger.info(f"Upload successful: {filename}")
            return doc
            
        except Exception as e:
            self.logger.error(f"Error uploading document: {e}")
            raise
    
    def _map_metadata(self, source_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapear metadata de SAP a formato FinancIA.
        
        Args:
            source_metadata: Metadata de SAP
            
        Returns:
            Dict: Metadata en formato FinancIA
        """
        mapped = {
            "source": "sap_dms",
            "sap_repository": source_metadata.get("repository_id"),
        }
        
        # Agregar campos mapeados
        for sap_field, financia_field in self.SAP_TO_FINANCIA_MAPPING.items():
            if financia_field in source_metadata:
                mapped[financia_field] = source_metadata[financia_field]
        
        return mapped


# Alias for easier import
SAPDMS = SAPDMSConnector
