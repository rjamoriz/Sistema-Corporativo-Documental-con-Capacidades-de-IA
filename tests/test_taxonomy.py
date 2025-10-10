"""
Tests para Taxonomy Service
Sprint 1: Tests de taxonomía jerárquica
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.taxonomy_service import TaxonomyService


@pytest.fixture
def taxonomy():
    """Fixture para TaxonomyService"""
    return TaxonomyService(taxonomy_file="backend/config/taxonomy.json")


class TestTaxonomyBasics:
    """Tests básicos de taxonomía"""
    
    def test_load_taxonomy(self, taxonomy):
        """Test: La taxonomía se carga correctamente"""
        assert taxonomy.taxonomy is not None
        assert len(taxonomy.taxonomy) > 0
    
    def test_get_class_exists(self, taxonomy):
        """Test: Obtener una clase existente"""
        prestamo_personal = taxonomy.get_class("PRESTAMO_PERSONAL")
        assert prestamo_personal is not None
        assert prestamo_personal["label"] == "Préstamo Personal"
        assert prestamo_personal["level"] == 3
    
    def test_get_class_not_exists(self, taxonomy):
        """Test: Obtener una clase inexistente"""
        result = taxonomy.get_class("CLASE_INEXISTENTE")
        assert result is None


class TestTaxonomyHierarchy:
    """Tests de navegación jerárquica"""
    
    def test_get_children(self, taxonomy):
        """Test: Obtener hijos de una clase"""
        children = taxonomy.get_children("CONTRATO_FINANCIACION")
        assert len(children) == 4
        
        labels = [c["label"] for c in children]
        assert "Préstamo Personal" in labels
        assert "Préstamo Hipotecario" in labels
    
    def test_get_parent(self, taxonomy):
        """Test: Obtener padre de una clase"""
        parent = taxonomy.get_parent("PRESTAMO_PERSONAL")
        assert parent is not None
        assert parent["id"] == "CONTRATO_FINANCIACION"
        assert parent["label"] == "Contrato de Financiación"
    
    def test_get_ancestors(self, taxonomy):
        """Test: Obtener todos los ancestros"""
        ancestors = taxonomy.get_ancestors("PRESTAMO_PERSONAL")
        assert len(ancestors) == 3
        
        # Orden: más cercano a más lejano
        assert ancestors[0]["id"] == "CONTRATO_FINANCIACION"
        assert ancestors[1]["id"] == "DOC_CONTRACTUAL"
        assert ancestors[2]["id"] == "DOCUMENTO"
    
    def test_get_path(self, taxonomy):
        """Test: Obtener path completo"""
        path = taxonomy.get_path("PRESTAMO_PERSONAL")
        assert path == "Documento > Documento Contractual > Contrato de Financiación > Préstamo Personal"
    
    def test_get_hierarchy(self, taxonomy):
        """Test: Obtener jerarquía completa como árbol"""
        hierarchy = taxonomy.get_hierarchy()
        assert hierarchy is not None
        assert hierarchy["id"] == "DOCUMENTO"
        assert len(hierarchy["children"]) > 0


class TestTaxonomyFields:
    """Tests de campos y metadatos"""
    
    def test_get_required_fields(self, taxonomy):
        """Test: Obtener campos obligatorios"""
        fields = taxonomy.get_required_fields("PRESTAMO_PERSONAL")
        assert len(fields) > 0
        
        field_names = [f["name"] for f in fields]
        assert "importe_financiado" in field_names
        assert "tae" in field_names
        assert "cliente_nif" in field_names
    
    def test_get_optional_fields(self, taxonomy):
        """Test: Obtener campos opcionales"""
        fields = taxonomy.get_optional_fields("PRESTAMO_PERSONAL")
        assert len(fields) >= 0  # Puede tener o no campos opcionales
    
    def test_get_all_fields(self, taxonomy):
        """Test: Obtener todos los campos"""
        fields = taxonomy.get_all_fields("PRESTAMO_PERSONAL")
        assert "required" in fields
        assert "optional" in fields
        assert len(fields["required"]) > 0


class TestTaxonomyValidation:
    """Tests de validación de metadatos"""
    
    def test_validate_metadata_valid(self, taxonomy):
        """Test: Validar metadatos correctos"""
        metadata = {
            "importe_financiado": 10000,
            "tae": 8.5,
            "tin": 7.5,
            "plazo_meses": 48,
            "cuota_mensual": 250,
            "cliente_nif": "12345678A",
            "ingresos_mensuales": 2000,
            "scoring_crediticio": 750
        }
        
        is_valid, errors = taxonomy.validate_metadata("PRESTAMO_PERSONAL", metadata)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_metadata_missing_required(self, taxonomy):
        """Test: Validar con campos obligatorios faltantes"""
        metadata = {
            "importe_financiado": 10000
            # Faltan campos obligatorios
        }
        
        is_valid, errors = taxonomy.validate_metadata("PRESTAMO_PERSONAL", metadata)
        assert is_valid is False
        assert len(errors) > 0
        assert any("tae" in e.lower() for e in errors)
    
    def test_validate_metadata_invalid_importe(self, taxonomy):
        """Test: Validar importe fuera de rango"""
        metadata = {
            "importe_financiado": 1000,  # Menos del mínimo (3000)
            "tae": 8.5,
            "tin": 7.5,
            "plazo_meses": 48,
            "cuota_mensual": 250,
            "cliente_nif": "12345678A",
            "ingresos_mensuales": 2000,
            "scoring_crediticio": 750
        }
        
        is_valid, errors = taxonomy.validate_metadata("PRESTAMO_PERSONAL", metadata)
        assert is_valid is False
        assert any("importe" in e.lower() for e in errors)
    
    def test_validate_metadata_invalid_plazo(self, taxonomy):
        """Test: Validar plazo fuera de rango"""
        metadata = {
            "importe_financiado": 10000,
            "tae": 8.5,
            "tin": 7.5,
            "plazo_meses": 120,  # Mayor del máximo (96)
            "cuota_mensual": 250,
            "cliente_nif": "12345678A",
            "ingresos_mensuales": 2000,
            "scoring_crediticio": 750
        }
        
        is_valid, errors = taxonomy.validate_metadata("PRESTAMO_PERSONAL", metadata)
        assert is_valid is False
        assert any("plazo" in e.lower() for e in errors)


class TestTaxonomySearch:
    """Tests de búsqueda"""
    
    def test_search_by_keyword(self, taxonomy):
        """Test: Buscar clases por keyword"""
        results = taxonomy.search_by_keyword("préstamo")
        assert len(results) > 0
        
        labels = [r["label"] for r in results]
        assert any("Préstamo" in label for label in labels)
    
    def test_search_by_keyword_case_insensitive(self, taxonomy):
        """Test: Búsqueda case-insensitive"""
        results1 = taxonomy.search_by_keyword("HIPOTECA")
        results2 = taxonomy.search_by_keyword("hipoteca")
        results3 = taxonomy.search_by_keyword("Hipoteca")
        
        assert len(results1) == len(results2) == len(results3)
    
    def test_search_no_results(self, taxonomy):
        """Test: Búsqueda sin resultados"""
        results = taxonomy.search_by_keyword("palabra_inexistente_123")
        assert len(results) == 0
    
    def test_classify_by_keywords(self, taxonomy):
        """Test: Clasificar texto por keywords"""
        text = "Quiero solicitar un préstamo hipotecario para comprar una casa. Necesito valoración del inmueble."
        
        results = taxonomy.classify_by_keywords(text, top_n=3)
        assert len(results) > 0
        
        # El primer resultado debería ser préstamo hipotecario
        assert "PRESTAMO_HIPOTECARIO" in results[0]["class_id"]
        assert results[0]["confidence"] > 0


class TestTaxonomyProperties:
    """Tests de propiedades"""
    
    def test_get_risk_level(self, taxonomy):
        """Test: Obtener nivel de riesgo"""
        risk = taxonomy.get_risk_level("PRESTAMO_HIPOTECARIO")
        assert risk == "BAJO"
        
        risk = taxonomy.get_risk_level("LINEA_CREDITO")
        assert risk == "ALTO"
    
    def test_get_retention_years(self, taxonomy):
        """Test: Obtener años de retención"""
        years = taxonomy.get_retention_years("PRESTAMO_HIPOTECARIO")
        assert years == 20
        
        years = taxonomy.get_retention_years("FACTURA")
        assert years == 7
    
    def test_is_sensitive(self, taxonomy):
        """Test: Verificar datos sensibles"""
        assert taxonomy.is_sensitive("DNI") is True
        assert taxonomy.is_sensitive("NOMINA") is True
        assert taxonomy.is_sensitive("FACTURA") is False
    
    def test_get_compliance_regulations(self, taxonomy):
        """Test: Obtener regulaciones"""
        regulations = taxonomy.get_compliance_regulations("PRESTAMO_HIPOTECARIO")
        assert len(regulations) > 0
        assert "GDPR" in regulations
        assert "Ley Hipotecaria" in regulations
    
    def test_get_related_documents(self, taxonomy):
        """Test: Obtener documentos relacionados"""
        related = taxonomy.get_related_documents("PRESTAMO_HIPOTECARIO")
        assert len(related) > 0
        assert "VALORACION_INMUEBLE" in related


class TestTaxonomyStatistics:
    """Tests de estadísticas"""
    
    def test_get_leaf_classes(self, taxonomy):
        """Test: Obtener clases hoja"""
        leaves = taxonomy.get_leaf_classes()
        assert len(leaves) > 0
        
        # Todas las hojas deben tener level > 0
        for leaf in leaves:
            assert leaf["level"] > 0
    
    def test_get_statistics(self, taxonomy):
        """Test: Obtener estadísticas generales"""
        stats = taxonomy.get_statistics()
        
        assert "total_classes" in stats
        assert stats["total_classes"] > 0
        
        assert "classes_by_level" in stats
        assert len(stats["classes_by_level"]) > 0
        
        assert "classes_by_risk" in stats
        assert "max_depth" in stats
        assert stats["max_depth"] == 3


# Ejecutar tests con pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
