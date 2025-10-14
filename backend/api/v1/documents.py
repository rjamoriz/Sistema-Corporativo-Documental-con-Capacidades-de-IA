"""
Documents Router
Handles document upload, retrieval, update, delete
Enhanced with ontology-based classification and validation
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from core.database import get_db
from models.schemas import (
    DocumentResponse, DocumentCreate, DocumentUpdate,
    DocumentUploadResponse, EntityResponse, ChunkResponse
)
from api.v1.auth import oauth2_scheme
from services import classification_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a new document
    
    - **file**: Document file (PDF, DOCX, images, audio, video, etc.)
    - **title**: Optional custom title (defaults to filename)
    - **department**: Department owning the document
    
    The document will be:
    1. Validated (MIME type, size, checksum)
    2. Stored in MinIO
    3. Queued for processing (OCR, NER, classification, etc.)
    """
    # TODO: Implement document upload
    # 1. Validate file (MIME, size)
    # 2. Compute checksum SHA-256
    # 3. Store in MinIO
    # 4. Create DB record
    # 5. Publish to Kafka for processing
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Document upload not yet implemented"
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Get document by ID"""
    # TODO: Implement get document
    # Check permissions (RBAC/ABAC)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get document not yet implemented"
    )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    doc_status: Optional[str] = Query(None, alias="status"),
    classification: Optional[str] = None,
    department: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    List documents with filters
    
    - **skip**: Pagination offset
    - **limit**: Max results (max 100)
    - **doc_status**: Filter by status
    - **classification**: Filter by classification
    - **department**: Filter by department
    """
    # TODO: Implement list documents with filters
    from fastapi import status as http_status
    raise HTTPException(
        status_code=http_status.HTTP_501_NOT_IMPLEMENTED,
        detail="List documents not yet implemented"
    )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_update: DocumentUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Update document metadata"""
    # TODO: Implement update document
    # Check permissions
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update document not yet implemented"
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete document
    
    Soft delete by default (status = archived)
    Physical delete only for authorized users
    """
    # TODO: Implement delete document
    # Check permissions
    # Soft delete by default
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Delete document not yet implemented"
    )


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Download original document file"""
    # TODO: Implement download from MinIO
    # Check permissions
    # Stream file from MinIO
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Download document not yet implemented"
    )


@router.get("/{document_id}/entities", response_model=List[EntityResponse])
async def get_document_entities(
    document_id: UUID,
    entity_type: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Get extracted entities (NER) from document"""
    # TODO: Implement get entities
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get entities not yet implemented"
    )


@router.get("/{document_id}/chunks", response_model=List[ChunkResponse])
async def get_document_chunks(
    document_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Get document chunks (for debugging/analysis)"""
    # TODO: Implement get chunks
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get chunks not yet implemented"
    )


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Reprocess document through the pipeline
    
    Useful when models are updated or errors occurred
    """
    # TODO: Implement reprocess
    # Publish to Kafka with reprocess flag
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Reprocess not yet implemented"
    )


# ============================================================================
# NUEVOS ENDPOINTS: INTEGRACIÓN CON ONTOLOGÍA OWL
# ============================================================================

@router.get("/{document_id}/classification/explanation", response_model=Dict[str, Any])
async def get_classification_explanation(
    document_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene explicación detallada de la clasificación del documento
    
    Incluye:
    - Clasificación ML con confianza
    - Clasificación ontológica (OWL) con keywords
    - Evidencias textuales (extractos)
    - Validación de metadatos contra restricciones OWL
    - Nivel de riesgo inferido
    - Jerarquía ontológica completa
    
    **Ejemplo de respuesta:**
    ```json
    {
      "category": "FINANCIAL",
      "confidence": 0.92,
      "method": "transformer_model+ontology",
      "matched_keywords": ["factura", "iva", "importe"],
      "evidence": [
        {
          "keyword": "factura",
          "excerpt": "...FACTURA Nº 2024-001...",
          "source": "ontology"
        }
      ],
      "ontology": {
        "class_name": "PrestamoHipotecario",
        "class_label": "Préstamo Hipotecario",
        "confidence": 0.88
      },
      "validation": {
        "is_valid": false,
        "errors": ["importeFinanciado debe ser >= 30000"],
        "required_fields": ["tieneCliente", "requiereValoracion"]
      },
      "risk": {
        "level": "ALTO",
        "method": "ontology_inference"
      }
    }
    ```
    """
    # TODO: Obtener documento de BD
    # document = await db.get(Document, document_id)
    # if not document:
    #     raise HTTPException(status_code=404, detail="Document not found")
    
    # text = await get_document_text(document_id)  # Helper function
    # explanation = classification_service.get_classification_explanation(document, text)
    # return explanation
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Classification explanation endpoint - implementation pending database integration"
    )


@router.get("/{document_id}/ontology/hierarchy", response_model=Dict[str, Any])
async def get_document_ontology_hierarchy(
    document_id: UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la jerarquía ontológica completa para el documento
    
    Incluye:
    - Información de la clase OWL asignada
    - Ancestros (clases padre)
    - Hermanos (clases del mismo nivel)
    - Descendientes (subclases)
    - Documentos relacionados semánticamente
    - Regulaciones de compliance aplicables
    
    **Ejemplo de respuesta:**
    ```json
    {
      "class_info": {
        "label": "Préstamo Hipotecario",
        "comment": "Contrato de financiación con garantía inmobiliaria",
        "parent_classes": ["ContratoFinanciacion", "DocumentoContractual"],
        "properties": {
          "nivelRiesgoBase": ["BAJO"],
          "importeMinimo": [30000]
        }
      },
      "hierarchy": {
        "uri": "http://tefinancia.es/ontology#PrestamoHipotecario",
        "name": "PrestamoHipotecario",
        "label": "Préstamo Hipotecario",
        "children": []
      },
      "related_documents": [
        {
          "property": "requiereDocumento",
          "target": "DNI"
        },
        {
          "property": "requiereValoracion",
          "target": "Valoracion"
        }
      ],
      "compliance_regulations": [
        "Ley Hipotecaria 5/2019",
        "MiFID II",
        "Ley de Crédito Inmobiliario"
      ]
    }
    ```
    """
    # TODO: Obtener documento de BD
    # document = await db.get(Document, document_id)
    # if not document:
    #     raise HTTPException(status_code=404, detail="Document not found")
    
    # hierarchy = await classification_service.get_ontology_hierarchy(document)
    # if not hierarchy:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="No ontology classification found for this document"
    #     )
    
    # return hierarchy
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Ontology hierarchy endpoint - implementation pending database integration"
    )


@router.post("/{document_id}/reclassify", response_model=Dict[str, Any])
async def reclassify_document_intelligent(
    document_id: UUID,
    mode: str = Query(
        "intelligent",
        description="Modo de clasificación: fast, ml, precise, intelligent"
    ),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Reclasifica un documento usando el pipeline triple inteligente
    
    **Modos de clasificación:**
    - `fast`: Solo taxonomía JSON (ultra rápido, ~10ms)
    - `ml`: Taxonomía + ML transformers (rápido, ~100ms)
    - `precise`: Taxonomía + ML + Ontología OWL (preciso, ~500ms)
    - `intelligent`: Adaptativo según confianza (recomendado)
    
    **Pipeline inteligente (modo intelligent):**
    1. FASE RÁPIDA: Taxonomía JSON con keywords jerárquicos
    2. FASE ML: Transformers si confianza < 80%
    3. FASE PRECISA: Ontología OWL si confianza < 85%
    4. VALIDACIÓN: Restricciones OWL
    5. INFERENCIA: Nivel de riesgo
    
    **Optimización:**
    El modo `intelligent` optimiza automáticamente:
    - Si taxonomía tiene confianza > 80% → Skip ML (ahorra 90ms)
    - Si taxonomía+ML tiene confianza > 85% → Skip OWL (ahorra 400ms)
    - Si confianza final < 85% → Usa todas las fases para máxima precisión
    
    **Retorna:**
    - Clasificación multi-fuente (taxonomy + ml + ontology)
    - Confianza combinada con blending adaptativo
    - Fases utilizadas para transparencia
    - Validación de metadatos OWL
    - Riesgo inferido con reglas de negocio
    
    **Ejemplo de respuesta (modo intelligent):**
    ```json
    {
      "category": "FINANCIAL",
      "confidence": 0.91,
      "method": "taxonomy+ml+ontology",
      "phases_used": ["taxonomy", "ml", "ontology"],
      "classification_mode": "intelligent",
      "taxonomy_class": "PrestamoHipotecario",
      "taxonomy_label": "Préstamo Hipotecario",
      "ml_category": "FINANCIAL",
      "ml_confidence": 0.87,
      "ontology_class": "PrestamoHipotecario",
      "ontology_label": "Préstamo Hipotecario",
      "ontology_confidence": 0.93,
      "matched_keywords": ["préstamo hipotecario", "hipoteca", "vivienda"],
      "metadata_validation": {
        "is_valid": false,
        "errors": ["importeFinanciado debe ser >= 30000"],
        "required_fields": ["tieneCliente", "requiereValoracion"]
      },
      "inferred_risk_level": "ALTO"
    }
    ```
    
    **Casos de uso:**
    - **fast**: Clasificación masiva de miles de documentos
    - **ml**: Balance velocidad/precisión para apps interactivas
    - **precise**: Documentos críticos que requieren máxima precisión
    - **intelligent**: Default recomendado - adapta automáticamente
    """
    # TODO: Obtener documento de BD
    # document = await db.get(Document, document_id)
    # if not document:
    #     raise HTTPException(status_code=404, detail="Document not found")
    
    # Validar modo
    valid_modes = ["fast", "ml", "precise", "intelligent"]
    if mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode '{mode}'. Must be one of: {', '.join(valid_modes)}"
        )
    
    # text = await get_document_text(document_id)
    # result = await classification_service.classify_document(
    #     document, text, db, mode=mode
    # )
    
    # return result
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Reclassify endpoint - implementation pending database integration"
    )
