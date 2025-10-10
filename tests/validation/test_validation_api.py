"""
Tests para endpoints de validación API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from backend.api.validation import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.mark.asyncio
async def test_check_entity_sanctions_endpoint():
    """Test: Endpoint POST /validation/sanctions/check."""
    mock_result = {
        "is_sanctioned": True,
        "confidence": 0.95,
        "matches": [
            {
                "source": "OFAC",
                "name": "John Doe",
                "type": "PERSON",
                "similarity": 95.0,
                "program": ["SDGT"],
                "address": [],
                "remarks": None,
            }
        ],
        "sources_checked": ["OFAC", "EU_SANCTIONS", "WORLD_BANK"],
        "checked_at": "2025-10-10T10:00:00",
        "validation_id": 1,
    }

    with patch(
        "backend.api.validation.SanctionsService"
    ) as MockService:
        mock_service = MockService.return_value.__aenter__.return_value
        mock_service.check_entity = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/v1/validation/sanctions/check",
            json={
                "entity_name": "John Doe",
                "entity_type": "PERSON",
                "country": "Iran",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["is_sanctioned"] is True
    assert data["confidence"] == 0.95
    assert len(data["matches"]) == 1


@pytest.mark.asyncio
async def test_validate_document_entities_endpoint():
    """Test: Endpoint POST /validation/document/{id}/validate-entities."""
    mock_result = {
        "document_id": 123,
        "total_entities": 5,
        "flagged_entities": 2,
        "validation_results": [],
        "history_id": 1,
    }

    with patch(
        "backend.api.validation.SanctionsService"
    ) as MockService:
        mock_service = MockService.return_value.__aenter__.return_value
        mock_service.validate_document_entities = AsyncMock(
            return_value=mock_result
        )

        response = client.post(
            "/api/v1/validation/document/123/validate-entities"
        )

    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == 123
    assert data["total_entities"] == 5
    assert data["flagged_entities"] == 2


@pytest.mark.asyncio
async def test_check_business_registry_endpoint():
    """Test: Endpoint POST /validation/business/check."""
    mock_result = {
        "cif": "A12345678",
        "name": "Test Company SL",
        "is_active": True,
        "status": "ACTIVA",
        "capital": 100000.0,
        "incorporation_date": "2020-01-15",
        "financial_indicators": {"revenue": 500000},
        "risk_indicators": {"bankruptcy_risk": "LOW"},
        "source": "InfoEmpresa",
        "checked_at": "2025-10-10T10:00:00",
    }

    with patch(
        "backend.api.validation.BusinessRegistryService"
    ) as MockService:
        mock_service = MockService.return_value.__aenter__.return_value
        mock_service.check_company = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/v1/validation/business/check",
            json={"cif": "A12345678", "name": "Test Company"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["cif"] == "A12345678"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_esg_score_endpoint():
    """Test: Endpoint POST /validation/esg/score."""
    mock_result = {
        "company_name": "Apple Inc",
        "isin": "US0378331005",
        "overall_score": 85.5,
        "rating": "AA",
        "environmental": {"score": 88.0},
        "social": {"score": 82.0},
        "governance": {"score": 86.0},
        "controversies": {"count": 0},
        "source": "Refinitiv",
        "last_updated": "2025-09-01",
        "checked_at": "2025-10-10T10:00:00",
    }

    with patch("backend.api.validation.ESGService") as MockService:
        mock_service = MockService.return_value.__aenter__.return_value
        mock_service.get_esg_score = AsyncMock(return_value=mock_result)

        response = client.post(
            "/api/v1/validation/esg/score",
            json={"company_name": "Apple Inc", "isin": "US0378331005"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Apple Inc"
    assert data["overall_score"] == 85.5
    assert data["rating"] == "AA"
