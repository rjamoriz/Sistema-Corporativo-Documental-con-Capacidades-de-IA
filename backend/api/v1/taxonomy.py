"""
Taxonomy API Endpoints
Sprint 1: API para navegación de taxonomía jerárquica
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from backend.services.taxonomy_service import taxonomy_service


router = APIRouter(prefix="/taxonomy", tags=["Taxonomy"])


# --- Response Models ---

class TaxonomyClass(BaseModel):
    """Información básica de una clase"""
    id: str
    label: str
    level: int
    description: Optional[str] = None


class TaxonomyClassDetail(TaxonomyClass):
    """Información detallada de una clase"""
    parent: Optional[str] = None
    children: List[str] = []
    required_fields: List[str] = []
    optional_fields: List[str] = []
    retention_years: int
    risk_level: str
    is_sensitive: bool = False
    keywords: List[str] = []
    compliance_regulations: List[str] = []
    validation_rules: Optional[Dict] = None
    related_documents: List[str] = []
    path: str


class TaxonomyHierarchy(BaseModel):
    """Estructura jerárquica de la taxonomía"""
    id: str
    label: str
    level: int
    description: Optional[str]
    children: List['TaxonomyHierarchy'] = []


class ClassificationResult(BaseModel):
    """Resultado de clasificación por keywords"""
    class_id: str
    label: str
    path: str
    confidence: float
    matches: int
    method: str


class MetadataValidation(BaseModel):
    """Resultado de validación de metadatos"""
    valid: bool
    errors: List[str] = []
    class_id: str
    class_label: str


class TaxonomyStatistics(BaseModel):
    """Estadísticas de la taxonomía"""
    total_classes: int
    classes_by_level: Dict[str, int]
    classes_by_risk: Dict[str, int]
    sensitive_classes: int
    max_depth: int
    leaf_classes: int


# Permitir referencias circulares en TaxonomyHierarchy
TaxonomyHierarchy.model_rebuild()


# --- Endpoints ---

@router.get("/", summary="Obtener información general de la taxonomía")
async def get_taxonomy_info():
    """
    Obtiene información general sobre la taxonomía
    
    Returns:
        Información básica y estadísticas
    """
    stats = taxonomy_service.get_statistics()
    
    return {
        "name": "TeFinancia Corporate Taxonomy",
        "version": "1.0.0",
        "type": "hierarchical",
        "max_levels": 3,
        "description": "Taxonomía jerárquica de 3 niveles para documentos corporativos",
        "statistics": stats
    }


@router.get("/hierarchy", response_model=TaxonomyHierarchy, summary="Obtener jerarquía completa")
async def get_full_hierarchy():
    """
    Obtiene la jerarquía completa de la taxonomía como árbol
    
    Returns:
        Árbol jerárquico con todas las clases
    """
    hierarchy = taxonomy_service.get_hierarchy()
    
    if not hierarchy:
        raise HTTPException(status_code=404, detail="Taxonomía no disponible")
    
    return hierarchy


@router.get("/class/{class_id}", response_model=TaxonomyClassDetail, summary="Obtener detalles de una clase")
async def get_class_details(class_id: str):
    """
    Obtiene información detallada de una clase específica
    
    Args:
        class_id: Identificador de la clase (ej: "PRESTAMO_PERSONAL")
    
    Returns:
        Información completa de la clase
    """
    node = taxonomy_service.get_class(class_id)
    
    if not node:
        raise HTTPException(status_code=404, detail=f"Clase no encontrada: {class_id}")
    
    return {
        "id": class_id,
        "label": node.get("label"),
        "level": node.get("level"),
        "description": node.get("description"),
        "parent": node.get("parent"),
        "children": node.get("children", []),
        "required_fields": node.get("required_fields", []),
        "optional_fields": node.get("optional_fields", []),
        "retention_years": node.get("retention_years", 5),
        "risk_level": node.get("risk_level", "MEDIO"),
        "is_sensitive": node.get("is_sensitive", False),
        "keywords": node.get("keywords", []),
        "compliance_regulations": node.get("compliance_regulations", []),
        "validation_rules": node.get("validation_rules"),
        "related_documents": node.get("related_documents", []),
        "path": taxonomy_service.get_path(class_id)
    }


@router.get("/class/{class_id}/children", response_model=List[TaxonomyClass], summary="Obtener clases hijas")
async def get_class_children(class_id: str):
    """
    Obtiene las clases hijas directas de una clase
    
    Args:
        class_id: Identificador de la clase padre
    
    Returns:
        Lista de clases hijas
    """
    children = taxonomy_service.get_children(class_id)
    
    if not children and not taxonomy_service.get_class(class_id):
        raise HTTPException(status_code=404, detail=f"Clase no encontrada: {class_id}")
    
    return children


@router.get("/class/{class_id}/parent", response_model=Optional[TaxonomyClass], summary="Obtener clase padre")
async def get_class_parent(class_id: str):
    """
    Obtiene la clase padre de una clase
    
    Args:
        class_id: Identificador de la clase
    
    Returns:
        Información de la clase padre o None si es raíz
    """
    if not taxonomy_service.get_class(class_id):
        raise HTTPException(status_code=404, detail=f"Clase no encontrada: {class_id}")
    
    return taxonomy_service.get_parent(class_id)


@router.get("/class/{class_id}/ancestors", response_model=List[TaxonomyClass], summary="Obtener ancestros")
async def get_class_ancestors(class_id: str):
    """
    Obtiene todos los ancestros (padre, abuelo, etc.) de una clase
    
    Args:
        class_id: Identificador de la clase
    
    Returns:
        Lista de ancestros desde el más cercano al más lejano
    """
    if not taxonomy_service.get_class(class_id):
        raise HTTPException(status_code=404, detail=f"Clase no encontrada: {class_id}")
    
    return taxonomy_service.get_ancestors(class_id)


@router.get("/class/{class_id}/path", summary="Obtener path completo")
async def get_class_path(class_id: str):
    """
    Obtiene el path completo de una clase
    
    Args:
        class_id: Identificador de la clase
    
    Returns:
        Path en formato "Documento > Contractual > Financiación > Préstamo Personal"
    """
    if not taxonomy_service.get_class(class_id):
        raise HTTPException(status_code=404, detail=f"Clase no encontrada: {class_id}")
    
    path = taxonomy_service.get_path(class_id)
    
    return {
        "class_id": class_id,
        "path": path,
        "depth": len(path.split(" > ")) - 1
    }


@router.get("/search", response_model=List[TaxonomyClass], summary="Buscar clases por keyword")
async def search_classes(
    keyword: str = Query(..., description="Palabra clave a buscar", min_length=3)
):
    """
    Busca clases que contengan una palabra clave
    
    Args:
        keyword: Palabra clave (mínimo 3 caracteres)
    
    Returns:
        Lista de clases que coinciden con la búsqueda
    """
    results = taxonomy_service.search_by_keyword(keyword)
    
    if not results:
        return []
    
    return results


@router.post("/classify", response_model=List[ClassificationResult], summary="Clasificar texto por keywords")
async def classify_text(
    text: str = Query(..., description="Texto a clasificar", min_length=10),
    top_n: int = Query(3, ge=1, le=10, description="Número de resultados")
):
    """
    Clasifica un texto basándose en coincidencias de keywords
    
    Args:
        text: Texto a clasificar (mínimo 10 caracteres)
        top_n: Número de resultados a devolver (1-10)
    
    Returns:
        Lista de clasificaciones ordenadas por relevancia
    """
    results = taxonomy_service.classify_by_keywords(text, top_n=top_n)
    
    if not results:
        return []
    
    return results


@router.post("/validate", response_model=MetadataValidation, summary="Validar metadatos")
async def validate_metadata(
    class_id: str = Query(..., description="Identificador de la clase"),
    metadata: Dict = Query(..., description="Metadatos a validar")
):
    """
    Valida que los metadatos cumplan con los requisitos de una clase
    
    Args:
        class_id: Identificador de la clase
        metadata: Diccionario con metadatos del documento
    
    Returns:
        Resultado de validación con errores si los hay
    """
    node = taxonomy_service.get_class(class_id)
    
    if not node:
        raise HTTPException(status_code=404, detail=f"Clase no encontrada: {class_id}")
    
    is_valid, errors = taxonomy_service.validate_metadata(class_id, metadata)
    
    return {
        "valid": is_valid,
        "errors": errors,
        "class_id": class_id,
        "class_label": node.get("label")
    }


@router.get("/leaves", response_model=List[TaxonomyClass], summary="Obtener clases hoja")
async def get_leaf_classes():
    """
    Obtiene todas las clases hoja (sin hijos) - las más específicas
    
    Returns:
        Lista de clases hoja
    """
    leaves = taxonomy_service.get_leaf_classes()
    return leaves


@router.get("/statistics", response_model=TaxonomyStatistics, summary="Obtener estadísticas")
async def get_taxonomy_statistics():
    """
    Obtiene estadísticas de la taxonomía
    
    Returns:
        Estadísticas generales
    """
    stats = taxonomy_service.get_statistics()
    
    # Convertir keys de level a string para JSON serialization
    stats["classes_by_level"] = {str(k): v for k, v in stats["classes_by_level"].items()}
    
    return stats


@router.get("/risk/{risk_level}", summary="Obtener clases por nivel de riesgo")
async def get_classes_by_risk(
    risk_level: str = Query(..., description="Nivel de riesgo: BAJO, MEDIO, ALTO")
):
    """
    Obtiene todas las clases con un nivel de riesgo específico
    
    Args:
        risk_level: Nivel de riesgo (BAJO, MEDIO, ALTO)
    
    Returns:
        Lista de clases con ese nivel de riesgo
    """
    risk_level = risk_level.upper()
    
    if risk_level not in ["BAJO", "MEDIO", "ALTO"]:
        raise HTTPException(status_code=400, detail="Nivel de riesgo debe ser: BAJO, MEDIO o ALTO")
    
    results = []
    
    for class_id, node in taxonomy_service.taxonomy.items():
        if node.get("risk_level") == risk_level:
            results.append({
                "id": class_id,
                "label": node.get("label"),
                "level": node.get("level"),
                "path": taxonomy_service.get_path(class_id)
            })
    
    return results


@router.get("/sensitive", summary="Obtener clases con datos sensibles")
async def get_sensitive_classes():
    """
    Obtiene todas las clases que contienen datos sensibles (GDPR)
    
    Returns:
        Lista de clases con datos sensibles
    """
    results = []
    
    for class_id, node in taxonomy_service.taxonomy.items():
        if node.get("is_sensitive"):
            results.append({
                "id": class_id,
                "label": node.get("label"),
                "level": node.get("level"),
                "path": taxonomy_service.get_path(class_id),
                "retention_years": node.get("retention_years"),
                "compliance_regulations": node.get("compliance_regulations", [])
            })
    
    return results


@router.get("/compliance/{regulation}", summary="Obtener clases por regulación")
async def get_classes_by_compliance(
    regulation: str = Query(..., description="Regulación (ej: GDPR, MiFID II)")
):
    """
    Obtiene todas las clases afectadas por una regulación específica
    
    Args:
        regulation: Nombre de la regulación
    
    Returns:
        Lista de clases sujetas a esa regulación
    """
    results = []
    
    for class_id, node in taxonomy_service.taxonomy.items():
        regulations = node.get("compliance_regulations", [])
        if regulation in regulations:
            results.append({
                "id": class_id,
                "label": node.get("label"),
                "level": node.get("level"),
                "path": taxonomy_service.get_path(class_id),
                "risk_level": node.get("risk_level"),
                "is_sensitive": node.get("is_sensitive", False)
            })
    
    return results
