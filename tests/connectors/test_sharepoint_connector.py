"""
Tests for SharePoint Connector

Estos tests verifican la funcionalidad del conector de SharePoint,
incluyendo autenticación, listado de sitios, documentos, descarga, upload, etc.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from backend.connectors.sharepoint_connector import (
    SharePointConnector,
    SharePointConfig,
    ConnectorDocument
)


@pytest.fixture
def sharepoint_config():
    """Configuración de prueba para SharePoint"""
    return SharePointConfig(
        enabled=True,
        name="Test SharePoint",
        type="sharepoint",
        tenant_id="test-tenant-id",
        client_id="test-client-id",
        client_secret="test-client-secret",
        sites=[
            {
                "name": "Corporate",
                "site_id": "test-site-123",
                "libraries": ["Shared Documents"]
            }
        ]
    )


@pytest.fixture
def mock_graph_client():
    """Mock de Microsoft Graph Client"""
    client = Mock()
    
    # Mock sites
    mock_site = Mock()
    mock_site.id = "test-site-123"
    mock_site.display_name = "Corporate Documents"
    mock_site.name = "Corporate"
    mock_site.web_url = "https://test.sharepoint.com/sites/corporate"
    mock_site.description = "Test site"
    mock_site.created_date_time = datetime.now()
    
    sites_response = Mock()
    sites_response.value = [mock_site]
    
    client.sites.get = AsyncMock(return_value=sites_response)
    client.sites.by_site_id = Mock(return_value=Mock())
    
    # Mock drives
    mock_drive = Mock()
    mock_drive.id = "test-drive-123"
    mock_drive.name = "Shared Documents"
    
    drives_response = Mock()
    drives_response.value = [mock_drive]
    
    client.sites.by_site_id().drives.get = AsyncMock(return_value=drives_response)
    
    # Mock drive items
    mock_item = Mock()
    mock_item.id = "test-item-123"
    mock_item.name = "test-document.pdf"
    mock_item.size = 1024
    mock_item.file = Mock(mime_type="application/pdf")
    mock_item.created_date_time = datetime.now()
    mock_item.last_modified_date_time = datetime.now()
    mock_item.created_by = Mock(user=Mock(display_name="Test User"))
    mock_item.last_modified_by = Mock(user=Mock(display_name="Test User"))
    mock_item.web_url = "https://test.sharepoint.com/test.pdf"
    mock_item.e_tag = "test-etag"
    
    items_response = Mock()
    items_response.value = [mock_item]
    
    client.sites.by_site_id().drives.by_drive_id().root.children.get = AsyncMock(
        return_value=items_response
    )
    
    # Mock get item
    client.sites.by_site_id().drives.by_drive_id().items.by_drive_item_id().get = AsyncMock(
        return_value=mock_item
    )
    
    # Mock content download
    mock_content_stream = AsyncMock()
    mock_content_stream.read = AsyncMock(return_value=b"Test PDF content")
    
    client.sites.by_site_id().drives.by_drive_id().items.by_drive_item_id().content.get = AsyncMock(
        return_value=mock_content_stream
    )
    
    return client


@pytest.mark.asyncio
class TestSharePointConnector:
    """Test suite para SharePoint Connector"""
    
    async def test_initialization(self, sharepoint_config):
        """Test: Inicialización del conector"""
        connector = SharePointConnector(sharepoint_config)
        
        assert connector.config.tenant_id == "test-tenant-id"
        assert connector.config.client_id == "test-client-id"
        assert connector.config.name == "Test SharePoint"
        assert connector._authenticated == False
    
    @patch('backend.connectors.sharepoint_connector.ConfidentialClientApplication')
    @patch('backend.connectors.sharepoint_connector.ClientSecretCredential')
    @patch('backend.connectors.sharepoint_connector.GraphServiceClient')
    async def test_authenticate_success(
        self, 
        mock_graph_client_class,
        mock_credential_class,
        mock_msal_app_class,
        sharepoint_config
    ):
        """Test: Autenticación exitosa"""
        # Setup mocks
        mock_app = Mock()
        mock_app.acquire_token_for_client.return_value = {
            "access_token": "test-token",
            "expires_in": 3600
        }
        mock_msal_app_class.return_value = mock_app
        
        mock_credential = Mock()
        mock_credential_class.return_value = mock_credential
        
        mock_client = Mock()
        mock_graph_client_class.return_value = mock_client
        
        # Test
        connector = SharePointConnector(sharepoint_config)
        result = await connector.authenticate()
        
        assert result == True
        assert connector._authenticated == True
        assert connector._access_token == "test-token"
        assert connector.client is not None
        
        # Verify MSAL called correctly
        mock_msal_app_class.assert_called_once()
        mock_app.acquire_token_for_client.assert_called_once()
    
    @patch('backend.connectors.sharepoint_connector.ConfidentialClientApplication')
    async def test_authenticate_failure(
        self, 
        mock_msal_app_class,
        sharepoint_config
    ):
        """Test: Fallo en autenticación"""
        # Setup mock to return error
        mock_app = Mock()
        mock_app.acquire_token_for_client.return_value = {
            "error": "invalid_client",
            "error_description": "Invalid client credentials"
        }
        mock_msal_app_class.return_value = mock_app
        
        # Test
        connector = SharePointConnector(sharepoint_config)
        result = await connector.authenticate()
        
        assert result == False
        assert connector._authenticated == False
        assert connector._access_token is None
    
    async def test_test_connection(self, sharepoint_config, mock_graph_client):
        """Test: Probar conexión"""
        connector = SharePointConnector(sharepoint_config)
        connector.client = mock_graph_client
        connector._authenticated = True
        
        result = await connector.test_connection()
        
        assert result == True
        mock_graph_client.sites.get.assert_called_once()
    
    async def test_list_repositories(self, sharepoint_config, mock_graph_client):
        """Test: Listar sitios/repositorios"""
        connector = SharePointConnector(sharepoint_config)
        connector.client = mock_graph_client
        connector._authenticated = True
        
        repositories = await connector.list_repositories()
        
        assert len(repositories) == 1
        assert repositories[0]["id"] == "test-site-123"
        assert repositories[0]["name"] == "Corporate Documents"
        assert repositories[0]["type"] == "sharepoint_site"
        mock_graph_client.sites.get.assert_called()
    
    async def test_list_documents(self, sharepoint_config, mock_graph_client):
        """Test: Listar documentos"""
        connector = SharePointConnector(sharepoint_config)
        connector.client = mock_graph_client
        connector._authenticated = True
        
        documents = await connector.list_documents(
            repository_id="test-site-123",
            path="Shared Documents"
        )
        
        assert len(documents) == 1
        assert isinstance(documents[0], ConnectorDocument)
        assert documents[0].name == "test-document.pdf"
        assert documents[0].size == 1024
        assert documents[0].mime_type == "application/pdf"
    
    async def test_list_documents_with_filters(self, sharepoint_config, mock_graph_client):
        """Test: Listar documentos con filtros"""
        connector = SharePointConnector(sharepoint_config)
        connector.client = mock_graph_client
        connector._authenticated = True
        
        # Test filtro de tipo de archivo
        documents = await connector.list_documents(
            repository_id="test-site-123",
            filters={"file_types": [".pdf", ".docx"]}
        )
        
        assert len(documents) == 1
        
        # Test filtro que no coincide
        documents = await connector.list_documents(
            repository_id="test-site-123",
            filters={"file_types": [".xlsx"]}
        )
        
        # Should be filtered out
        assert len(documents) == 0
    
    async def test_get_document(self, sharepoint_config, mock_graph_client):
        """Test: Obtener documento específico"""
        connector = SharePointConnector(sharepoint_config)
        connector.client = mock_graph_client
        connector._authenticated = True
        
        document_id = "test-site-123|test-drive-123|test-item-123"
        document = await connector.get_document(document_id)
        
        assert isinstance(document, ConnectorDocument)
        assert document.name == "test-document.pdf"
        assert document.metadata["site_id"] == "test-site-123"
        assert document.metadata["drive_id"] == "test-drive-123"
    
    async def test_get_document_invalid_id(self, sharepoint_config, mock_graph_client):
        """Test: Get con ID inválido"""
        connector = SharePointConnector(sharepoint_config)
        connector.client = mock_graph_client
        connector._authenticated = True
        
        with pytest.raises(ValueError, match="Invalid document_id format"):
            await connector.get_document("invalid-id")
    
    async def test_download_document(self, sharepoint_config, mock_graph_client):
        """Test: Descargar documento"""
        connector = SharePointConnector(sharepoint_config)
        connector.client = mock_graph_client
        connector._authenticated = True
        
        document_id = "test-site-123|test-drive-123|test-item-123"
        content = await connector.download_document(document_id)
        
        assert content == b"Test PDF content"
        assert len(content) > 0
    
    async def test_map_metadata(self, sharepoint_config):
        """Test: Mapeo de metadata"""
        connector = SharePointConnector(sharepoint_config)
        
        source_metadata = {
            "site_id": "site-123",
            "site_name": "Corporate",
            "drive_id": "drive-456",
            "drive_name": "Documents",
            "item_id": "item-789",
            "url": "https://test.sharepoint.com/doc.pdf",
            "e_tag": "etag-abc"
        }
        
        mapped = connector._map_metadata(source_metadata)
        
        assert mapped["source"] == "sharepoint"
        assert mapped["sharepoint_site_id"] == "site-123"
        assert mapped["sharepoint_drive_id"] == "drive-456"
        assert mapped["sharepoint_url"] == "https://test.sharepoint.com/doc.pdf"
    
    async def test_not_authenticated_raises_error(self, sharepoint_config):
        """Test: Operaciones sin autenticación fallan"""
        connector = SharePointConnector(sharepoint_config)
        # No autenticar
        
        with pytest.raises(Exception, match="Not authenticated"):
            await connector.list_repositories()


@pytest.mark.asyncio
class TestSharePointConnectorIntegration:
    """Tests de integración (requieren credenciales reales)"""
    
    @pytest.mark.skipif(
        not os.getenv("SHAREPOINT_TENANT_ID"),
        reason="SharePoint credentials not configured"
    )
    async def test_real_authentication(self):
        """Test: Autenticación real con SharePoint"""
        config = SharePointConfig(
            enabled=True,
            name="Real SharePoint",
            type="sharepoint",
            tenant_id=os.getenv("SHAREPOINT_TENANT_ID"),
            client_id=os.getenv("SHAREPOINT_CLIENT_ID"),
            client_secret=os.getenv("SHAREPOINT_CLIENT_SECRET")
        )
        
        async with SharePointConnector(config) as connector:
            # Test connection
            result = await connector.test_connection()
            assert result == True
            
            # List sites
            sites = await connector.list_repositories()
            assert len(sites) > 0
            
            print(f"Found {len(sites)} sites")
            for site in sites[:3]:  # Print first 3
                print(f"  - {site['name']}: {site['url']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
