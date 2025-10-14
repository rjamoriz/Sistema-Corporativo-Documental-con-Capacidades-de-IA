"""
Dashboard API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from typing import Dict, Any, List
from datetime import datetime, timedelta

from core.auth import get_current_user
from core.database import get_db
from models.database_models import Document, User
from models.schemas import UserResponse

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get dashboard statistics including:
    - Total documents
    - Documents by category
    - Documents by status
    - Risk distribution
    - Compliance summary
    - Recent uploads
    """
    
    try:
        # Total documents
        result = await db.execute(select(func.count(Document.id)))
        total_documents = result.scalar() or 0
        
        # Documents by category
        result = await db.execute(
            select(Document.classification, func.count(Document.id))
            .group_by(Document.classification)
        )
        category_counts = result.all()
        
        documents_by_category = {
            (category.value if category else "sin_clasificar"): count 
            for category, count in category_counts
        }
        
        # Documents by status
        result = await db.execute(
            select(Document.status, func.count(Document.id))
            .group_by(Document.status)
        )
        status_counts = result.all()
        
        documents_by_status = {
            (status.value if status else "unknown"): count 
            for status, count in status_counts
        }
        
        # Risk distribution (mock data for now - can be enhanced with real risk data)
        risk_distribution = {
            "low": int(total_documents * 0.5),
            "medium": int(total_documents * 0.3),
            "high": int(total_documents * 0.15),
            "critical": int(total_documents * 0.05)
        }
        
        # Compliance summary (mock data for now - can be enhanced with real compliance data)
        compliance_summary = {
            "compliant": int(total_documents * 0.7),
            "non_compliant": int(total_documents * 0.1),
            "pending": int(total_documents * 0.2)
        }
        
        # Recent uploads (last 10 documents)
        result = await db.execute(
            select(Document)
            .order_by(Document.created_at.desc())
            .limit(10)
        )
        recent_uploads = result.scalars().all()
        
        recent_uploads_data = [
            {
                "id": str(doc.id),
                "filename": doc.title,
                "status": doc.status.value if doc.status else "unknown",
                "classification": doc.classification.value if doc.classification else "sin_clasificar",
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "file_size": doc.file_size_bytes,
                "mime_type": doc.mime_type
            }
            for doc in recent_uploads
        ]
        
        return {
            "total_documents": total_documents,
            "total_chunks": 0,  # Can be enhanced with real chunk count
            "total_entities": 0,  # Can be enhanced with real entity count
            "documents_by_category": documents_by_category,
            "documents_by_status": documents_by_status,
            "risk_distribution": risk_distribution,
            "compliance_summary": compliance_summary,
            "recent_uploads": recent_uploads_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas del dashboard: {str(e)}"
        )
