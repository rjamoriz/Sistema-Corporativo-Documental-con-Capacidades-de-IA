"""
SharePoint Connector - Integration with SharePoint Online and On-Premises

Conecta con SharePoint usando Microsoft Graph API para:
- Listar sitios y bibliotecas
- Descargar documentos
- Subir documentos
- Sincronización automática
- Webhooks para cambios en tiempo real
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
import requests

try:
    from msal import ConfidentialClientApplication
    from msgraph import GraphServiceClient
    from msgraph.generated.models.site import Site
    from msgraph.generated.models.drive_item import DriveItem
    from azure.identity import ClientSecretCredential
    MSGRAPH_AVAILABLE = True
except ImportError:
    MSGRAPH_AVAILABLE = False
    logging.warning(
        "Microsoft Graph SDK not installed. "
        "Install with: pip install msal msgraph-sdk-python azure-identity"
    )

from .base_connector import (
    BaseConnector,
    ConnectorDocument,
    ConnectorConfig
)

logger = logging.getLogger(__name__)


class SharePointConfig(ConnectorConfig):
    """Configuración específica para SharePoint"""
    
    tenant_id: str
    client_id: str
    client_secret: str
    site_url: Optional[str] = None
    sites: List[Dict[str, Any]] = []
    webhook_enabled: bool = False
    webhook_expiration_days: int = 30


class SharePointConnector(BaseConnector):
    """
    Conector para SharePoint Online y On-Premises.
    
    Utiliza Microsoft Graph API para acceder a sitios,
    bibliotecas y documentos de SharePoint.
    
    Example:
        ```python
        config = SharePointConfig(
            enabled=True,
            name="Corporate SharePoint",
            type="sharepoint",
            tenant_id="your-tenant-id",
            client_id="your-client-id",
            client_secret="your-secret"
        )
        
        async with SharePointConnector(config) as connector:
            sites = await connector.list_repositories()
            for site in sites:
                print(f"Site: {site['name']}")
        ```
    """
    
    def __init__(self, config: SharePointConfig):
        super().__init__(config)
        self.config: SharePointConfig = config
        
        if not MSGRAPH_AVAILABLE:
            raise ImportError(
                "Microsoft Graph SDK is required. "
                "Install with: pip install msal msgraph-sdk-python azure-identity"
            )
        
        self.client: Optional[GraphServiceClient] = None
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
    
    async def authenticate(self) -> bool:
        """
        Autenticarse con Microsoft Graph API usando OAuth2.
        
        Utiliza Client Credentials Flow para autenticación de app-to-app.
        
        Returns:
            bool: True si autenticación exitosa
        """
        try:
            self.logger.info("Authenticating with Microsoft Graph API")
            
            # Crear aplicación MSAL
            app = ConfidentialClientApplication(
                client_id=self.config.client_id,
                client_credential=self.config.client_secret,
                authority=f"https://login.microsoftonline.com/{self.config.tenant_id}"
            )
            
            # Obtener token
            result = app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )
            
            if "access_token" in result:
                self._access_token = result["access_token"]
                # Los tokens típicamente duran 1 hora
                self._token_expires_at = datetime.now() + timedelta(hours=1)
                
                # Crear cliente de Graph
                credential = ClientSecretCredential(
                    tenant_id=self.config.tenant_id,
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret
                )
                
                self.client = GraphServiceClient(credential)
                
                self._authenticated = True
                self.logger.info("Authentication successful")
                return True
            else:
                error = result.get("error_description", "Unknown error")
                self.logger.error(f"Authentication failed: {error}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    async def _refresh_token_if_needed(self):
        """Refrescar token si está próximo a expirar"""
        if self._token_expires_at:
            # Refrescar si quedan menos de 5 minutos
            if datetime.now() + timedelta(minutes=5) > self._token_expires_at:
                self.logger.info("Token expiring soon, refreshing")
                await self.authenticate()
    
    async def test_connection(self) -> bool:
        """
        Probar conexión listando sitios.
        
        Returns:
            bool: True si conexión exitosa
        """
        try:
            await self._refresh_token_if_needed()
            
            if not self.client:
                return False
            
            # Intentar listar sitios (solo los primeros 5)
            sites = await self.client.sites.get()
            
            self.logger.info(f"Connection test successful. Found {len(sites.value)} sites")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    async def list_repositories(self) -> List[Dict[str, Any]]:
        """
        Listar sitios de SharePoint disponibles.
        
        Returns:
            List[Dict]: Lista de sitios con ID, nombre, URL
        """
        try:
            await self._refresh_token_if_needed()
            
            if not self.client:
                raise Exception("Not authenticated")
            
            self.logger.info("Listing SharePoint sites")
            
            # Obtener sitios
            sites_response = await self.client.sites.get()
            
            repositories = []
            for site in sites_response.value:
                repositories.append({
                    "id": site.id,
                    "name": site.display_name or site.name,
                    "url": site.web_url,
                    "description": site.description,
                    "created_at": site.created_date_time.isoformat() if site.created_date_time else None,
                    "type": "sharepoint_site"
                })
            
            self.logger.info(f"Found {len(repositories)} sites")
            return repositories
            
        except Exception as e:
            self.logger.error(f"Error listing repositories: {e}")
            return []
    
    async def list_documents(
        self,
        repository_id: str,
        path: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ConnectorDocument]:
        """
        Listar documentos en una biblioteca de SharePoint.
        
        Args:
            repository_id: ID del sitio SharePoint
            path: Ruta específica o nombre de biblioteca (ej: "Shared Documents")
            filters: Filtros adicionales (file_types, modified_after, etc)
            
        Returns:
            List[ConnectorDocument]: Lista de documentos
        """
        try:
            await self._refresh_token_if_needed()
            
            if not self.client:
                raise Exception("Not authenticated")
            
            self.logger.info(f"Listing documents in site {repository_id}, path: {path}")
            
            documents = []
            
            # Obtener drives (bibliotecas) del sitio
            site = await self.client.sites.by_site_id(repository_id).get()
            drives_response = await self.client.sites.by_site_id(repository_id).drives.get()
            
            for drive in drives_response.value:
                # Si se especificó un path, filtrar por nombre de biblioteca
                if path and drive.name != path:
                    continue
                
                # Listar items del drive
                items_response = await self.client.sites.by_site_id(repository_id).drives.by_drive_id(drive.id).root.children.get()
                
                for item in items_response.value:
                    # Solo procesar archivos, no carpetas
                    if item.file is None:
                        continue
                    
                    # Aplicar filtros si se especificaron
                    if filters:
                        if "file_types" in filters:
                            ext = os.path.splitext(item.name)[1].lower()
                            if ext not in filters["file_types"]:
                                continue
                        
                        if "modified_after" in filters:
                            if item.last_modified_date_time < filters["modified_after"]:
                                continue
                    
                    # Crear ConnectorDocument
                    doc = ConnectorDocument(
                        id=item.id,
                        name=item.name,
                        size=item.size or 0,
                        mime_type=item.file.mime_type or "application/octet-stream",
                        created_at=item.created_date_time,
                        modified_at=item.last_modified_date_time,
                        created_by=item.created_by.user.display_name if item.created_by and item.created_by.user else None,
                        modified_by=item.last_modified_by.user.display_name if item.last_modified_by and item.last_modified_by.user else None,
                        path=f"{drive.name}/{item.name}",
                        url=item.web_url,
                        metadata={
                            "drive_id": drive.id,
                            "drive_name": drive.name,
                            "site_id": repository_id,
                            "site_name": site.display_name,
                            "e_tag": item.e_tag,
                        }
                    )
                    
                    documents.append(doc)
            
            self.logger.info(f"Found {len(documents)} documents")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error listing documents: {e}")
            return []
    
    async def get_document(self, document_id: str) -> ConnectorDocument:
        """
        Obtener metadata completa de un documento.
        
        Args:
            document_id: ID del documento en formato "site_id|drive_id|item_id"
            
        Returns:
            ConnectorDocument: Documento con metadata completa
        """
        try:
            await self._refresh_token_if_needed()
            
            if not self.client:
                raise Exception("Not authenticated")
            
            # El document_id debe venir en formato "site_id|drive_id|item_id"
            parts = document_id.split("|")
            if len(parts) != 3:
                raise ValueError("Invalid document_id format. Expected: site_id|drive_id|item_id")
            
            site_id, drive_id, item_id = parts
            
            self.logger.info(f"Getting document {item_id} from drive {drive_id}")
            
            # Obtener item
            item = await self.client.sites.by_site_id(site_id).drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).get()
            
            # Obtener info del sitio y drive
            site = await self.client.sites.by_site_id(site_id).get()
            drive = await self.client.sites.by_site_id(site_id).drives.by_drive_id(drive_id).get()
            
            doc = ConnectorDocument(
                id=document_id,
                name=item.name,
                size=item.size or 0,
                mime_type=item.file.mime_type if item.file else "application/octet-stream",
                created_at=item.created_date_time,
                modified_at=item.last_modified_date_time,
                created_by=item.created_by.user.display_name if item.created_by and item.created_by.user else None,
                modified_by=item.last_modified_by.user.display_name if item.last_modified_by and item.last_modified_by.user else None,
                path=f"{drive.name}/{item.name}",
                url=item.web_url,
                metadata={
                    "drive_id": drive_id,
                    "drive_name": drive.name,
                    "site_id": site_id,
                    "site_name": site.display_name,
                    "e_tag": item.e_tag,
                    "item_id": item_id,
                }
            )
            
            return doc
            
        except Exception as e:
            self.logger.error(f"Error getting document: {e}")
            raise
    
    async def download_document(self, document_id: str) -> bytes:
        """
        Descargar contenido de un documento.
        
        Args:
            document_id: ID del documento en formato "site_id|drive_id|item_id"
            
        Returns:
            bytes: Contenido del documento
        """
        try:
            await self._refresh_token_if_needed()
            
            if not self.client:
                raise Exception("Not authenticated")
            
            parts = document_id.split("|")
            if len(parts) != 3:
                raise ValueError("Invalid document_id format")
            
            site_id, drive_id, item_id = parts
            
            self.logger.info(f"Downloading document {item_id}")
            
            # Descargar contenido
            content_stream = await self.client.sites.by_site_id(site_id).drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).content.get()
            
            # Leer stream completo
            content = await content_stream.read()
            
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
        Subir un documento a SharePoint.
        
        Args:
            repository_id: ID del sitio (formato: "site_id|drive_id")
            filename: Nombre del archivo
            content: Contenido del archivo
            metadata: Metadata adicional (opcional)
            
        Returns:
            ConnectorDocument: Documento creado
        """
        try:
            await self._refresh_token_if_needed()
            
            if not self.client:
                raise Exception("Not authenticated")
            
            parts = repository_id.split("|")
            if len(parts) != 2:
                raise ValueError("Invalid repository_id format. Expected: site_id|drive_id")
            
            site_id, drive_id = parts
            
            self.logger.info(f"Uploading document {filename} to drive {drive_id}")
            
            # Upload using simple upload (< 4MB) or session upload (> 4MB)
            if len(content) < 4 * 1024 * 1024:  # 4MB
                # Simple upload
                item = await self.client.sites.by_site_id(site_id).drives.by_drive_id(drive_id).root.children[filename].content.put(content)
            else:
                # Session upload para archivos grandes
                item = await self._upload_large_file(site_id, drive_id, filename, content)
            
            # Construir document_id
            document_id = f"{site_id}|{drive_id}|{item.id}"
            
            # Obtener documento completo
            doc = await self.get_document(document_id)
            
            self.logger.info(f"Upload successful: {filename}")
            return doc
            
        except Exception as e:
            self.logger.error(f"Error uploading document: {e}")
            raise
    
    async def _upload_large_file(
        self,
        site_id: str,
        drive_id: str,
        filename: str,
        content: bytes,
        chunk_size: int = 10 * 1024 * 1024  # 10MB chunks
    ) -> Any:
        """
        Upload archivo grande usando resumable upload session.
        
        Para archivos > 4MB, SharePoint requiere usar upload sessions
        que permiten subir el archivo en chunks y manejar reintento.
        
        Args:
            site_id: ID del sitio
            drive_id: ID del drive
            filename: Nombre del archivo
            content: Contenido del archivo
            chunk_size: Tamaño de cada chunk (default 10MB)
            
        Returns:
            DriveItem: Item creado
        """
        try:
            self.logger.info(f"Starting large file upload: {filename} ({len(content)} bytes)")
            
            # Crear upload session
            upload_session_request = {
                "item": {
                    "@microsoft.graph.conflictBehavior": "rename",
                    "name": filename
                }
            }
            
            # Endpoint para crear session
            session_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{filename}:/createUploadSession"
            
            # Crear session con requests directo (más control)
            import requests
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                session_url,
                json=upload_session_request,
                headers=headers
            )
            response.raise_for_status()
            
            session_data = response.json()
            upload_url = session_data["uploadUrl"]
            
            self.logger.info(f"Upload session created: {upload_url}")
            
            # Upload en chunks
            total_size = len(content)
            uploaded = 0
            
            while uploaded < total_size:
                # Calcular chunk actual
                chunk_start = uploaded
                chunk_end = min(uploaded + chunk_size, total_size)
                chunk = content[chunk_start:chunk_end]
                
                # Headers para este chunk
                chunk_headers = {
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {chunk_start}-{chunk_end-1}/{total_size}"
                }
                
                # Upload chunk
                self.logger.debug(f"Uploading chunk: {chunk_start}-{chunk_end-1}/{total_size}")
                
                chunk_response = requests.put(
                    upload_url,
                    data=chunk,
                    headers=chunk_headers
                )
                chunk_response.raise_for_status()
                
                uploaded = chunk_end
                
                # Log progress
                progress = (uploaded / total_size) * 100
                self.logger.info(f"Upload progress: {progress:.1f}% ({uploaded}/{total_size} bytes)")
            
            # El último chunk response contiene el item creado
            final_response = chunk_response.json()
            
            self.logger.info(f"Large file upload completed: {filename}")
            
            # Convertir response a objeto similar a DriveItem
            # Para simplificar, devolvemos un objeto mock con los datos necesarios
            class MockDriveItem:
                def __init__(self, data):
                    self.id = data.get("id")
                    self.name = data.get("name")
            
            return MockDriveItem(final_response)
            
        except Exception as e:
            self.logger.error(f"Error in large file upload: {e}")
            raise
    
    def _map_metadata(self, source_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapear metadata de SharePoint a formato FinancIA.
        
        Args:
            source_metadata: Metadata de SharePoint
            
        Returns:
            Dict: Metadata en formato FinancIA
        """
        return {
            "source": "sharepoint",
            "sharepoint_site_id": source_metadata.get("site_id"),
            "sharepoint_site_name": source_metadata.get("site_name"),
            "sharepoint_drive_id": source_metadata.get("drive_id"),
            "sharepoint_drive_name": source_metadata.get("drive_name"),
            "sharepoint_item_id": source_metadata.get("item_id"),
            "sharepoint_url": source_metadata.get("url"),
            "sharepoint_etag": source_metadata.get("e_tag"),
        }


# Alias for easier import
SharePoint = SharePointConnector
