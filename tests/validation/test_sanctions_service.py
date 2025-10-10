"""
Tests para SanctionsService.

Cobertura:
- Validación contra OFAC (casos positivos/negativos)
- Validación contra EU Sanctions
- Validación contra World Bank
- Fuzzy matching con diferentes similitudes
- Consolidación de resultados múltiples
- Manejo de errores de API
- Validación de documento completo
- Historial de validaciones
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from backend.services.validation import SanctionsService
from backend.models.validation import ValidationResult, ValidationHistory


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Mock de sesión de base de datos."""
    session = Mock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.query = Mock()
    session.get = AsyncMock()
    return session


@pytest.fixture
def sanctions_config():
    """Configuración de test para SanctionsService."""
    return {
        "ofac": {
            "api_url": "https://test-ofac.com/api",
            "api_key": "test_key",
            "enabled": True,
        },
        "eu_sanctions": {
            "api_url": "https://test-eu.com/api",
            "api_key": "test_key",
            "enabled": True,
        },
        "world_bank": {
            "api_url": "https://test-wb.com/api",
            "enabled": True,
        },
        "fuzzy_threshold": 85,
    }


@pytest.fixture
async def sanctions_service(mock_db_session, sanctions_config):
    """Instancia de SanctionsService para tests."""
    service = SanctionsService(mock_db_session, sanctions_config)
    async with service:
        yield service


# ============================================================================
# Tests de OFAC
# ============================================================================

@pytest.mark.asyncio
async def test_check_ofac_exact_match(sanctions_service):
    """Test: Match exacto en OFAC."""
    mock_response = {
        "results": [
            {
                "id": "OFAC-123",
                "name": "John Doe",
                "type": "PERSON",
                "programs": ["SDGT"],
                "addresses": [{"city": "Tehran"}],
                "remarks": "Suspected terrorist",
            }
        ]
    }

    with patch.object(
        sanctions_service._session, "get"
    ) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )

        result = await sanctions_service._check_ofac(
            "John Doe", "PERSON", None, None
        )

    assert len(result["matches"]) == 1
    assert result["matches"][0]["source"] == "OFAC"
    assert result["matches"][0]["name"] == "John Doe"
    assert result["matches"][0]["similarity"] == 100  # Exact match
    assert result["confidence"] == 1.0


@pytest.mark.asyncio
async def test_check_ofac_fuzzy_match(sanctions_service):
    """Test: Fuzzy match en OFAC."""
    mock_response = {
        "results": [
            {
                "id": "OFAC-456",
                "name": "John H. Doe Jr.",
                "type": "PERSON",
                "programs": ["SDGT"],
            }
        ]
    }

    with patch.object(
        sanctions_service._session, "get"
    ) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )

        result = await sanctions_service._check_ofac(
            "John Doe", "PERSON", None, None
        )

    assert len(result["matches"]) == 1
    # Similarity será alta pero no 100%
    assert 85 <= result["matches"][0]["similarity"] < 100
    assert 0.85 <= result["confidence"] < 1.0


@pytest.mark.asyncio
async def test_check_ofac_no_match(sanctions_service):
    """Test: Sin match en OFAC."""
    mock_response = {"results": []}

    with patch.object(
        sanctions_service._session, "get"
    ) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )

        result = await sanctions_service._check_ofac(
            "Jane Smith", "PERSON", None, None
        )

    assert len(result["matches"]) == 0
    assert result["confidence"] == 0


@pytest.mark.asyncio
async def test_check_ofac_api_error(sanctions_service):
    """Test: Error de API de OFAC."""
    with patch.object(
        sanctions_service._session, "get"
    ) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 500

        with pytest.raises(Exception):
            await sanctions_service._check_ofac(
                "John Doe", "PERSON", None, None
            )


# ============================================================================
# Tests de EU Sanctions
# ============================================================================

@pytest.mark.asyncio
async def test_check_eu_sanctions_match(sanctions_service):
    """Test: Match en EU Sanctions."""
    mock_response = {
        "results": [
            {
                "euReferenceNumber": "EU-789",
                "fullName": "ACME Corp",
                "subjectType": "COMPANY",
                "regulation": "EU 269/2014",
                "publicationDate": "2022-03-15",
            }
        ]
    }

    with patch.object(
        sanctions_service._session, "post"
    ) as mock_post:
        mock_post.return_value.__aenter__.return_value.status = 200
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )

        result = await sanctions_service._check_eu_sanctions(
            "ACME Corp", "COMPANY", None
        )

    assert len(result["matches"]) == 1
    assert result["matches"][0]["source"] == "EU_SANCTIONS"
    assert result["matches"][0]["regulation"] == "EU 269/2014"


# ============================================================================
# Tests de World Bank
# ============================================================================

@pytest.mark.asyncio
async def test_check_world_bank_match(sanctions_service):
    """Test: Match en World Bank."""
    mock_response = {
        "response": {
            "docs": [
                {
                    "firm_name": "Bad Construction Inc",
                    "country": "Kenya",
                    "ineligibility_period": "5 years",
                    "grounds": "Fraud",
                }
            ]
        }
    }

    with patch.object(
        sanctions_service._session, "get"
    ) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )

        result = await sanctions_service._check_world_bank(
            "Bad Construction Inc", "COMPANY"
        )

    assert len(result["matches"]) == 1
    assert result["matches"][0]["source"] == "WORLD_BANK"
    assert result["matches"][0]["grounds"] == "Fraud"


# ============================================================================
# Tests de check_entity (integración)
# ============================================================================

@pytest.mark.asyncio
async def test_check_entity_sanctioned_multiple_sources(
    sanctions_service, mock_db_session
):
    """Test: Entidad sancionada en múltiples fuentes."""
    # Mock responses para todas las fuentes
    ofac_response = {
        "results": [{"id": "1", "name": "Bad Guy", "type": "PERSON", "programs": []}]
    }
    eu_response = {
        "results": [{"euReferenceNumber": "2", "fullName": "Bad Guy", "subjectType": "PERSON"}]
    }
    wb_response = {"response": {"docs": []}}

    with patch.object(sanctions_service, "_check_ofac") as mock_ofac, \
         patch.object(sanctions_service, "_check_eu_sanctions") as mock_eu, \
         patch.object(sanctions_service, "_check_world_bank") as mock_wb:

        mock_ofac.return_value = {
            "matches": [{"source": "OFAC", "name": "Bad Guy", "similarity": 95}],
            "confidence": 0.95,
        }
        mock_eu.return_value = {
            "matches": [{"source": "EU_SANCTIONS", "name": "Bad Guy", "similarity": 90}],
            "confidence": 0.90,
        }
        mock_wb.return_value = {"matches": [], "confidence": 0}

        result = await sanctions_service.check_entity(
            "Bad Guy", "PERSON", None, None
        )

    assert result["is_sanctioned"] is True
    assert result["confidence"] == 0.95  # Max de las dos fuentes
    assert len(result["matches"]) == 2
    assert "OFAC" in result["sources_checked"]
    assert "EU_SANCTIONS" in result["sources_checked"]


@pytest.mark.asyncio
async def test_check_entity_not_sanctioned(sanctions_service, mock_db_session):
    """Test: Entidad NO sancionada."""
    with patch.object(sanctions_service, "_check_ofac") as mock_ofac, \
         patch.object(sanctions_service, "_check_eu_sanctions") as mock_eu, \
         patch.object(sanctions_service, "_check_world_bank") as mock_wb:

        mock_ofac.return_value = {"matches": [], "confidence": 0}
        mock_eu.return_value = {"matches": [], "confidence": 0}
        mock_wb.return_value = {"matches": [], "confidence": 0}

        result = await sanctions_service.check_entity(
            "Good Person", "PERSON", None, None
        )

    assert result["is_sanctioned"] is False
    assert result["confidence"] == 0
    assert len(result["matches"]) == 0


@pytest.mark.asyncio
async def test_check_entity_api_failure_resilience(
    sanctions_service, mock_db_session
):
    """Test: Resiliencia ante fallos de API."""
    with patch.object(sanctions_service, "_check_ofac") as mock_ofac, \
         patch.object(sanctions_service, "_check_eu_sanctions") as mock_eu, \
         patch.object(sanctions_service, "_check_world_bank") as mock_wb:

        # OFAC falla, pero EU funciona
        mock_ofac.side_effect = Exception("OFAC API down")
        mock_eu.return_value = {
            "matches": [{"source": "EU_SANCTIONS", "name": "Bad Guy", "similarity": 92}],
            "confidence": 0.92,
        }
        mock_wb.return_value = {"matches": [], "confidence": 0}

        result = await sanctions_service.check_entity(
            "Bad Guy", "PERSON", None, None
        )

    # Debe seguir funcionando con las fuentes disponibles
    assert result["is_sanctioned"] is True
    assert len(result["matches"]) == 1
    assert result["sources_checked"] == ["OFAC", "EU_SANCTIONS", "WORLD_BANK"]


# ============================================================================
# Tests adicionales
# ============================================================================

@pytest.mark.asyncio
async def test_validate_document_entities(sanctions_service, mock_db_session):
    """Test: Validar entidades de un documento."""
    # Mock documento y entidades
    mock_doc = Mock(id=1)
    mock_entities = [
        Mock(id=1, text="John Doe", entity_type="PERSON", metadata={}),
        Mock(id=2, text="ACME Corp", entity_type="COMPANY", metadata={}),
    ]

    mock_db_session.get.return_value = mock_doc
    mock_db_session.query.return_value.filter.return_value.all = AsyncMock(
        return_value=mock_entities
    )

    with patch.object(sanctions_service, "check_entity") as mock_check:
        mock_check.side_effect = [
            {
                "is_sanctioned": True,
                "confidence": 0.95,
                "matches": [],
                "sources_checked": [],
                "checked_at": datetime.utcnow().isoformat(),
                "validation_id": 1,
            },
            {
                "is_sanctioned": False,
                "confidence": 0,
                "matches": [],
                "sources_checked": [],
                "checked_at": datetime.utcnow().isoformat(),
                "validation_id": 2,
            },
        ]

        result = await sanctions_service.validate_document_entities(1)

    assert result["document_id"] == 1
    assert result["total_entities"] == 2
    assert result["flagged_entities"] == 1


@pytest.mark.asyncio
async def test_get_validation_history(sanctions_service, mock_db_session):
    """Test: Obtener historial de validaciones."""
    mock_history = [
        Mock(
            id=1,
            document_id=10,
            entities_validated=5,
            entities_flagged=1,
            validated_at=datetime.utcnow(),
        ),
        Mock(
            id=2,
            document_id=11,
            entities_validated=3,
            entities_flagged=0,
            validated_at=datetime.utcnow(),
        ),
    ]

    mock_db_session.query.return_value.order_by.return_value.limit.return_value.all = AsyncMock(
        return_value=mock_history
    )

    result = await sanctions_service.get_validation_history(limit=10)

    assert len(result) == 2
    assert result[0]["document_id"] == 10
    assert result[0]["entities_flagged"] == 1
