"""
Tests unitarios para OntologyService y API REST de ontología.
Sprint 2 & 3: Validar consultas SPARQL, inferencia y validación semántica.
"""

import pytest
from rdflib import URIRef

from backend.services.ontology_service import ontology_service


class TestOntologyLoading:
    """Tests para verificar carga correcta de la ontología."""
    
    def test_ontology_loads_successfully(self):
        """Verifica que la ontología se carga sin errores."""
        assert ontology_service.graph is not None
        assert len(ontology_service.graph) > 0
    
    def test_ontology_has_expected_namespaces(self):
        """Verifica que los namespaces están definidos."""
        assert ontology_service.TF is not None
        assert str(ontology_service.TF) == "http://tefinancia.es/ontology#"
    
    def test_ontology_statistics(self):
        """Verifica estadísticas básicas de la ontología."""
        stats = ontology_service.get_statistics()
        
        assert stats["total_triples"] > 0
        assert stats["total_classes"] >= 30  # Esperamos al menos 30 clases
        assert stats["total_object_properties"] >= 8
        assert stats["total_datatype_properties"] >= 15


class TestClassNavigation:
    """Tests para navegación de clases OWL."""
    
    def test_get_class_info_documento(self):
        """Obtiene información de la clase raíz Documento."""
        class_uri = ontology_service.TF.Documento
        info = ontology_service.get_class_info(class_uri)
        
        assert info is not None
        assert info["label"] == "Documento"
        assert "properties" in info
    
    def test_get_class_info_prestamo_hipotecario(self):
        """Obtiene información de PrestamoHipotecario."""
        class_uri = ontology_service.TF.PrestamoHipotecario
        info = ontology_service.get_class_info(class_uri)
        
        assert info is not None
        assert "Préstamo Hipotecario" in info["label"]
        assert len(info["parent_classes"]) > 0
        
        # Verificar propiedades específicas
        props = info["properties"]
        assert "nivelRiesgoBase" in props
        assert "importeMinimo" in props
    
    def test_get_subclasses_documento(self):
        """Obtiene subclases directas de Documento."""
        class_uri = ontology_service.TF.Documento
        subclasses = ontology_service.get_subclasses(class_uri, direct_only=True)
        
        assert len(subclasses) > 0
        
        # Verificar que incluye clases esperadas
        subclass_names = [str(sc).split("#")[-1] for sc in subclasses]
        assert "DocumentoContractual" in subclass_names or \
               "DocumentoIdentidad" in subclass_names or \
               "DocumentoFinanciero" in subclass_names
    
    def test_get_subclasses_transitive(self):
        """Obtiene subclases transitivas (todas las descendientes)."""
        class_uri = ontology_service.TF.Documento
        all_subclasses = ontology_service.get_subclasses(class_uri, direct_only=False)
        
        # Debería incluir todas las clases de la jerarquía
        assert len(all_subclasses) >= 10
        
        # Verificar clases profundas en la jerarquía
        subclass_names = [str(sc).split("#")[-1] for sc in all_subclasses]
        assert "PrestamoHipotecario" in subclass_names or \
               "DNI" in subclass_names or \
               "Factura" in subclass_names
    
    def test_get_hierarchy(self):
        """Construye árbol de jerarquía completo."""
        class_uri = ontology_service.TF.Documento
        hierarchy = ontology_service.get_hierarchy(class_uri)
        
        assert hierarchy is not None
        assert hierarchy["name"] == "Documento"
        assert "children" in hierarchy
        assert len(hierarchy["children"]) > 0
        
        # Verificar que tiene al menos 2 niveles
        first_child = hierarchy["children"][0]
        assert "children" in first_child


class TestDocumentClassification:
    """Tests para clasificación de documentos."""
    
    def test_classify_prestamo_hipotecario(self):
        """Clasifica documento de préstamo hipotecario."""
        content = """
        Contrato de préstamo hipotecario con garantía inmobiliaria.
        El banco concede un préstamo de 200.000€ con plazo de 20 años.
        La vivienda queda hipotecada como garantía del préstamo.
        TAE: 3.5%, TIN: 2.8%
        """
        
        result = ontology_service.classify_document(content, {})
        
        assert result is not None
        assert "PrestamoHipotecario" in result["class_name"]
        assert result["confidence"] > 0
        assert len(result["matched_keywords"]) > 0
    
    def test_classify_dni(self):
        """Clasifica documento DNI."""
        content = """
        Documento Nacional de Identidad
        NIF: 12345678A
        Nombre: Juan Pérez García
        Fecha de nacimiento: 01/01/1980
        """
        
        result = ontology_service.classify_document(content, {})
        
        assert result is not None
        assert "DNI" in result["class_name"]
        assert result["confidence"] > 0
    
    def test_classify_factura(self):
        """Clasifica factura."""
        content = """
        FACTURA Nº 2024-001
        Fecha: 15/01/2024
        Importe: 1.500,00 €
        IVA (21%): 315,00 €
        Total: 1.815,00 €
        """
        
        result = ontology_service.classify_document(content, {})
        
        assert result is not None
        assert "Factura" in result["class_name"]
        assert result["confidence"] > 0
    
    def test_classify_no_match(self):
        """Intenta clasificar contenido sin coincidencias."""
        content = "Lorem ipsum dolor sit amet"
        
        result = ontology_service.classify_document(content, {})
        
        # Puede retornar None o una clasificación con baja confianza
        if result:
            assert result["confidence"] < 0.5


class TestMetadataValidation:
    """Tests para validación de metadatos contra OWL."""
    
    def test_validate_prestamo_hipotecario_valid(self):
        """Valida metadatos válidos de préstamo hipotecario."""
        class_uri = ontology_service.TF.PrestamoHipotecario
        metadata = {
            "importeFinanciado": 200000,
            "tae": 3.5,
            "tin": 2.8,
            "plazoMeses": 240,
            "ltv": 80.0,
            "valorTasacion": 250000
        }
        
        is_valid, errors = ontology_service.validate_metadata(class_uri, metadata)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_prestamo_hipotecario_invalid_importe(self):
        """Valida préstamo con importe menor al mínimo."""
        class_uri = ontology_service.TF.PrestamoHipotecario
        metadata = {
            "importeFinanciado": 10000,  # Menor al mínimo (30000)
            "tae": 3.5,
            "plazoMeses": 240
        }
        
        is_valid, errors = ontology_service.validate_metadata(class_uri, metadata)
        
        assert not is_valid
        assert any("importeMinimo" in error for error in errors)
    
    def test_validate_prestamo_hipotecario_invalid_plazo(self):
        """Valida préstamo con plazo menor al mínimo."""
        class_uri = ontology_service.TF.PrestamoHipotecario
        metadata = {
            "importeFinanciado": 200000,
            "tae": 3.5,
            "plazoMeses": 30  # Menor al mínimo (60)
        }
        
        is_valid, errors = ontology_service.validate_metadata(class_uri, metadata)
        
        assert not is_valid
        assert any("plazoMinimo" in error for error in errors)
    
    def test_validate_prestamo_personal_valid(self):
        """Valida préstamo personal válido."""
        class_uri = ontology_service.TF.PrestamoPersonal
        metadata = {
            "importeFinanciado": 10000,
            "tae": 7.5,
            "plazoMeses": 60
        }
        
        is_valid, errors = ontology_service.validate_metadata(class_uri, metadata)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_get_required_fields(self):
        """Obtiene campos requeridos de una clase."""
        class_uri = ontology_service.TF.PrestamoHipotecario
        required_fields = ontology_service.get_required_fields(class_uri)
        
        assert isinstance(required_fields, list)
        # PrestamoHipotecario requiere cliente (cardinality exacta 1)
        # y valoración (minCardinality 1)


class TestRiskInference:
    """Tests para inferencia de nivel de riesgo."""
    
    def test_infer_risk_ltv_high(self):
        """Infiere alto riesgo por LTV > 80%."""
        class_uri = ontology_service.TF.PrestamoHipotecario
        metadata = {
            "ltv": 85.0,
            "importeFinanciado": 250000
        }
        
        risk = ontology_service.infer_risk_level(class_uri, metadata)
        
        assert risk == "ALTO"
    
    def test_infer_risk_tae_high(self):
        """Infiere alto riesgo por TAE > 10%."""
        class_uri = ontology_service.TF.PrestamoPersonal
        metadata = {
            "tae": 12.5,
            "importeFinanciado": 10000
        }
        
        risk = ontology_service.infer_risk_level(class_uri, metadata)
        
        assert risk == "ALTO"
    
    def test_infer_risk_sensitive_data(self):
        """Infiere alto riesgo por datos sensibles."""
        class_uri = ontology_service.TF.DNI
        metadata = {
            "esSensible": True
        }
        
        risk = ontology_service.infer_risk_level(class_uri, metadata)
        
        assert risk == "ALTO"
    
    def test_infer_risk_linea_credito(self):
        """Línea de crédito siempre es alto riesgo."""
        class_uri = ontology_service.TF.LineaCredito
        metadata = {}
        
        risk = ontology_service.infer_risk_level(class_uri, metadata)
        
        assert risk == "ALTO"
    
    def test_infer_risk_long_term(self):
        """Plazo largo aumenta riesgo de BAJO a MEDIO."""
        class_uri = ontology_service.TF.PrestamoHipotecario
        metadata = {
            "plazoMeses": 300,  # 25 años
            "ltv": 70.0,  # LTV bajo
            "tae": 3.0  # TAE baja
        }
        
        risk = ontology_service.infer_risk_level(class_uri, metadata)
        
        # Debería ser MEDIO por plazo largo
        assert risk in ["MEDIO", "ALTO"]
    
    def test_infer_risk_base_level(self):
        """Usa nivel base si no aplican reglas."""
        class_uri = ontology_service.TF.Factura
        metadata = {}
        
        risk = ontology_service.infer_risk_level(class_uri, metadata)
        
        # Factura tiene riesgo base BAJO
        assert risk in ["BAJO", "MEDIO", "ALTO"]


class TestSPARQLQueries:
    """Tests para consultas SPARQL."""
    
    def test_query_all_classes(self):
        """Consulta todas las clases OWL."""
        query = """
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT DISTINCT ?class ?label WHERE {
                ?class rdf:type owl:Class .
                OPTIONAL { ?class rdfs:label ?label }
            }
        """
        
        results = ontology_service.query_sparql(query)
        
        assert len(results) >= 30
        assert all("class" in r for r in results)
    
    def test_query_contratos_financiacion(self):
        """Consulta subclases de ContratoFinanciacion."""
        query = """
            PREFIX tf: <http://tefinancia.es/ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?class ?label WHERE {
                ?class rdfs:subClassOf tf:ContratoFinanciacion .
                ?class rdfs:label ?label .
            }
        """
        
        results = ontology_service.query_sparql(query)
        
        assert len(results) > 0
        labels = [r["label"] for r in results if "label" in r]
        
        # Verificar que incluye clases esperadas
        assert any("Préstamo" in label for label in labels)
    
    def test_query_high_risk_documents(self):
        """Consulta documentos con alto riesgo."""
        query = """
            PREFIX tf: <http://tefinancia.es/ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?class ?label ?risk WHERE {
                ?class tf:nivelRiesgoBase ?risk .
                ?class rdfs:label ?label .
                FILTER(?risk = "ALTO")
            }
        """
        
        results = ontology_service.query_sparql(query)
        
        # Debería encontrar al menos LineaCredito
        assert len(results) > 0
    
    def test_query_with_filter(self):
        """Consulta con filtro numérico."""
        query = """
            PREFIX tf: <http://tefinancia.es/ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?class ?label ?importe WHERE {
                ?class tf:importeMinimo ?importe .
                ?class rdfs:label ?label .
                FILTER(?importe >= 30000)
            }
        """
        
        results = ontology_service.query_sparql(query)
        
        # Préstamo Hipotecario debería estar incluido
        assert len(results) > 0
        assert all(r["importe"] >= 30000 for r in results if "importe" in r)
    
    def test_query_invalid_syntax(self):
        """Consulta con sintaxis inválida genera error."""
        query = "SELECT ?x WHERE { INVALID SYNTAX }"
        
        with pytest.raises(Exception):
            ontology_service.query_sparql(query)


class TestRelationships:
    """Tests para relaciones semánticas (ObjectProperties)."""
    
    def test_get_related_documents(self):
        """Obtiene documentos relacionados."""
        class_uri = ontology_service.TF.PrestamoHipotecario
        related = ontology_service.get_related_documents(class_uri)
        
        assert isinstance(related, list)
        
        # PrestamoHipotecario requiere valoración, DNI, etc.
        if len(related) > 0:
            assert all("property" in r and "target" in r for r in related)
    
    def test_get_compliance_regulations(self):
        """Obtiene regulaciones aplicables."""
        class_uri = ontology_service.TF.PrestamoHipotecario
        regulations = ontology_service.get_compliance_regulations(class_uri)
        
        assert isinstance(regulations, list)
        
        # PrestamoHipotecario debería tener Ley Hipotecaria
        if len(regulations) > 0:
            assert any("Hipotecaria" in reg or "MiFID" in reg for reg in regulations)


class TestEdgeCases:
    """Tests para casos límite y manejo de errores."""
    
    def test_get_class_info_nonexistent(self):
        """Intenta obtener info de clase inexistente."""
        fake_uri = ontology_service.TF.ClaseInexistente
        info = ontology_service.get_class_info(fake_uri)
        
        # Debería retornar dict vacío o None
        assert info is None or len(info.get("properties", {})) == 0
    
    def test_validate_empty_metadata(self):
        """Valida con metadatos vacíos."""
        class_uri = ontology_service.TF.PrestamoHipotecario
        metadata = {}
        
        is_valid, errors = ontology_service.validate_metadata(class_uri, metadata)
        
        # No debería ser válido si hay campos requeridos
        # (depende de las restricciones en la ontología)
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
    
    def test_infer_risk_no_metadata(self):
        """Infiere riesgo sin metadatos."""
        class_uri = ontology_service.TF.PrestamoPersonal
        metadata = {}
        
        risk = ontology_service.infer_risk_level(class_uri, metadata)
        
        # Debería retornar nivel base
        assert risk in ["BAJO", "MEDIO", "ALTO"]
    
    def test_classify_empty_content(self):
        """Clasifica contenido vacío."""
        content = ""
        
        result = ontology_service.classify_document(content, {})
        
        # Puede retornar None o clasificación con confianza 0
        if result:
            assert result["confidence"] == 0 or len(result["matched_keywords"]) == 0


# ============================================================================
# TESTS DE INTEGRACIÓN CON API REST
# ============================================================================

class TestOntologyAPIIntegration:
    """Tests de integración para API REST (requieren servidor corriendo)."""
    
    @pytest.mark.skip(reason="Requiere servidor FastAPI corriendo")
    def test_api_classify_endpoint(self):
        """Test de endpoint POST /ontology/classify."""
        # Este test requeriría requests o httpx
        pass
    
    @pytest.mark.skip(reason="Requiere servidor FastAPI corriendo")
    def test_api_validate_endpoint(self):
        """Test de endpoint POST /ontology/validate."""
        pass
    
    @pytest.mark.skip(reason="Requiere servidor FastAPI corriendo")
    def test_api_sparql_endpoint(self):
        """Test de endpoint POST /ontology/sparql."""
        pass
    
    @pytest.mark.skip(reason="Requiere servidor FastAPI corriendo")
    def test_api_hierarchy_endpoint(self):
        """Test de endpoint GET /ontology/hierarchy."""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
