"""
API REST para operaciones con la ontología OWL.
Sprint 2 & 3: Endpoints para consultas SPARQL, inferencia y validación semántica.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from ...services.ontology_service import ontology_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ontology",
    tags=["ontology"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class ClassifyDocumentRequest(BaseModel):
    """Request para clasificar un documento usando la ontología."""
    content: str = Field(..., description="Contenido del documento a clasificar")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadatos del documento")
    
    class Config:
        schema_extra = {
            "example": {
                "content": "Contrato de préstamo hipotecario con garantía inmobiliaria...",
                "metadata": {
                    "importeFinanciado": 200000,
                    "ltv": 80.0,
                    "plazoMeses": 240
                }
            }
        }


class ClassifyDocumentResponse(BaseModel):
    """Response de clasificación de documento."""
    class_uri: str = Field(..., description="URI de la clase OWL asignada")
    class_name: str = Field(..., description="Nombre de la clase")
    class_label: str = Field(..., description="Etiqueta en español")
    confidence: float = Field(..., ge=0, le=1, description="Nivel de confianza (0-1)")
    matched_keywords: List[str] = Field(..., description="Keywords que coincidieron")
    class_info: Dict[str, Any] = Field(..., description="Información adicional de la clase")


class ValidateMetadataRequest(BaseModel):
    """Request para validar metadatos contra restricciones OWL."""
    class_name: str = Field(..., description="Nombre de la clase OWL")
    metadata: Dict[str, Any] = Field(..., description="Metadatos a validar")
    
    class Config:
        schema_extra = {
            "example": {
                "class_name": "PrestamoHipotecario",
                "metadata": {
                    "importeFinanciado": 200000,
                    "tae": 3.5,
                    "plazoMeses": 240,
                    "ltv": 80.0
                }
            }
        }


class ValidateMetadataResponse(BaseModel):
    """Response de validación de metadatos."""
    is_valid: bool = Field(..., description="¿Los metadatos son válidos?")
    errors: List[str] = Field(..., description="Lista de errores de validación")
    required_fields: List[str] = Field(..., description="Campos requeridos por la clase")
    missing_fields: List[str] = Field(..., description="Campos requeridos que faltan")


class InferRiskRequest(BaseModel):
    """Request para inferir nivel de riesgo."""
    class_name: str = Field(..., description="Nombre de la clase OWL")
    metadata: Dict[str, Any] = Field(..., description="Metadatos del documento")
    
    class Config:
        schema_extra = {
            "example": {
                "class_name": "PrestamoHipotecario",
                "metadata": {
                    "importeFinanciado": 250000,
                    "ltv": 85.0,
                    "tae": 4.2,
                    "plazoMeses": 300
                }
            }
        }


class InferRiskResponse(BaseModel):
    """Response de inferencia de riesgo."""
    risk_level: str = Field(..., description="Nivel de riesgo inferido (BAJO, MEDIO, ALTO)")
    base_risk: str = Field(..., description="Riesgo base de la clase")
    applied_rules: List[str] = Field(..., description="Reglas de inferencia aplicadas")
    explanation: str = Field(..., description="Explicación del nivel de riesgo")


class SPARQLQueryRequest(BaseModel):
    """Request para ejecutar consulta SPARQL."""
    query: str = Field(..., description="Consulta SPARQL a ejecutar")
    
    class Config:
        schema_extra = {
            "example": {
                "query": """
                    PREFIX tf: <http://tefinancia.es/ontology#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    
                    SELECT ?class ?label ?riskLevel WHERE {
                        ?class rdfs:subClassOf tf:ContratoFinanciacion .
                        ?class rdfs:label ?label .
                        ?class tf:nivelRiesgoBase ?riskLevel .
                    }
                """
            }
        }


class SPARQLQueryResponse(BaseModel):
    """Response de consulta SPARQL."""
    results: List[Dict[str, Any]] = Field(..., description="Resultados de la consulta")
    count: int = Field(..., description="Número de resultados")


class ClassInfoResponse(BaseModel):
    """Response con información de una clase OWL."""
    uri: str = Field(..., description="URI de la clase")
    label: str = Field(..., description="Etiqueta en español")
    comment: Optional[str] = Field(None, description="Comentario/descripción")
    parent_classes: List[str] = Field(..., description="Clases padre")
    properties: Dict[str, List[str]] = Field(..., description="Propiedades de la clase")
    required_fields: List[str] = Field(..., description="Campos requeridos")
    related_documents: List[Dict[str, str]] = Field(..., description="Documentos relacionados")
    compliance_regulations: List[str] = Field(..., description="Regulaciones aplicables")


class HierarchyNode(BaseModel):
    """Nodo del árbol de jerarquía."""
    uri: str = Field(..., description="URI de la clase")
    name: str = Field(..., description="Nombre de la clase")
    label: str = Field(..., description="Etiqueta en español")
    children: List['HierarchyNode'] = Field(default=[], description="Subclases")


# Para soporte de referencias recursivas
HierarchyNode.update_forward_refs()


class HierarchyResponse(BaseModel):
    """Response con jerarquía de clases."""
    root: HierarchyNode = Field(..., description="Nodo raíz de la jerarquía")
    total_classes: int = Field(..., description="Número total de clases")


class OntologyStatsResponse(BaseModel):
    """Response con estadísticas de la ontología."""
    total_triples: int = Field(..., description="Número total de triples RDF")
    total_classes: int = Field(..., description="Número de clases OWL")
    total_object_properties: int = Field(..., description="Número de ObjectProperties")
    total_datatype_properties: int = Field(..., description="Número de DatatypeProperties")


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/classify", response_model=ClassifyDocumentResponse)
async def classify_document(request: ClassifyDocumentRequest):
    """
    Clasifica un documento usando la ontología OWL.
    
    Utiliza keywords definidas en la ontología (tf:keyword) para encontrar
    la clase más apropiada basándose en el contenido del documento.
    
    **Proceso:**
    1. Extrae keywords de las clases en la ontología
    2. Busca coincidencias en el contenido del documento
    3. Calcula confianza basada en número de coincidencias
    4. Retorna la clase con mayor confianza
    """
    try:
        result = ontology_service.classify_document(
            content=request.content,
            metadata=request.metadata
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No se pudo clasificar el documento. No se encontraron coincidencias con la ontología."
            )
        
        # Obtener información adicional de la clase
        class_info = ontology_service.get_class_info(result["class_uri"])
        
        return ClassifyDocumentResponse(
            class_uri=result["class_uri"],
            class_name=result["class_name"],
            class_label=result["class_label"],
            confidence=result["confidence"],
            matched_keywords=result["matched_keywords"],
            class_info=class_info
        )
        
    except Exception as e:
        logger.error(f"Error clasificando documento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en clasificación: {str(e)}")


@router.post("/validate", response_model=ValidateMetadataResponse)
async def validate_metadata(request: ValidateMetadataRequest):
    """
    Valida metadatos contra restricciones OWL de una clase.
    
    **Validaciones:**
    - Campos requeridos (owl:minCardinality >= 1)
    - Rangos numéricos (importeMinimo/Maximo, plazoMinimo/Maximo)
    - Valores máximos (taeMaximo)
    - Tipos de datos
    
    **Ejemplo de restricciones:**
    - PrestamoHipotecario requiere: cliente, valoracion
    - PrestamoHipotecario.importeFinanciado >= 30000
    - PrestamoHipotecario.plazoMeses >= 60
    """
    try:
        # Construir URI de la clase
        class_uri = ontology_service.TF[request.class_name]
        
        # Validar metadatos
        is_valid, errors = ontology_service.validate_metadata(class_uri, request.metadata)
        
        # Obtener campos requeridos
        required_fields = ontology_service.get_required_fields(class_uri)
        
        # Identificar campos faltantes
        missing_fields = [
            field for field in required_fields
            if field not in request.metadata
        ]
        
        return ValidateMetadataResponse(
            is_valid=is_valid,
            errors=errors,
            required_fields=required_fields,
            missing_fields=missing_fields
        )
        
    except Exception as e:
        logger.error(f"Error validando metadatos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en validación: {str(e)}")


@router.post("/infer-risk", response_model=InferRiskResponse)
async def infer_risk_level(request: InferRiskRequest):
    """
    Infiere el nivel de riesgo basándose en reglas de la ontología.
    
    **Reglas de inferencia implementadas:**
    1. **LTV > 80%** → ALTO (préstamo con alta relación loan-to-value)
    2. **TAE > 10%** → ALTO (tasa anual elevada indica riesgo)
    3. **esSensible = true** → ALTO (datos personales sensibles)
    4. **LineaCredito** → ALTO (siempre alto riesgo)
    5. **plazo > 240 meses** → Upgrade BAJO a MEDIO
    
    **Proceso:**
    1. Obtiene riesgo base de la clase (tf:nivelRiesgoBase)
    2. Aplica reglas de inferencia secuencialmente
    3. Retorna nivel final y explicación
    """
    try:
        # Construir URI de la clase
        class_uri = ontology_service.TF[request.class_name]
        
        # Inferir nivel de riesgo
        risk_level = ontology_service.infer_risk_level(class_uri, request.metadata)
        
        # Obtener riesgo base
        class_info = ontology_service.get_class_info(class_uri)
        base_risk = class_info.get("properties", {}).get("nivelRiesgoBase", ["MEDIO"])[0]
        
        # Determinar reglas aplicadas
        applied_rules = []
        explanation_parts = [f"Riesgo base de {request.class_name}: {base_risk}"]
        
        if "ltv" in request.metadata and request.metadata["ltv"] > 80:
            applied_rules.append("LTV > 80%")
            explanation_parts.append("LTV superior al 80% aumenta el riesgo")
        
        if "tae" in request.metadata and request.metadata["tae"] > 10:
            applied_rules.append("TAE > 10%")
            explanation_parts.append("TAE elevada indica mayor riesgo")
        
        if request.metadata.get("esSensible"):
            applied_rules.append("Datos sensibles")
            explanation_parts.append("Documento contiene datos sensibles")
        
        if request.class_name == "LineaCredito":
            applied_rules.append("Línea de crédito")
            explanation_parts.append("Las líneas de crédito son alto riesgo por defecto")
        
        if "plazoMeses" in request.metadata and request.metadata["plazoMeses"] > 240:
            applied_rules.append("Plazo > 20 años")
            explanation_parts.append("Plazo muy largo aumenta exposición al riesgo")
        
        explanation = ". ".join(explanation_parts) + "."
        
        return InferRiskResponse(
            risk_level=risk_level,
            base_risk=base_risk,
            applied_rules=applied_rules,
            explanation=explanation
        )
        
    except Exception as e:
        logger.error(f"Error infiriendo riesgo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en inferencia: {str(e)}")


@router.post("/sparql", response_model=SPARQLQueryResponse)
async def execute_sparql_query(request: SPARQLQueryRequest):
    """
    Ejecuta una consulta SPARQL personalizada sobre la ontología.
    
    **Capacidades SPARQL:**
    - SELECT: Consultas de selección
    - FILTER: Filtros complejos
    - OPTIONAL: Patrones opcionales
    - Navegación de propiedades transitivas (rdfs:subClassOf*)
    
    **Prefijos disponibles:**
    ```
    PREFIX tf: <http://tefinancia.es/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    ```
    
    **Ejemplo de consulta:**
    ```sparql
    SELECT ?doc ?label WHERE {
        ?doc rdfs:subClassOf* tf:ContratoFinanciacion .
        ?doc rdfs:label ?label .
    }
    ```
    """
    try:
        results = ontology_service.query_sparql(request.query)
        
        return SPARQLQueryResponse(
            results=results,
            count=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error ejecutando SPARQL: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error en consulta SPARQL: {str(e)}"
        )


@router.get("/class/{class_name}", response_model=ClassInfoResponse)
async def get_class_information(class_name: str):
    """
    Obtiene información completa de una clase OWL.
    
    **Información retornada:**
    - URI y etiquetas
    - Clases padre (jerarquía)
    - Propiedades (ObjectProperty y DatatypeProperty)
    - Campos requeridos (restricciones de cardinalidad)
    - Documentos relacionados (relaciones semánticas)
    - Regulaciones aplicables (compliance)
    
    **Ejemplos de clases:**
    - Documento (raíz)
    - PrestamoHipotecario
    - DNI
    - Factura
    """
    try:
        # Construir URI de la clase
        class_uri = ontology_service.TF[class_name]
        
        # Obtener información básica
        class_info = ontology_service.get_class_info(class_uri)
        
        if not class_info:
            raise HTTPException(
                status_code=404,
                detail=f"Clase '{class_name}' no encontrada en la ontología"
            )
        
        # Obtener campos requeridos
        required_fields = ontology_service.get_required_fields(class_uri)
        
        # Obtener documentos relacionados
        related_docs = ontology_service.get_related_documents(class_uri)
        
        # Obtener regulaciones
        regulations = ontology_service.get_compliance_regulations(class_uri)
        
        return ClassInfoResponse(
            uri=str(class_uri),
            label=class_info.get("label", class_name),
            comment=class_info.get("comment"),
            parent_classes=class_info.get("parent_classes", []),
            properties=class_info.get("properties", {}),
            required_fields=required_fields,
            related_documents=related_docs,
            compliance_regulations=regulations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo información de clase: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/hierarchy", response_model=HierarchyResponse)
async def get_ontology_hierarchy(
    root_class: Optional[str] = Query(
        default=None,
        description="Clase raíz (por defecto: Documento)"
    )
):
    """
    Obtiene la jerarquía completa de clases OWL.
    
    **Estructura:**
    - Árbol recursivo con relaciones rdfs:subClassOf
    - Incluye URI, nombre y etiquetas
    - Navegación desde clase raíz especificada
    
    **Ejemplo de jerarquía:**
    ```
    Documento
    ├── DocumentoContractual
    │   ├── ContratoFinanciacion
    │   │   ├── PrestamoHipotecario
    │   │   ├── PrestamoPersonal
    │   │   └── LineaCredito
    │   └── ContratoTrabajo
    ├── DocumentoIdentidad
    │   ├── DNI
    │   └── Pasaporte
    └── DocumentoFinanciero
        ├── Factura
        └── Nomina
    ```
    """
    try:
        # Si no se especifica root, usar Documento
        if not root_class:
            root_uri = ontology_service.TF.Documento
        else:
            root_uri = ontology_service.TF[root_class]
        
        # Obtener jerarquía
        hierarchy = ontology_service.get_hierarchy(root_uri)
        
        # Contar total de clases
        def count_classes(node):
            count = 1
            for child in node.get("children", []):
                count += count_classes(child)
            return count
        
        total_classes = count_classes(hierarchy)
        
        # Convertir a modelo Pydantic
        def build_hierarchy_node(node_dict):
            return HierarchyNode(
                uri=node_dict["uri"],
                name=node_dict["name"],
                label=node_dict["label"],
                children=[build_hierarchy_node(child) for child in node_dict.get("children", [])]
            )
        
        root_node = build_hierarchy_node(hierarchy)
        
        return HierarchyResponse(
            root=root_node,
            total_classes=total_classes
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo jerarquía: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/statistics", response_model=OntologyStatsResponse)
async def get_ontology_statistics():
    """
    Obtiene estadísticas de la ontología OWL.
    
    **Métricas incluidas:**
    - Total de triples RDF en el grafo
    - Número de clases OWL definidas
    - Número de ObjectProperties (relaciones entre clases)
    - Número de DatatypeProperties (propiedades de datos)
    
    **Utilidad:**
    - Monitoreo de complejidad de la ontología
    - Validación de integridad
    - Análisis de cobertura semántica
    """
    try:
        stats = ontology_service.get_statistics()
        
        return OntologyStatsResponse(
            total_triples=stats["total_triples"],
            total_classes=stats["total_classes"],
            total_object_properties=stats["total_object_properties"],
            total_datatype_properties=stats["total_datatype_properties"]
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================================================================
# ENDPOINTS ADICIONALES DE UTILIDAD
# ============================================================================

@router.get("/classes", response_model=List[Dict[str, str]])
async def list_all_classes(
    include_subclasses_of: Optional[str] = Query(
        default=None,
        description="Filtrar por superclase"
    )
):
    """
    Lista todas las clases OWL disponibles.
    
    Opcionalmente filtra por superclase usando rdfs:subClassOf.
    """
    try:
        if include_subclasses_of:
            parent_uri = ontology_service.TF[include_subclasses_of]
            subclasses = ontology_service.get_subclasses(parent_uri, direct_only=False)
            
            classes = []
            for class_uri in subclasses:
                info = ontology_service.get_class_info(class_uri)
                classes.append({
                    "uri": str(class_uri),
                    "name": class_uri.split("#")[-1],
                    "label": info.get("label", "")
                })
        else:
            # Query SPARQL para todas las clases
            query = """
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                
                SELECT DISTINCT ?class ?label WHERE {
                    ?class rdf:type owl:Class .
                    OPTIONAL { ?class rdfs:label ?label }
                }
                ORDER BY ?label
            """
            results = ontology_service.query_sparql(query)
            classes = [
                {
                    "uri": r["class"],
                    "name": r["class"].split("#")[-1],
                    "label": r.get("label", "")
                }
                for r in results
            ]
        
        return classes
        
    except Exception as e:
        logger.error(f"Error listando clases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Verifica que la ontología está cargada correctamente.
    """
    try:
        stats = ontology_service.get_statistics()
        
        return {
            "status": "healthy",
            "ontology_loaded": True,
            "total_classes": stats["total_classes"],
            "total_triples": stats["total_triples"]
        }
        
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return {
            "status": "unhealthy",
            "ontology_loaded": False,
            "error": str(e)
        }
