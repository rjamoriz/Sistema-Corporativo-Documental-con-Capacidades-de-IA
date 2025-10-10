"""
Tests para el Servidor MCP de Ontología TEFinancia

Prueba las 8 herramientas MCP expuestas a Claude Desktop
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Añadir directorios al path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))
sys.path.insert(0, str(root_path / "backend"))


@pytest.fixture
def mock_ontology_service():
    """Mock del servicio de ontología"""
    with patch('mcp_server.ontology_service') as mock:
        # Configurar TF namespace
        mock.TF = {
            "PrestamoHipotecario": "http://www.tefinancia.com/ontology#PrestamoHipotecario",
            "TarjetaCredito": "http://www.tefinancia.com/ontology#TarjetaCredito"
        }
        yield mock


@pytest.fixture
def mock_taxonomy_service():
    """Mock del servicio de taxonomía"""
    with patch('mcp_server.taxonomy_service') as mock:
        yield mock


class TestMCPToolGetOntologyClasses:
    """Tests de la herramienta get_ontology_classes"""
    
    @pytest.mark.asyncio
    async def test_get_all_classes_without_properties(self, mock_ontology_service):
        """
        Debe listar todas las clases sin propiedades
        """
        mock_ontology_service.get_all_classes.return_value = {
            "http://example.com/PrestamoHipotecario": {
                "name": "PrestamoHipotecario",
                "label": "Préstamo Hipotecario",
                "comment": "Préstamo garantizado con hipoteca",
                "parent_classes": ["http://example.com/Prestamo"],
                "properties": []
            }
        }
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="get_ontology_classes",
            arguments={"include_properties": False}
        )
        
        # Verificar resultado
        assert len(result) == 1
        assert result[0].type == "text"
        
        data = json.loads(result[0].text)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]
        assert "label" in data[0]
    
    @pytest.mark.asyncio
    async def test_get_all_classes_with_properties(self, mock_ontology_service):
        """
        Debe listar clases con propiedades incluidas
        """
        mock_ontology_service.get_all_classes.return_value = {
            "http://example.com/PrestamoHipotecario": {
                "name": "PrestamoHipotecario",
                "label": "Préstamo Hipotecario",
                "comment": "Préstamo garantizado con hipoteca",
                "parent_classes": [],
                "properties": [
                    {
                        "name": "importeFinanciado",
                        "label": "Importe Financiado",
                        "type": "DatatypeProperty"
                    }
                ]
            }
        }
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="get_ontology_classes",
            arguments={"include_properties": True}
        )
        
        data = json.loads(result[0].text)
        assert "properties" in data[0]
        assert len(data[0]["properties"]) > 0


class TestMCPToolGetClassDetails:
    """Tests de la herramienta get_class_details"""
    
    @pytest.mark.asyncio
    async def test_get_details_of_existing_class(self, mock_ontology_service):
        """
        Debe obtener detalles completos de una clase existente
        """
        mock_ontology_service.get_class_info.return_value = {
            "label": "Préstamo Hipotecario",
            "comment": "Préstamo garantizado con hipoteca sobre inmueble",
            "parent_classes": ["http://example.com/Prestamo"],
            "subclasses": [],
            "properties": [
                {
                    "name": "importeFinanciado",
                    "label": "Importe Financiado",
                    "type": "DatatypeProperty"
                }
            ]
        }
        
        mock_ontology_service.get_class_restrictions.return_value = [
            {
                "property": "importeFinanciado",
                "type": "MinInclusive",
                "value": 30000
            }
        ]
        
        mock_ontology_service.get_required_fields.return_value = ["tieneCliente"]
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="get_class_details",
            arguments={"class_name": "PrestamoHipotecario"}
        )
        
        data = json.loads(result[0].text)
        assert data["name"] == "PrestamoHipotecario"
        assert data["label"] == "Préstamo Hipotecario"
        assert "properties" in data
        assert "restrictions" in data
        assert "required_fields" in data


class TestMCPToolExecuteSPARQL:
    """Tests de la herramienta execute_sparql"""
    
    @pytest.mark.asyncio
    async def test_execute_simple_sparql_query(self, mock_ontology_service):
        """
        Debe ejecutar consulta SPARQL simple
        """
        mock_ontology_service.execute_sparql.return_value = {
            "columns": ["class", "label"],
            "rows": [
                {"class": "PrestamoHipotecario", "label": "Préstamo Hipotecario"},
                {"class": "TarjetaCredito", "label": "Tarjeta de Crédito"}
            ]
        }
        
        from mcp_server import handle_call_tool
        
        query = """
        SELECT ?class ?label
        WHERE {
            ?class rdfs:label ?label .
        }
        """
        
        result = await handle_call_tool(
            name="execute_sparql",
            arguments={"query": query, "limit": 100}
        )
        
        data = json.loads(result[0].text)
        assert "columns" in data
        assert "rows" in data
        assert "count" in data
        assert len(data["rows"]) == 2
    
    @pytest.mark.asyncio
    async def test_execute_sparql_adds_limit_if_missing(self, mock_ontology_service):
        """
        Debe añadir LIMIT si no existe en la query
        """
        mock_ontology_service.execute_sparql.return_value = {
            "columns": ["class"],
            "rows": []
        }
        
        from mcp_server import handle_call_tool
        
        query = "SELECT ?class WHERE { ?class rdf:type owl:Class }"
        
        await handle_call_tool(
            name="execute_sparql",
            arguments={"query": query, "limit": 50}
        )
        
        # Verificar que se llamó con LIMIT añadido
        called_query = mock_ontology_service.execute_sparql.call_args[0][0]
        assert "LIMIT" in called_query.upper()


class TestMCPToolClassifyDocument:
    """Tests de la herramienta classify_document"""
    
    @pytest.mark.asyncio
    async def test_classify_document_with_ontology(self, mock_ontology_service):
        """
        Debe clasificar documento usando ontología
        """
        mock_ontology_service.classify_document.return_value = {
            "class_name": "PrestamoHipotecario",
            "class_label": "Préstamo Hipotecario",
            "confidence": 0.93,
            "matched_keywords": ["préstamo hipotecario", "hipoteca"],
            "method": "ontology_keywords"
        }
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="classify_document",
            arguments={
                "content": "Contrato de préstamo hipotecario para vivienda...",
                "metadata": {"importeFinanciado": 250000}
            }
        )
        
        data = json.loads(result[0].text)
        assert data["class_name"] == "PrestamoHipotecario"
        assert data["confidence"] > 0.9
        assert "matched_keywords" in data


class TestMCPToolValidateMetadata:
    """Tests de la herramienta validate_metadata"""
    
    @pytest.mark.asyncio
    async def test_validate_valid_metadata(self, mock_ontology_service):
        """
        Debe validar metadatos correctos
        """
        mock_ontology_service.validate_metadata.return_value = (True, [])
        mock_ontology_service.get_required_fields.return_value = ["tieneCliente"]
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="validate_metadata",
            arguments={
                "class_name": "PrestamoHipotecario",
                "metadata": {
                    "importeFinanciado": 250000,
                    "ltv": 75,
                    "tieneCliente": True
                }
            }
        )
        
        data = json.loads(result[0].text)
        assert data["is_valid"] is True
        assert len(data["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_validate_invalid_metadata(self, mock_ontology_service):
        """
        Debe detectar metadatos inválidos
        """
        mock_ontology_service.validate_metadata.return_value = (
            False,
            ["importeFinanciado debe ser >= 30000", "ltv debe ser <= 100"]
        )
        mock_ontology_service.get_required_fields.return_value = ["tieneCliente"]
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="validate_metadata",
            arguments={
                "class_name": "PrestamoHipotecario",
                "metadata": {
                    "importeFinanciado": 20000,  # Inválido
                    "ltv": 150  # Inválido
                }
            }
        )
        
        data = json.loads(result[0].text)
        assert data["is_valid"] is False
        assert len(data["errors"]) == 2


class TestMCPToolInferRiskLevel:
    """Tests de la herramienta infer_risk_level"""
    
    @pytest.mark.asyncio
    async def test_infer_high_risk(self, mock_ontology_service):
        """
        Debe inferir riesgo ALTO con LTV > 80%
        """
        mock_ontology_service.infer_risk_level.return_value = "ALTO"
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="infer_risk_level",
            arguments={
                "class_name": "PrestamoHipotecario",
                "metadata": {
                    "ltv": 85,  # > 80% → ALTO
                    "tae": 3.5
                }
            }
        )
        
        data = json.loads(result[0].text)
        assert data["risk_level"] == "ALTO"
    
    @pytest.mark.asyncio
    async def test_infer_low_risk(self, mock_ontology_service):
        """
        Debe inferir riesgo BAJO con condiciones normales
        """
        mock_ontology_service.infer_risk_level.return_value = "BAJO"
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="infer_risk_level",
            arguments={
                "class_name": "PrestamoHipotecario",
                "metadata": {
                    "ltv": 70,  # < 80%
                    "tae": 3.5  # < 10%
                }
            }
        )
        
        data = json.loads(result[0].text)
        assert data["risk_level"] == "BAJO"


class TestMCPToolGetOntologyHierarchy:
    """Tests de la herramienta get_ontology_hierarchy"""
    
    @pytest.mark.asyncio
    async def test_get_hierarchy_from_root(self, mock_ontology_service):
        """
        Debe obtener jerarquía completa desde raíz
        """
        mock_ontology_service.get_hierarchy.return_value = {
            "class_info": {
                "name": "DocumentoCorporativo",
                "label": "Documento Corporativo"
            },
            "children": [
                {
                    "class_info": {
                        "name": "ProductoFinanciero",
                        "label": "Producto Financiero"
                    },
                    "children": []
                }
            ]
        }
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="get_ontology_hierarchy",
            arguments={"root_class": "DocumentoCorporativo"}
        )
        
        data = json.loads(result[0].text)
        assert "class_info" in data
        assert "children" in data
        assert data["class_info"]["name"] == "DocumentoCorporativo"


class TestMCPToolSearchByKeywords:
    """Tests de la herramienta search_by_keywords"""
    
    @pytest.mark.asyncio
    async def test_search_finds_matching_class(self, mock_taxonomy_service):
        """
        Debe encontrar clase por keywords
        """
        mock_taxonomy_service.classify_by_keywords.return_value = {
            "class_id": "PrestamoHipotecario",
            "class_label": "Préstamo Hipotecario",
            "confidence": 0.85,
            "path": ["ProductoFinanciero", "Prestamo", "PrestamoHipotecario"],
            "matched_keywords": ["hipoteca", "préstamo"]
        }
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="search_by_keywords",
            arguments={"text": "Contrato de hipoteca para vivienda"}
        )
        
        data = json.loads(result[0].text)
        assert data["class_id"] == "PrestamoHipotecario"
        assert data["confidence"] > 0.8
        assert "matched_keywords" in data


class TestMCPErrorHandling:
    """Tests de manejo de errores del servidor MCP"""
    
    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self):
        """
        Herramienta desconocida debe retornar error
        """
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="unknown_tool",
            arguments={}
        )
        
        assert len(result) == 1
        assert "Error" in result[0].text or "desconocida" in result[0].text
    
    @pytest.mark.asyncio
    async def test_exception_in_tool_returns_error(self, mock_ontology_service):
        """
        Excepción en herramienta debe retornar error
        """
        mock_ontology_service.get_all_classes.side_effect = Exception("Test error")
        
        from mcp_server import handle_call_tool
        
        result = await handle_call_tool(
            name="get_ontology_classes",
            arguments={}
        )
        
        assert len(result) == 1
        assert "Error" in result[0].text


class TestMCPIntegration:
    """Tests de integración del servidor MCP"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_classify_validate_risk(
        self, mock_ontology_service, mock_taxonomy_service
    ):
        """
        Workflow completo: clasificar → validar → inferir riesgo
        """
        # Setup mocks
        mock_ontology_service.classify_document.return_value = {
            "class_name": "PrestamoHipotecario",
            "class_label": "Préstamo Hipotecario",
            "confidence": 0.93,
            "matched_keywords": ["préstamo hipotecario"]
        }
        
        mock_ontology_service.validate_metadata.return_value = (True, [])
        mock_ontology_service.get_required_fields.return_value = ["tieneCliente"]
        mock_ontology_service.infer_risk_level.return_value = "BAJO"
        
        from mcp_server import handle_call_tool
        
        # Paso 1: Clasificar
        classify_result = await handle_call_tool(
            name="classify_document",
            arguments={
                "content": "Contrato de préstamo hipotecario...",
                "metadata": {"importeFinanciado": 250000}
            }
        )
        classify_data = json.loads(classify_result[0].text)
        class_name = classify_data["class_name"]
        
        # Paso 2: Validar
        validate_result = await handle_call_tool(
            name="validate_metadata",
            arguments={
                "class_name": class_name,
                "metadata": {"importeFinanciado": 250000, "ltv": 75}
            }
        )
        validate_data = json.loads(validate_result[0].text)
        
        # Paso 3: Inferir riesgo
        risk_result = await handle_call_tool(
            name="infer_risk_level",
            arguments={
                "class_name": class_name,
                "metadata": {"ltv": 75, "tae": 3.5}
            }
        )
        risk_data = json.loads(risk_result[0].text)
        
        # Verificaciones del workflow completo
        assert class_name == "PrestamoHipotecario"
        assert validate_data["is_valid"] is True
        assert risk_data["risk_level"] == "BAJO"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
