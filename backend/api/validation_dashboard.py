"""
Endpoints adicionales para el dashboard de validación.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.validation import ValidationResult, ValidationHistory

router = APIRouter(prefix="/api/v1/validation/dashboard", tags=["validation-dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    period: str = Query("30d", description="Período: 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Estadísticas completas para el dashboard.
    
    Incluye:
    - Total validaciones
    - Entidades flagged
    - Documentos procesados
    - Tasa de cumplimiento
    - Comparación con período anterior
    """
    # Calcular fechas
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
    start_date = datetime.utcnow() - timedelta(days=days)
    previous_start = start_date - timedelta(days=days)
    
    # Stats período actual
    total_validations = db.query(func.count(ValidationResult.id)).filter(
        ValidationResult.checked_at >= start_date
    ).scalar() or 0
    
    entities_flagged = db.query(func.count(ValidationResult.id)).filter(
        and_(
            ValidationResult.checked_at >= start_date,
            ValidationResult.is_sanctioned == True
        )
    ).scalar() or 0
    
    documents_processed = db.query(func.count(ValidationHistory.id)).filter(
        ValidationHistory.validated_at >= start_date
    ).scalar() or 0
    
    # Stats período anterior (para comparación)
    prev_total = db.query(func.count(ValidationResult.id)).filter(
        and_(
            ValidationResult.checked_at >= previous_start,
            ValidationResult.checked_at < start_date
        )
    ).scalar() or 0
    
    prev_flagged = db.query(func.count(ValidationResult.id)).filter(
        and_(
            ValidationResult.checked_at >= previous_start,
            ValidationResult.checked_at < start_date,
            ValidationResult.is_sanctioned == True
        )
    ).scalar() or 0
    
    # Calcular cambios
    validation_change = ((total_validations - prev_total) / prev_total * 100) if prev_total > 0 else 0
    flagged_change = ((entities_flagged - prev_flagged) / prev_flagged * 100) if prev_flagged > 0 else 0
    
    return {
        "period": period,
        "total_validations": total_validations,
        "entities_flagged": entities_flagged,
        "flagged_percentage": (entities_flagged / total_validations * 100) if total_validations > 0 else 0,
        "documents_processed": documents_processed,
        "compliance_rate": 100 - ((entities_flagged / total_validations * 100) if total_validations > 0 else 0),
        "changes": {
            "validation_change_pct": round(validation_change, 1),
            "flagged_change_pct": round(flagged_change, 1),
        },
        "previous_period": {
            "total_validations": prev_total,
            "entities_flagged": prev_flagged,
        }
    }


@router.get("/recent")
async def get_recent_validations(
    limit: int = Query(20, description="Número de resultados"),
    flagged_only: bool = Query(False, description="Solo entidades flagged"),
    db: Session = Depends(get_db)
):
    """
    Obtiene validaciones recientes con detalles.
    """
    query = db.query(ValidationResult).order_by(ValidationResult.checked_at.desc())
    
    if flagged_only:
        query = query.filter(ValidationResult.is_sanctioned == True)
    
    results = query.limit(limit).all()
    
    return [
        {
            "id": r.id,
            "entity_name": r.entity_name,
            "entity_type": r.entity_type,
            "is_sanctioned": r.is_sanctioned,
            "confidence": r.confidence,
            "sources_checked": r.sources_checked,
            "checked_at": r.checked_at.isoformat(),
            "document_id": r.document_id,
        }
        for r in results
    ]


@router.get("/trends")
async def get_validation_trends(
    period: str = Query("30d", description="Período: 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Obtiene tendencias de validaciones por día.
    
    Retorna array con datos diarios de:
    - Validaciones totales
    - Entidades flagged
    - Tasa de cumplimiento
    """
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Agrupar por día
    from sqlalchemy import Date, cast
    
    trends = []
    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        total = db.query(func.count(ValidationResult.id)).filter(
            and_(
                ValidationResult.checked_at >= day_start,
                ValidationResult.checked_at < day_end
            )
        ).scalar() or 0
        
        flagged = db.query(func.count(ValidationResult.id)).filter(
            and_(
                ValidationResult.checked_at >= day_start,
                ValidationResult.checked_at < day_end,
                ValidationResult.is_sanctioned == True
            )
        ).scalar() or 0
        
        trends.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "validations": total,
            "flagged": flagged,
            "compliance_rate": 100 - ((flagged / total * 100) if total > 0 else 0),
        })
    
    return trends


@router.get("/sources")
async def get_source_distribution(
    period: str = Query("30d", description="Período: 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Distribución de matches por fuente (OFAC, EU, World Bank).
    """
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Mock data - implementar query real
    return [
        {"source": "OFAC", "count": 45, "percentage": 47.4},
        {"source": "EU_SANCTIONS", "count": 32, "percentage": 33.7},
        {"source": "WORLD_BANK", "count": 18, "percentage": 18.9},
    ]


@router.get("/top-entities")
async def get_top_flagged_entities(
    limit: int = Query(10, description="Número de resultados"),
    period: str = Query("30d", description="Período: 7d, 30d, 90d"),
    db: Session = Depends(get_db)
):
    """
    Top entidades más flagged en el período.
    """
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 30)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Agrupar por nombre de entidad
    results = db.query(
        ValidationResult.entity_name,
        ValidationResult.entity_type,
        func.count(ValidationResult.id).label("occurrences"),
        func.max(ValidationResult.confidence).label("max_confidence")
    ).filter(
        and_(
            ValidationResult.checked_at >= start_date,
            ValidationResult.is_sanctioned == True
        )
    ).group_by(
        ValidationResult.entity_name,
        ValidationResult.entity_type
    ).order_by(
        func.count(ValidationResult.id).desc()
    ).limit(limit).all()
    
    return [
        {
            "entity_name": r.entity_name,
            "entity_type": r.entity_type,
            "occurrences": r.occurrences,
            "max_confidence": r.max_confidence,
        }
        for r in results
    ]
