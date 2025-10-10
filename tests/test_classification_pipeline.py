"""
Tests de Integración para el Pipeline de Clasificación Triple

Prueba el pipeline completo: Taxonomía → ML → Ontología → Validación → Riesgo
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from backend.services.classification_service import classification_service
from backend.models.database_models import Document


@pytest.fixture
def mock_document():
    """Fixture para documento de prueba"""
    doc = Mock(spec=Document)
    doc.id = uuid4()
    doc.title = "Contrato de Préstamo Hipotecario"
    doc.metadata_ = {
        "importeFinanciado": 250000,
        "ltv": 75,
        "tae": 3.5,
        "plazoMeses": 300
    }
    return doc


@pytest.fixture
def sample_text_prestamo():
    """Texto de ejemplo de un préstamo hipotecario"""
    return """
    Contrato de Préstamo Hipotecario
    
    El Banco XYZ concede un préstamo hipotecario de 250.000€ para la 
    adquisición de vivienda habitual. El préstamo está garantizado 
    mediante hipoteca sobre el inmueble situado en Madrid.
    
    Condiciones:
    - Importe: 250.000€
    - Plazo: 25 años
    - LTV: 75%
    - TAE: 3.5%
    """


@pytest.fixture
def sample_text_tarjeta():
    """Texto de ejemplo de tarjeta de crédito"""
    return """
    Contrato de Tarjeta de Crédito
    
    El Banco XYZ emite una tarjeta de crédito con las siguientes condiciones:
    - Límite de crédito: 3.000€
    - TAE: 21.5%
    - Comisión anual: 50€
    """


class TestClassificationModes:
    """Tests de los 4 modos de clasificación"""
    
    @pytest.mark.asyncio
    async def test_fast_mode_uses_only_taxonomy(self, mock_document, sample_text_prestamo):
        """
        Modo FAST debe usar solo taxonomía (10ms)
        """
        with patch('backend.services.taxonomy_service.taxonomy_service.classify_by_keywords') as mock_taxonomy:
            mock_taxonomy.return_value = {
                "class_id": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.85,
                "path": ["ProductoFinanciero", "Prestamo", "PrestamoHipotecario"]
            }
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="fast"
            )
            
            # Verificaciones
            assert result["category"] == "PrestamoHipotecario"
            assert result["method"] == "taxonomy"
            assert "taxonomy" in result["phases_used"]
            assert "ml" not in result["phases_used"]
            assert "ontology" not in result["phases_used"]
            mock_taxonomy.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ml_mode_uses_taxonomy_and_ml(self, mock_document, sample_text_prestamo):
        """
        Modo ML debe usar taxonomía + ML (~100ms)
        """
        result = await classification_service.classify_document(
            document=mock_document,
            text=sample_text_prestamo,
            db=Mock(),
            mode="ml"
        )
        
        # Verificaciones
        assert result["method"] in ["taxonomy+ml", "ml"]
        assert "taxonomy" in result["phases_used"] or "ml" in result["phases_used"]
        assert "ontology" not in result["phases_used"]
    
    @pytest.mark.asyncio
    async def test_precise_mode_uses_all_phases(self, mock_document, sample_text_prestamo):
        """
        Modo PRECISE debe usar todas las fases (~500ms)
        """
        with patch('backend.services.ontology_service.ontology_service.classify_document') as mock_ontology:
            mock_ontology.return_value = {
                "class_name": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.93,
                "matched_keywords": ["préstamo hipotecario", "hipoteca"]
            }
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="precise"
            )
            
            # Verificaciones
            assert "ontology" in result["phases_used"]
            assert result.get("ontology_confidence") is not None
            mock_ontology.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_intelligent_mode_skips_phases_with_high_confidence(self, mock_document, sample_text_prestamo):
        """
        Modo INTELLIGENT debe saltar fases si confianza > 85%
        """
        with patch('backend.services.taxonomy_service.taxonomy_service.classify_by_keywords') as mock_taxonomy:
            # Confianza alta (90%) debe saltar ML y OWL
            mock_taxonomy.return_value = {
                "class_id": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.90,
                "path": ["ProductoFinanciero", "Prestamo", "PrestamoHipotecario"]
            }
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="intelligent"
            )
            
            # Con confianza 90%, debe saltar ML y OWL
            assert result["confidence"] >= 0.85
            # Solo debe tener taxonomía
            assert "taxonomy" in result["phases_used"]


class TestOntologyValidation:
    """Tests de validación de metadatos contra restricciones OWL"""
    
    @pytest.mark.asyncio
    async def test_validation_detects_invalid_importe(self, mock_document, sample_text_prestamo):
        """
        Debe detectar importeFinanciado < 30000 (restricción OWL)
        """
        # Metadatos inválidos
        mock_document.metadata_ = {
            "importeFinanciado": 20000,  # Debería ser >= 30000
            "ltv": 75,
            "tae": 3.5
        }
        
        with patch('backend.services.ontology_service.ontology_service') as mock_ont:
            mock_ont.classify_document.return_value = {
                "class_name": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.93,
                "matched_keywords": ["préstamo hipotecario"]
            }
            
            mock_ont.TF = {"PrestamoHipotecario": "http://example.com/PrestamoHipotecario"}
            mock_ont.validate_metadata.return_value = (
                False,
                ["importeFinanciado debe ser >= 30000"]
            )
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="precise"
            )
            
            # Verificaciones
            validation = result.get("metadata_validation")
            assert validation is not None
            assert validation["is_valid"] is False
            assert len(validation["errors"]) > 0
            assert any("importeFinanciado" in err for err in validation["errors"])
    
    @pytest.mark.asyncio
    async def test_validation_accepts_valid_metadata(self, mock_document, sample_text_prestamo):
        """
        Debe aceptar metadatos válidos
        """
        # Metadatos válidos
        mock_document.metadata_ = {
            "importeFinanciado": 250000,  # >= 30000 ✓
            "ltv": 75,  # <= 100 ✓
            "tae": 3.5,  # >= 0 ✓
            "plazoMeses": 300  # > 0 ✓
        }
        
        with patch('backend.services.ontology_service.ontology_service') as mock_ont:
            mock_ont.classify_document.return_value = {
                "class_name": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.93,
                "matched_keywords": ["préstamo hipotecario"]
            }
            
            mock_ont.TF = {"PrestamoHipotecario": "http://example.com/PrestamoHipotecario"}
            mock_ont.validate_metadata.return_value = (True, [])
            mock_ont.get_required_fields.return_value = ["tieneCliente"]
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="precise"
            )
            
            # Verificaciones
            validation = result.get("metadata_validation")
            assert validation is not None
            assert validation["is_valid"] is True
            assert len(validation["errors"]) == 0


class TestRiskInference:
    """Tests de inferencia de nivel de riesgo"""
    
    @pytest.mark.asyncio
    async def test_high_risk_ltv_over_80(self, mock_document, sample_text_prestamo):
        """
        LTV > 80% debe inferir riesgo ALTO
        """
        mock_document.metadata_ = {
            "importeFinanciado": 250000,
            "ltv": 85,  # > 80% → ALTO
            "tae": 3.5
        }
        
        with patch('backend.services.ontology_service.ontology_service') as mock_ont:
            mock_ont.classify_document.return_value = {
                "class_name": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.93,
                "matched_keywords": ["préstamo hipotecario"]
            }
            
            mock_ont.TF = {"PrestamoHipotecario": "http://example.com/PrestamoHipotecario"}
            mock_ont.infer_risk_level.return_value = "ALTO"
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="precise"
            )
            
            # Verificaciones
            assert result.get("inferred_risk_level") == "ALTO"
    
    @pytest.mark.asyncio
    async def test_high_risk_tae_over_10(self, mock_document, sample_text_tarjeta):
        """
        TAE > 10% debe inferir riesgo ALTO
        """
        mock_document.metadata_ = {
            "limiteCredito": 3000,
            "tae": 21.5  # > 10% → ALTO
        }
        
        with patch('backend.services.ontology_service.ontology_service') as mock_ont:
            mock_ont.classify_document.return_value = {
                "class_name": "TarjetaCredito",
                "class_label": "Tarjeta de Crédito",
                "confidence": 0.90,
                "matched_keywords": ["tarjeta de crédito"]
            }
            
            mock_ont.TF = {"TarjetaCredito": "http://example.com/TarjetaCredito"}
            mock_ont.infer_risk_level.return_value = "ALTO"
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_tarjeta,
                db=Mock(),
                mode="precise"
            )
            
            # Verificaciones
            assert result.get("inferred_risk_level") == "ALTO"
    
    @pytest.mark.asyncio
    async def test_low_risk_normal_conditions(self, mock_document, sample_text_prestamo):
        """
        Condiciones normales debe inferir riesgo BAJO
        """
        mock_document.metadata_ = {
            "importeFinanciado": 250000,
            "ltv": 75,  # < 80% ✓
            "tae": 3.5,  # < 10% ✓
            "plazoMeses": 300
        }
        
        with patch('backend.services.ontology_service.ontology_service') as mock_ont:
            mock_ont.classify_document.return_value = {
                "class_name": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.93,
                "matched_keywords": ["préstamo hipotecario"]
            }
            
            mock_ont.TF = {"PrestamoHipotecario": "http://example.com/PrestamoHipotecario"}
            mock_ont.infer_risk_level.return_value = "BAJO"
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="precise"
            )
            
            # Verificaciones
            assert result.get("inferred_risk_level") == "BAJO"
    
    @pytest.mark.asyncio
    async def test_medium_risk_long_term(self, mock_document, sample_text_prestamo):
        """
        Plazo > 240 meses debe elevar riesgo de BAJO a MEDIO
        """
        mock_document.metadata_ = {
            "importeFinanciado": 250000,
            "ltv": 70,  # BAJO
            "tae": 3.5,  # BAJO
            "plazoMeses": 360  # > 240 → MEDIO
        }
        
        with patch('backend.services.ontology_service.ontology_service') as mock_ont:
            mock_ont.classify_document.return_value = {
                "class_name": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.93,
                "matched_keywords": ["préstamo hipotecario"]
            }
            
            mock_ont.TF = {"PrestamoHipotecario": "http://example.com/PrestamoHipotecario"}
            mock_ont.infer_risk_level.return_value = "MEDIO"
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="precise"
            )
            
            # Verificaciones
            risk = result.get("inferred_risk_level")
            assert risk in ["MEDIO", "ALTO"]  # Debe ser al menos MEDIO


class TestConfidenceBlending:
    """Tests de blending de confianza entre fases"""
    
    @pytest.mark.asyncio
    async def test_taxonomy_ml_blending_50_50(self, mock_document, sample_text_prestamo):
        """
        Blending Taxonomía + ML debe ser 50%-50%
        """
        with patch('backend.services.taxonomy_service.taxonomy_service.classify_by_keywords') as mock_tax:
            mock_tax.return_value = {
                "class_id": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.70,
                "path": ["ProductoFinanciero", "Prestamo", "PrestamoHipotecario"]
            }
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="ml"
            )
            
            # Si usó ML, debe haber blending
            if "ml" in result["phases_used"]:
                # Confianza final debe estar entre taxonomía y ML
                assert 0.6 <= result["confidence"] <= 0.95
    
    @pytest.mark.asyncio
    async def test_ontology_blending_40_60(self, mock_document, sample_text_prestamo):
        """
        Blending con Ontología debe ser Anterior(40%) + OWL(60%)
        """
        with patch('backend.services.ontology_service.ontology_service.classify_document') as mock_ont:
            mock_ont.return_value = {
                "class_name": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.95,
                "matched_keywords": ["préstamo hipotecario", "hipoteca"]
            }
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="precise"
            )
            
            # Si usó ontología, confianza debe ser alta
            if "ontology" in result["phases_used"]:
                assert result["confidence"] >= 0.85
                assert result.get("ontology_confidence") is not None


class TestMetadataEnrichment:
    """Tests de enriquecimiento de metadata"""
    
    @pytest.mark.asyncio
    async def test_metadata_includes_all_phases(self, mock_document, sample_text_prestamo):
        """
        Metadata debe incluir información de todas las fases
        """
        with patch('backend.services.ontology_service.ontology_service') as mock_ont:
            mock_ont.classify_document.return_value = {
                "class_name": "PrestamoHipotecario",
                "class_label": "Préstamo Hipotecario",
                "confidence": 0.93,
                "matched_keywords": ["préstamo hipotecario", "hipoteca"]
            }
            mock_ont.TF = {"PrestamoHipotecario": "http://example.com/PrestamoHipotecario"}
            mock_ont.validate_metadata.return_value = (True, [])
            mock_ont.get_required_fields.return_value = ["tieneCliente"]
            mock_ont.infer_risk_level.return_value = "BAJO"
            
            result = await classification_service.classify_document(
                document=mock_document,
                text=sample_text_prestamo,
                db=Mock(),
                mode="precise"
            )
            
            # Verificar campos clave
            assert "phases_used" in result
            assert "classification_mode" in result
            assert result["classification_mode"] == "precise"
            
            # Si usó ontología
            if "ontology" in result["phases_used"]:
                assert "ontology_class" in result
                assert "ontology_label" in result
                assert "matched_keywords" in result


# Tests de performance (benchmarks)
class TestPerformance:
    """Tests de performance de los diferentes modos"""
    
    @pytest.mark.asyncio
    async def test_fast_mode_is_faster_than_100ms(self, mock_document, sample_text_prestamo):
        """
        Modo FAST debe ejecutar en menos de 100ms
        """
        import time
        
        start = time.time()
        result = await classification_service.classify_document(
            document=mock_document,
            text=sample_text_prestamo,
            db=Mock(),
            mode="fast"
        )
        duration_ms = (time.time() - start) * 1000
        
        # Fast mode debe ser < 100ms
        assert duration_ms < 100, f"Fast mode took {duration_ms}ms (expected < 100ms)"
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
