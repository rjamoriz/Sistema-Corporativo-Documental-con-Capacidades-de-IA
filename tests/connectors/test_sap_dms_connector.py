"""
Tests for SAP DMS Connector

Estos tests verifican la funcionalidad del conector SAP DMS,
incluyendo autenticación, listado de repositorios, búsqueda, descarga, etc.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from backend.connectors.sap_dms_connector import (
    SAPDMSConnector,
    SAPDMSConfig,
    ConnectorDocument
)


@pytest.fixture
def sap_config():
    """Configuración de prueba para SAP DMS"""
    return SAPDMSConfig(
        enabled=True,
        name="Test SAP DMS",
        type="sap_dms",
        url="https://sap-test.company.com",
        auth_type="basic",
        username="test_user",
        password="test_password",
        client="100",
        repositories=[
            {
                "id": "FI_DOCUMENTS",
                "name": "Financial Documents",
                "sync_filters": {
                    "status": ["active", "approved"],
                    "document_type": ["INVOICE", "CONTRACT"]
                }
            }
        ]
    )


@pytest.fixture
def mock_sap_session():
    """Mock de requests.Session para SAP"""
    session = Mock()
    
    # Mock response exitoso para auth
    auth_response = Mock()
    auth_response.status_code = 200
    auth_response.json.return_value = {"d": {"results": []}}
    
    # Mock para listar repositorios
    repos_response = Mock()
    repos_response.status_code = 200
    repos_response.json.return_value = {
        "d": {
            "results": [
                {
                    "RepositoryId": "FI_DOCUMENTS",
                    "RepositoryName": "Financial Documents",
                    "Description": "Financial documents repository"
                }
            ]
        }
    }
    
    # Mock para buscar documentos
    docs_response = Mock()
    docs_response.status_code = 200
    docs_response.json.return_value = {
        "d": {
            "results": [
                {
                    "DOKNR": "DOC001",
                    "DOKAR": "INVOICE",
                    "DOKVR": "01",
                    "DOKTL": "000",
                    "DOKST": "active",
                    "ERNAM": "TESTUSER",
                    "ERDAT": "20240101",
                    "AENAM": "TESTUSER",
                    "AEDAT": "20240115",
                    "DKTXT": "Test Invoice.pdf",
                    "MIMETYPE": "application/pdf",
                    "FILE_SIZE": 1024
                }
            ]
        }
    }
    
    # Mock para obtener documento específico
    doc_response = Mock()
    doc_response.status_code = 200
    doc_response.json.return_value = {
        "d": {
            "DOKNR": "DOC001",
            "DOKAR": "INVOICE",
            "DOKVR": "01",
            "DOKTL": "000",
            "DOKST": "active",
            "ERNAM": "TESTUSER",
            "ERDAT": "20240101",
            "DKTXT": "Test Invoice.pdf",
            "MIMETYPE": "application/pdf",
            "FILE_SIZE": 1024
        }
    }
    
    # Mock para descargar contenido
    content_response = Mock()
    content_response.status_code = 200
    content_response.content = b"PDF content here"
    
    # Mock para upload
    upload_response = Mock()
    upload_response.status_code = 201
    upload_response.json.return_value = {
        "d": {
            "DocumentNumber": "DOC002",
            "DocumentType": "DWS",
            "DocumentVersion": "01",
            "DocumentPart": "000"
        }
    }
    
    # Configurar session.get para devolver respuestas según URL
    def side_effect_get(url, *args, **kwargs):
        if "Repositories" in url:
            return repos_response
        elif "Documents(" in url and "$value" in url:
            return content_response
        elif "Documents(" in url:
            return doc_response
        elif "Documents" in url:
            return docs_response
        else:
            return auth_response
    
    session.get.side_effect = side_effect_get
    session.post.return_value = upload_response
    session.put.return_value = Mock(status_code=204)
    
    return session


@pytest.mark.asyncio
class TestSAPDMSConnector:
    """Test suite para SAP DMS Connector"""
    
    async def test_initialization(self, sap_config):
        """Test: Inicialización del conector"""
        connector = SAPDMSConnector(sap_config)
        
        assert connector.config.url == "https://sap-test.company.com"
        assert connector.config.username == "test_user"
        assert connector.config.auth_type == "basic"
        assert connector._authenticated == False
        assert len(connector.SAP_TO_FINANCIA_MAPPING) > 0
    
    @patch('backend.connectors.sap_dms_connector.requests.Session')
    async def test_authenticate_success(self, mock_session_class, sap_config, mock_sap_session):
        """Test: Autenticación básica exitosa"""
        mock_session_class.return_value = mock_sap_session
        
        connector = SAPDMSConnector(sap_config)
        result = await connector.authenticate()
        
        assert result == True
        assert connector._authenticated == True
        assert connector.session is not None
        
        # Verificar que se configuró auth básica
        mock_sap_session.get.assert_called()
    
    @patch('backend.connectors.sap_dms_connector.requests.Session')
    async def test_authenticate_invalid_credentials(self, mock_session_class, sap_config):
        """Test: Autenticación con credenciales inválidas"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        connector = SAPDMSConnector(sap_config)
        result = await connector.authenticate()
        
        assert result == False
        assert connector._authenticated == False
    
    async def test_list_repositories_from_config(self, sap_config):
        """Test: Listar repositorios desde configuración"""
        connector = SAPDMSConnector(sap_config)
        connector.session = Mock()  # Mock session
        
        repos = await connector.list_repositories()
        
        assert len(repos) == 1
        assert repos[0]["id"] == "FI_DOCUMENTS"
        assert repos[0]["name"] == "Financial Documents"
        assert repos[0]["type"] == "sap_dms_repository"
    
    async def test_search_documents(self, sap_config, mock_sap_session):
        """Test: Buscar documentos con filtros"""
        connector = SAPDMSConnector(sap_config)
        connector.session = mock_sap_session
        
        documents = await connector.search_documents(
            repository_id="FI_DOCUMENTS",
            filters={
                "status": ["active"],
                "document_type": ["INVOICE"]
            }
        )
        
        assert len(documents) == 1
        assert isinstance(documents[0], ConnectorDocument)
        assert documents[0].name == "Test Invoice.pdf"
        assert documents[0].mime_type == "application/pdf"
        assert "sap_document_number" in documents[0].metadata
    
    async def test_list_documents(self, sap_config, mock_sap_session):
        """Test: Listar documentos (alias de search)"""
        connector = SAPDMSConnector(sap_config)
        connector.session = mock_sap_session
        
        documents = await connector.list_documents(
            repository_id="FI_DOCUMENTS",
            filters={"status": ["active"]}
        )
        
        assert len(documents) == 1
        assert documents[0].name == "Test Invoice.pdf"
    
    async def test_parse_sap_document(self, sap_config):
        """Test: Parsear documento SAP a ConnectorDocument"""
        connector = SAPDMSConnector(sap_config)
        
        sap_doc = {
            "DOKNR": "DOC001",
            "DOKAR": "INVOICE",
            "DOKVR": "01",
            "DOKTL": "000",
            "DOKST": "active",
            "ERNAM": "TESTUSER",
            "ERDAT": "20240101",
            "AENAM": "TESTUSER",
            "AEDAT": "20240115",
            "DKTXT": "Invoice.pdf",
            "MIMETYPE": "application/pdf",
            "FILE_SIZE": 2048
        }
        
        doc = connector._parse_sap_document(sap_doc, "FI_DOCUMENTS")
        
        assert doc.name == "Invoice.pdf"
        assert doc.size == 2048
        assert doc.mime_type == "application/pdf"
        assert doc.created_by == "TESTUSER"
        assert doc.metadata["sap_document_number"] == "DOC001"
        assert doc.metadata["sap_document_type"] == "INVOICE"
        assert doc.metadata["sap_status"] == "active"
    
    async def test_parse_sap_date(self, sap_config):
        """Test: Parsear fechas SAP"""
        connector = SAPDMSConnector(sap_config)
        
        # Fecha válida
        date = connector._parse_sap_date("20240115")
        assert date.year == 2024
        assert date.month == 1
        assert date.day == 15
        
        # Fecha vacía
        date = connector._parse_sap_date(None)
        assert isinstance(date, datetime)
        
        # Fecha inválida
        date = connector._parse_sap_date("invalid")
        assert isinstance(date, datetime)
    
    async def test_get_document(self, sap_config, mock_sap_session):
        """Test: Obtener documento específico"""
        connector = SAPDMSConnector(sap_config)
        connector.session = mock_sap_session
        
        document_id = "FI_DOCUMENTS|INVOICE|DOC001|01|000"
        doc = await connector.get_document(document_id)
        
        assert isinstance(doc, ConnectorDocument)
        assert doc.name == "Test Invoice.pdf"
        assert doc.metadata["sap_document_number"] == "DOC001"
    
    async def test_get_document_invalid_id(self, sap_config, mock_sap_session):
        """Test: Get con ID inválido"""
        connector = SAPDMSConnector(sap_config)
        connector.session = mock_sap_session
        
        with pytest.raises(ValueError, match="Invalid document_id format"):
            await connector.get_document("invalid-id")
    
    async def test_download_document(self, sap_config, mock_sap_session):
        """Test: Descargar contenido de documento"""
        connector = SAPDMSConnector(sap_config)
        connector.session = mock_sap_session
        
        document_id = "FI_DOCUMENTS|INVOICE|DOC001|01|000"
        content = await connector.download_document(document_id)
        
        assert content == b"PDF content here"
        assert len(content) > 0
    
    async def test_upload_document(self, sap_config, mock_sap_session):
        """Test: Subir documento a SAP"""
        connector = SAPDMSConnector(sap_config)
        connector.session = mock_sap_session
        
        # Mock get_document para después del upload
        async def mock_get_doc(doc_id):
            return ConnectorDocument(
                id=doc_id,
                name="uploaded.pdf",
                size=1024,
                mime_type="application/pdf",
                created_at=datetime.now(),
                modified_at=datetime.now(),
                metadata={"sap_document_number": "DOC002"}
            )
        
        connector.get_document = mock_get_doc
        
        content = b"Test document content"
        doc = await connector.upload_document(
            repository_id="FI_DOCUMENTS",
            filename="uploaded.pdf",
            content=content,
            metadata={"DOKAR": "DWS", "DKTXT": "Test upload"}
        )
        
        assert isinstance(doc, ConnectorDocument)
        assert doc.name == "uploaded.pdf"
        
        # Verificar que se llamó a post y put
        mock_sap_session.post.assert_called()
        mock_sap_session.put.assert_called()
    
    async def test_map_metadata(self, sap_config):
        """Test: Mapeo de metadata SAP a FinancIA"""
        connector = SAPDMSConnector(sap_config)
        
        source_metadata = {
            "repository_id": "FI_DOCUMENTS",
            "sap_document_number": "DOC001",
            "sap_document_type": "INVOICE",
            "sap_status": "active",
            "sap_created_by": "TESTUSER"
        }
        
        mapped = connector._map_metadata(source_metadata)
        
        assert mapped["source"] == "sap_dms"
        assert mapped["sap_repository"] == "FI_DOCUMENTS"
        assert mapped["sap_document_number"] == "DOC001"
        assert mapped["sap_status"] == "active"
    
    async def test_not_authenticated_raises_error(self, sap_config):
        """Test: Operaciones sin autenticación fallan"""
        connector = SAPDMSConnector(sap_config)
        # No autenticar
        
        with pytest.raises(Exception, match="Not authenticated"):
            await connector.search_documents("FI_DOCUMENTS")
    
    async def test_oauth2_not_implemented(self, sap_config):
        """Test: OAuth2 aún no implementado"""
        sap_config.auth_type = "oauth2"
        connector = SAPDMSConnector(sap_config)
        
        with pytest.raises(NotImplementedError):
            await connector.authenticate()


@pytest.mark.asyncio
class TestSAPDMSConnectorIntegration:
    """Tests de integración (requieren SAP real)"""
    
    @pytest.mark.skipif(
        not os.getenv("SAP_DMS_URL"),
        reason="SAP DMS credentials not configured"
    )
    async def test_real_authentication(self):
        """Test: Autenticación real con SAP DMS"""
        config = SAPDMSConfig(
            enabled=True,
            name="Real SAP DMS",
            type="sap_dms",
            url=os.getenv("SAP_DMS_URL"),
            username=os.getenv("SAP_USERNAME"),
            password=os.getenv("SAP_PASSWORD"),
            client=os.getenv("SAP_CLIENT", "100")
        )
        
        async with SAPDMSConnector(config) as connector:
            # Test connection
            result = await connector.test_connection()
            assert result == True
            
            # List repositories
            repos = await connector.list_repositories()
            print(f"Found {len(repos)} repositories")
            
            if repos:
                # Search documents in first repo
                docs = await connector.search_documents(
                    repos[0]["id"],
                    filters={"status": ["active"]}
                )
                print(f"Found {len(docs)} documents in {repos[0]['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
