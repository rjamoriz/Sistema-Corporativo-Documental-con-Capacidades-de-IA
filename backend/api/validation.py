"""
Endpoints API para validación de terceros.

Rutas:
- POST /api/v1/validation/sanctions/check - Validar entidad contra sanciones
- POST /api/v1/validation/document/{id}/validate-entities - Validar entidades de documento
- GET /api/v1/validation/history - Obtener historial de validaciones
- POST /api/v1/validation/business/check - Validar empresa en registro mercantil
- POST /api/v1/validation/esg/score - Obtener scoring ESG
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.services.validation import (
    SanctionsService,
    BusinessRegistryService,
    ESGService,
)
from backend.database import get_db


router = APIRouter(prefix="/api/v1/validation", tags=["validation"])


# ============================================================================
# Schemas de Request/Response
# ============================================================================

class EntityCheckRequest(BaseModel):
    """Request para validar entidad contra sanciones."""
    entity_name: str = Field(..., description="Nombre de la entidad")
    entity_type: str = Field(..., description="Tipo: PERSON, COMPANY, VESSEL")
    country: Optional[str] = Field(None, description="País de la entidad")
    additional_info: Optional[dict] = Field(None, description="Info adicional")


class SanctionMatch(BaseModel):
    """Match encontrado en lista de sanciones."""
    source: str
    name: str
    type: Optional[str]
    similarity: float
    program: Optional[List[str]]
    address: Optional[List[dict]]
    remarks: Optional[str]


class EntityCheckResponse(BaseModel):
    """Response de validación de entidad."""
    is_sanctioned: bool
    confidence: float
    matches: List[SanctionMatch]
    sources_checked: List[str]
    checked_at: str
    validation_id: int


class DocumentValidationResponse(BaseModel):
    """Response de validación de documento."""
    document_id: int
    total_entities: int
    flagged_entities: int
    validation_results: List[dict]
    history_id: int


class ValidationHistoryItem(BaseModel):
    """Item del historial de validaciones."""
    id: int
    document_id: int
    entities_validated: int
    entities_flagged: int
    validated_at: str


class BusinessCheckRequest(BaseModel):
    """Request para validar empresa."""
    cif: str = Field(..., description="CIF/NIF de la empresa")
    name: Optional[str] = Field(None, description="Nombre de la empresa")


class BusinessCheckResponse(BaseModel):
    """Response de validación de empresa."""
    cif: str
    name: str
    is_active: bool
    status: str
    capital: float
    incorporation_date: Optional[str]
    financial_indicators: dict
    risk_indicators: dict
    source: str
    checked_at: str


class ESGScoreRequest(BaseModel):
    """Request para obtener ESG score."""
    company_name: str = Field(..., description="Nombre de la empresa")
    isin: Optional[str] = Field(None, description="Código ISIN")


class ESGScoreResponse(BaseModel):
    """Response con ESG score."""
    company_name: str
    isin: Optional[str]
    overall_score: float
    rating: str
    environmental: dict
    social: dict
    governance: dict
    controversies: dict
    source: str
    last_updated: Optional[str]
    checked_at: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post(
    "/sanctions/check",
    response_model=EntityCheckResponse,
    summary="Validar entidad contra listas de sanciones",
    description="Valida una entidad (persona, empresa, barco) contra OFAC, EU Sanctions y World Bank"
)
async def check_entity_sanctions(
    request: EntityCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Valida una entidad contra todas las listas de sanciones internacionales.
    
    - **entity_name**: Nombre de la entidad a validar
    - **entity_type**: Tipo (PERSON, COMPANY, VESSEL, etc.)
    - **country**: País (opcional, mejora precisión)
    - **additional_info**: DNI, CIF, etc. (opcional)
    
    Returns información de matches encontrados con nivel de confianza.
    """
    async with SanctionsService(db) as service:
        result = await service.check_entity(
            entity_name=request.entity_name,
            entity_type=request.entity_type,
            country=request.country,
            additional_info=request.additional_info,
        )
    
    return EntityCheckResponse(**result)


@router.post(
    "/document/{document_id}/validate-entities",
    response_model=DocumentValidationResponse,
    summary="Validar todas las entidades de un documento",
    description="Valida todas las entidades extraídas (por NER) de un documento"
)
async def validate_document_entities(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Valida todas las entidades de un documento contra listas de sanciones.
    
    Asume que las entidades ya fueron extraídas por el sistema NER.
    """
    async with SanctionsService(db) as service:
        result = await service.validate_document_entities(document_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento {document_id} no encontrado"
        )
    
    return DocumentValidationResponse(**result)


@router.get(
    "/history",
    response_model=List[ValidationHistoryItem],
    summary="Obtener historial de validaciones",
    description="Retorna el historial de validaciones realizadas"
)
async def get_validation_history(
    document_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de validaciones.
    
    - **document_id**: Filtrar por documento (opcional)
    - **limit**: Máximo de resultados (default: 100)
    """
    async with SanctionsService(db) as service:
        history = await service.get_validation_history(document_id, limit)
    
    return [ValidationHistoryItem(**item) for item in history]


@router.post(
    "/business/check",
    response_model=BusinessCheckResponse,
    summary="Validar empresa en registro mercantil",
    description="Verifica empresa en InfoEmpresa/Informa y obtiene datos financieros"
)
async def check_business_registry(
    request: BusinessCheckRequest,
):
    """
    Valida una empresa en el registro mercantil español.
    
    - **cif**: CIF/NIF de la empresa
    - **name**: Nombre (opcional, para validación cruzada)
    
    Returns información legal, financiera y de riesgo.
    """
    async with BusinessRegistryService() as service:
        result = await service.check_company(
            cif=request.cif,
            name=request.name,
        )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empresa con CIF {request.cif} no encontrada"
        )
    
    return BusinessCheckResponse(**result)


@router.post(
    "/esg/score",
    response_model=ESGScoreResponse,
    summary="Obtener scoring ESG de empresa",
    description="Obtiene el scoring ESG (Refinitiv/MSCI) de una empresa"
)
async def get_esg_score(
    request: ESGScoreRequest,
):
    """
    Obtiene el scoring ESG de una empresa.
    
    - **company_name**: Nombre de la empresa
    - **isin**: Código ISIN (opcional, mejora precisión)
    
    Returns scoring ESG desglosado por Environmental, Social y Governance.
    """
    async with ESGService() as service:
        result = await service.get_esg_score(
            company_name=request.company_name,
            isin=request.isin,
        )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ESG score no disponible para {request.company_name}"
        )
    
    return ESGScoreResponse(**result)


@router.post(
    "/sanctions/batch",
    summary="Validar múltiples entidades en batch",
    description="Valida múltiples entidades contra sanciones en paralelo"
)
async def check_batch_sanctions(
    entities: List[EntityCheckRequest],
    db: Session = Depends(get_db)
):
    """
    Valida múltiples entidades en paralelo.
    
    Útil para validar listas completas de clientes, proveedores, etc.
    """
    async with SanctionsService(db) as service:
        results = []
        for entity in entities:
            result = await service.check_entity(
                entity_name=entity.entity_name,
                entity_type=entity.entity_type,
                country=entity.country,
                additional_info=entity.additional_info,
            )
            results.append(result)
    
    return results


@router.get(
    "/stats",
    summary="Estadísticas de validaciones",
    description="Obtiene estadísticas globales de validaciones"
)
async def get_validation_stats(
    db: Session = Depends(get_db)
):
    """
    Estadísticas de validaciones realizadas.
    """
    from backend.models.validation import ValidationHistory, ValidationResult
    from sqlalchemy import func
    
    total_validations = db.query(func.count(ValidationResult.id)).scalar()
    sanctioned_count = db.query(func.count(ValidationResult.id)).filter(
        ValidationResult.is_sanctioned == True
    ).scalar()
    
    total_documents = db.query(func.count(ValidationHistory.id)).scalar()
    
    return {
        "total_entities_validated": total_validations,
        "entities_flagged": sanctioned_count,
        "flagged_percentage": (sanctioned_count / total_validations * 100) if total_validations > 0 else 0,
        "total_documents_validated": total_documents,
    }
