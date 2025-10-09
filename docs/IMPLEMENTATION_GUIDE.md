# 🚀 Guía de Implementación - Mejoras RFP TeFinancia

**Fecha**: 9 de Octubre 2025  
**Proyecto**: FinancIA 2030  
**Versión**: 1.0

---

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Mejoras Quick-Win (1-2 sprints)](#mejoras-quick-win)
3. [Implementación Ontología](#implementación-ontología)
4. [Servidor MCP](#servidor-mcp)
5. [Validación Terceros](#validación-terceros)
6. [Plan de Acción Técnico](#plan-de-acción-técnico)

---

## 1. Resumen Ejecutivo

### Estado Actual vs RFP
- **Alineación global**: 92%
- **Gaps críticos identificados**: 3
- **Timeline a 100%**: 12 semanas
- **Esfuerzo estimado**: 480 horas

### Priorización de Mejoras

| Mejora | Impacto | Esfuerzo | ROI | Prioridad |
|--------|---------|----------|-----|-----------|
| **Ontología formal** | ALTO | 4 sem | 🟢 | P0 |
| **Servidor MCP** | MUY ALTO | 3 sem | 🟢🟢🟢 | P1 |
| **Validación terceros** | MEDIO | 3 sem | 🟢 | P0 |
| **GraphQL API** | BAJO | 2 sem | 🟡 | P2 |
| **Formatos adicionales** | BAJO | 2 sem | 🟡 | P2 |

---

## 2. Mejoras Quick-Win (1-2 sprints)

### 2.1 Mejora #1: Enriquecer Clasificación con Metadatos Ontológicos

**Esfuerzo**: 1 sprint (5 días)  
**Impacto**: ALTO - Mejora clasificación sin cambiar arquitectura

#### Archivos a Modificar

```bash
backend/services/classification_service.py
backend/models/database_models.py
backend/api/v1/documents.py
```

#### Cambios en `classification_service.py`

```python
# AÑADIR después de la línea 85
class ClassificationService:
    def __init__(self):
        # ... código existente ...
        
        # NUEVO: Jerarquía de conceptos (pre-ontología)
        self.concept_hierarchy = {
            DocumentClassification.FINANCIAL: {
                "parent": None,
                "children": ["INVOICE", "BUDGET", "LOAN", "CREDIT"],
                "required_fields": ["amount", "date", "parties"],
                "synonyms": ["financiero", "económico", "monetario"]
            },
            "LOAN": {
                "parent": DocumentClassification.FINANCIAL,
                "children": ["MORTGAGE_LOAN", "PERSONAL_LOAN", "BUSINESS_LOAN"],
                "required_fields": ["loan_amount", "interest_rate", "term"],
                "synonyms": ["préstamo", "crédito", "financiación"]
            },
            "MORTGAGE_LOAN": {
                "parent": "LOAN",
                "children": [],
                "required_fields": ["property_value", "appraisal"],
                "synonyms": ["hipoteca", "préstamo hipotecario"]
            }
            # ... más categorías
        }
    
    async def classify_document(self, document: Document, text: str, db: AsyncSession) -> Dict:
        """Clasificación mejorada con jerarquía"""
        # ... clasificación ML existente ...
        
        # NUEVO: Refinamiento jerárquico
        refined_classification = await self._refine_with_hierarchy(
            classification, text, document
        )
        
        # Guardar metadata enriquecida
        document.metadata_["concept_hierarchy"] = refined_classification["hierarchy"]
        document.metadata_["concept_level"] = refined_classification["level"]
        document.metadata_["missing_fields"] = refined_classification["missing"]
        
        return refined_classification
    
    async def _refine_with_hierarchy(self, base_classification: Dict, 
                                      text: str, document: Document) -> Dict:
        """Refina clasificación usando jerarquía de conceptos"""
        category = base_classification["category"]
        hierarchy_info = self.concept_hierarchy.get(category, {})
        
        # Detectar subcategoría más específica
        best_child = None
        max_confidence = 0.0
        
        for child in hierarchy_info.get("children", []):
            child_info = self.concept_hierarchy.get(child, {})
            synonyms = child_info.get("synonyms", [])
            
            # Contar coincidencias de sinónimos
            matches = sum(1 for syn in synonyms if syn.lower() in text.lower())
            confidence = matches / max(len(synonyms), 1)
            
            if confidence > max_confidence:
                max_confidence = confidence
                best_child = child
        
        # Validar campos obligatorios
        required = hierarchy_info.get("required_fields", [])
        missing_fields = [f for f in required 
                         if f not in document.metadata_]
        
        return {
            "category": best_child or category,
            "confidence": base_classification["confidence"] * (1 + max_confidence * 0.2),
            "hierarchy": [hierarchy_info.get("parent"), category, best_child],
            "level": "specific" if best_child else "general",
            "missing": missing_fields,
            "method": "hierarchical_refinement"
        }
```

#### Resultado Esperado
- ✅ Clasificación más específica (ej: "Préstamo Hipotecario" vs "Financiero")
- ✅ Validación de campos obligatorios por tipo
- ✅ Preparación para ontología formal
- ✅ Sin cambios en base de datos (usa metadata JSON)

---

### 2.2 Mejora #2: API Endpoint para Descubrimiento de Conceptos

**Esfuerzo**: 3 días  
**Impacto**: ALTO - Habilita exploración inteligente

#### Nuevo Archivo: `backend/api/v1/ontology.py`

```python
"""
API Endpoints para Descubrimiento Ontológico
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.services.classification_service import classification_service
from backend.models.schemas import ConceptInfo, ConceptHierarchy

router = APIRouter(prefix="/ontology", tags=["Ontology"])


@router.get("/concepts", response_model=List[ConceptInfo])
async def list_concepts(
    parent: Optional[str] = Query(None, description="Concepto padre"),
    level: Optional[int] = Query(None, ge=0, le=5, description="Nivel jerárquico")
):
    """
    Lista conceptos disponibles en la jerarquía
    
    Ejemplos:
    - GET /ontology/concepts → Todos los conceptos raíz
    - GET /ontology/concepts?parent=LOAN → Hijos de LOAN
    - GET /ontology/concepts?level=2 → Conceptos de nivel 2
    """
    hierarchy = classification_service.concept_hierarchy
    
    if parent:
        parent_info = hierarchy.get(parent, {})
        children = parent_info.get("children", [])
        concepts = [
            ConceptInfo(
                name=child,
                parent=parent,
                children=hierarchy.get(child, {}).get("children", []),
                required_fields=hierarchy.get(child, {}).get("required_fields", []),
                synonyms=hierarchy.get(child, {}).get("synonyms", [])
            )
            for child in children
        ]
    else:
        # Conceptos raíz (sin padre)
        concepts = [
            ConceptInfo(
                name=key,
                parent=info.get("parent"),
                children=info.get("children", []),
                required_fields=info.get("required_fields", []),
                synonyms=info.get("synonyms", [])
            )
            for key, info in hierarchy.items()
            if info.get("parent") is None
        ]
    
    return concepts


@router.get("/concepts/{concept_name}/hierarchy", response_model=ConceptHierarchy)
async def get_concept_hierarchy(concept_name: str):
    """
    Obtiene la jerarquía completa de un concepto
    
    Ejemplo:
    - GET /ontology/concepts/MORTGAGE_LOAN/hierarchy
    
    Retorna:
    {
        "concept": "MORTGAGE_LOAN",
        "ancestors": ["FINANCIAL", "LOAN"],
        "descendants": [],
        "siblings": ["PERSONAL_LOAN", "BUSINESS_LOAN"],
        "level": 3
    }
    """
    hierarchy = classification_service.concept_hierarchy
    
    # Construir ancestros
    ancestors = []
    current = concept_name
    while current:
        parent = hierarchy.get(current, {}).get("parent")
        if parent:
            ancestors.append(parent)
            current = parent
        else:
            break
    
    # Obtener hermanos
    if ancestors:
        parent = ancestors[0]
        siblings = hierarchy.get(parent, {}).get("children", [])
        siblings = [s for s in siblings if s != concept_name]
    else:
        siblings = []
    
    # Obtener descendientes
    descendants = []
    def get_all_children(node):
        children = hierarchy.get(node, {}).get("children", [])
        descendants.extend(children)
        for child in children:
            get_all_children(child)
    
    get_all_children(concept_name)
    
    return ConceptHierarchy(
        concept=concept_name,
        ancestors=ancestors,
        descendants=descendants,
        siblings=siblings,
        level=len(ancestors) + 1
    )


@router.get("/search")
async def search_concepts(
    query: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db)
):
    """
    Busca conceptos por término (sinónimos incluidos)
    
    Ejemplo:
    - GET /ontology/search?query=hipoteca
    
    Retorna conceptos que matchean en nombre o sinónimos
    """
    hierarchy = classification_service.concept_hierarchy
    query_lower = query.lower()
    
    matches = []
    for concept, info in hierarchy.items():
        # Buscar en nombre
        if query_lower in concept.lower():
            matches.append({
                "concept": concept,
                "match_type": "name",
                "relevance": 1.0
            })
            continue
        
        # Buscar en sinónimos
        synonyms = info.get("synonyms", [])
        for syn in synonyms:
            if query_lower in syn.lower():
                matches.append({
                    "concept": concept,
                    "match_type": "synonym",
                    "matched_term": syn,
                    "relevance": 0.8
                })
                break
    
    # Ordenar por relevancia
    matches.sort(key=lambda x: x["relevance"], reverse=True)
    
    return {
        "query": query,
        "total_matches": len(matches),
        "results": matches
    }
```

#### Schemas Necesarios (`backend/models/schemas.py`)

```python
# AÑADIR al final del archivo
class ConceptInfo(BaseModel):
    """Información de un concepto en la jerarquía"""
    name: str
    parent: Optional[str] = None
    children: List[str] = []
    required_fields: List[str] = []
    synonyms: List[str] = []


class ConceptHierarchy(BaseModel):
    """Jerarquía completa de un concepto"""
    concept: str
    ancestors: List[str]
    descendants: List[str]
    siblings: List[str]
    level: int
```

#### Registrar Router (`backend/api/v1/__init__.py`)

```python
# AÑADIR al final
from backend.api.v1 import ontology

# En el diccionario de routers
routers = [
    # ... routers existentes ...
    ontology.router,  # NUEVO
]
```

---

### 2.3 Mejora #3: Widget Frontend para Exploración Ontológica

**Esfuerzo**: 3 días  
**Impacto**: MEDIO - Mejora UX descubrimiento

#### Nuevo Componente: `frontend/src/components/OntologyExplorer.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { Search, ChevronRight, ChevronDown, Tag } from 'lucide-react';

interface Concept {
  name: string;
  parent: string | null;
  children: string[];
  required_fields: string[];
  synonyms: string[];
}

export default function OntologyExplorer() {
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // Cargar conceptos raíz al montar
  useEffect(() => {
    fetch('/api/v1/ontology/concepts')
      .then(res => res.json())
      .then(data => setConcepts(data));
  }, []);

  // Búsqueda de conceptos
  useEffect(() => {
    if (searchQuery.length >= 2) {
      fetch(`/api/v1/ontology/search?query=${encodeURIComponent(searchQuery)}`)
        .then(res => res.json())
        .then(data => setSearchResults(data.results || []));
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const toggleNode = async (conceptName: string) => {
    const newExpanded = new Set(expandedNodes);
    
    if (newExpanded.has(conceptName)) {
      newExpanded.delete(conceptName);
    } else {
      newExpanded.add(conceptName);
      
      // Cargar hijos si no están cargados
      const response = await fetch(`/api/v1/ontology/concepts?parent=${conceptName}`);
      const children = await response.json();
      
      // Añadir hijos a conceptos
      setConcepts(prev => {
        const existing = new Set(prev.map(c => c.name));
        const newConcepts = children.filter((c: Concept) => !existing.has(c.name));
        return [...prev, ...newConcepts];
      });
    }
    
    setExpandedNodes(newExpanded);
  };

  const renderConcept = (concept: Concept, level: number = 0) => {
    const hasChildren = concept.children.length > 0;
    const isExpanded = expandedNodes.has(concept.name);

    return (
      <div key={concept.name} style={{ marginLeft: `${level * 20}px` }}>
        <div
          className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded cursor-pointer"
          onClick={() => hasChildren && toggleNode(concept.name)}
        >
          {hasChildren ? (
            isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
          ) : (
            <span style={{ width: 16 }} />
          )}
          
          <Tag size={16} className="text-blue-500" />
          
          <span className="font-medium">{concept.name}</span>
          
          {concept.synonyms.length > 0 && (
            <span className="text-xs text-gray-500">
              ({concept.synonyms.slice(0, 2).join(', ')})
            </span>
          )}
          
          {concept.required_fields.length > 0 && (
            <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded">
              {concept.required_fields.length} campos
            </span>
          )}
        </div>

        {isExpanded && concept.children.map(childName => {
          const childConcept = concepts.find(c => c.name === childName);
          return childConcept ? renderConcept(childConcept, level + 1) : null;
        })}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Explorador de Conceptos</h3>
      
      {/* Barra de búsqueda */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Buscar conceptos (ej: hipoteca, préstamo...)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-lg"
        />
      </div>

      {/* Resultados de búsqueda */}
      {searchResults.length > 0 && (
        <div className="mb-4 p-3 bg-blue-50 rounded">
          <p className="text-sm font-medium mb-2">
            {searchResults.length} resultado(s) encontrado(s)
          </p>
          {searchResults.map((result, idx) => (
            <div key={idx} className="text-sm py-1">
              <span className="font-medium">{result.concept}</span>
              {result.matched_term && (
                <span className="text-gray-600"> (sinónimo: {result.matched_term})</span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Árbol de conceptos */}
      <div className="border rounded p-2 max-h-96 overflow-y-auto">
        {concepts
          .filter(c => c.parent === null)
          .map(concept => renderConcept(concept))}
      </div>
    </div>
  );
}
```

---

## 3. Implementación Ontología

### 3.1 Fase 1: Diseño (2 semanas)

#### Dependencias Nuevas

```bash
# requirements.txt - AÑADIR
rdflib==7.0.0              # Manipulación RDF/OWL
owlready2==0.46            # Ontologías OWL en Python
SPARQLWrapper==2.0.0       # Cliente SPARQL
```

#### Instalar

```bash
pip install rdflib owlready2 SPARQLWrapper
```

#### Estructura de Archivos Nueva

```
backend/ontology/
├── __init__.py
├── ontology_service.py       # Servicio principal
├── sparql_queries.py          # Queries SPARQL predefinidas
└── models/
    └── tefinancia_base.owl    # Ontología base

infrastructure/triple-store/
├── docker-compose.jena.yml    # Apache Jena Fuseki
└── config/
    └── fuseki-config.ttl      # Configuración Fuseki
```

### 3.2 Servicio Ontología Básico

#### `backend/ontology/ontology_service.py`

```python
"""
Servicio de Ontología - FinancIA 2030
Integración con OWL/SKOS y triple store
"""
from typing import List, Dict, Optional
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from SPARQLWrapper import SPARQLWrapper, JSON
import logging

logger = logging.getLogger(__name__)

# Namespaces
TF = Namespace("http://tefinancia.es/onto#")
FIBO = Namespace("https://spec.edmcouncil.org/fibo/ontology/FBC/")


class OntologyService:
    """Servicio para operaciones ontológicas"""
    
    def __init__(self, sparql_endpoint: str = "http://localhost:3030/financia"):
        self.graph = Graph()
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.load_ontology()
    
    def load_ontology(self):
        """Carga ontología base desde archivo OWL"""
        try:
            self.graph.parse("backend/ontology/models/tefinancia_base.owl", format="xml")
            logger.info(f"Ontología cargada: {len(self.graph)} triples")
        except Exception as e:
            logger.warning(f"No se pudo cargar ontología: {e}")
    
    async def classify_document(self, content: str, entities: List[str]) -> Dict:
        """
        Clasifica documento usando razonamiento ontológico
        
        Args:
            content: Texto del documento
            entities: Entidades extraídas por NER
            
        Returns:
            Dict con clase ontológica y nivel de confianza
        """
        query = f"""
        PREFIX tf: <http://tefinancia.es/onto#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?class ?label ?pattern WHERE {{
            ?class rdfs:subClassOf* tf:Documento .
            ?class rdfs:label ?label .
            ?class tf:contenidoPatron ?pattern .
        }}
        """
        
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        
        # Scoring por coincidencias de patrones
        best_match = None
        max_score = 0.0
        
        content_lower = content.lower()
        
        for result in results["results"]["bindings"]:
            class_uri = result["class"]["value"]
            pattern = result["pattern"]["value"]
            
            # Contar coincidencias de patrón
            matches = sum(1 for term in pattern.split("|") 
                         if term.lower() in content_lower)
            
            # Boost si entidades matchean
            entity_matches = sum(1 for ent in entities 
                                if ent.lower() in pattern.lower())
            
            score = matches + (entity_matches * 0.5)
            
            if score > max_score:
                max_score = score
                best_match = {
                    "class": class_uri.split("#")[-1],
                    "label": result["label"]["value"],
                    "confidence": min(1.0, score / 10),
                    "method": "ontology_reasoning"
                }
        
        return best_match or {
            "class": "Documento",
            "label": "Documento General",
            "confidence": 0.5,
            "method": "default"
        }
    
    async def get_required_fields(self, doc_class: str) -> List[str]:
        """Obtiene campos obligatorios para una clase de documento"""
        query = f"""
        PREFIX tf: <http://tefinancia.es/onto#>
        
        SELECT ?property WHERE {{
            tf:{doc_class} tf:requiereCampo ?property .
        }}
        """
        
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        
        return [r["property"]["value"].split("#")[-1] 
                for r in results["results"]["bindings"]]
    
    async def infer_risk_level(self, doc_class: str, metadata: Dict) -> str:
        """Infiere nivel de riesgo base según ontología"""
        query = f"""
        PREFIX tf: <http://tefinancia.es/onto#>
        
        SELECT ?riskLevel WHERE {{
            tf:{doc_class} tf:nivelRiesgoBase ?riskLevel .
        }}
        """
        
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        
        if results["results"]["bindings"]:
            base_risk = results["results"]["bindings"][0]["riskLevel"]["value"]
            
            # Ajustar según metadata
            # Ejemplo: si préstamo > 30k → aumentar riesgo
            if "amount" in metadata:
                amount = float(metadata.get("amount", 0))
                if amount > 30000:
                    return "ALTO" if base_risk == "MEDIO" else base_risk
            
            return base_risk
        
        return "MEDIO"  # Default


# Singleton
ontology_service = OntologyService()
```

---

## 4. Servidor MCP

### 4.1 Estructura del Proyecto

```
mcp_server/
├── server.py              # Servidor principal MCP
├── tools/                 # Herramientas expuestas
│   ├── search_tool.py
│   ├── risk_tool.py
│   ├── compliance_tool.py
│   └── rag_tool.py
├── prompts/               # System prompts
│   └── system_prompts.py
└── config.py              # Configuración
```

### 4.2 Servidor MCP Básico

#### `mcp_server/server.py`

```python
"""
Servidor MCP para FinancIA 2030
Expone capacidades del sistema via Model Context Protocol
"""
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent
from typing import List

from mcp_server.tools.search_tool import SearchTool
from mcp_server.tools.risk_tool import RiskTool
from mcp_server.tools.compliance_tool import ComplianceTool
from mcp_server.tools.rag_tool import RAGTool

# Crear servidor MCP
app = Server("financia-2030-mcp")

# Inicializar tools
search_tool = SearchTool()
risk_tool = RiskTool()
compliance_tool = ComplianceTool()
rag_tool = RAGTool()


@app.list_tools()
async def list_tools() -> List[Tool]:
    """Lista todas las herramientas disponibles"""
    return [
        Tool(
            name="search_documents",
            description="Busca documentos en el sistema usando búsqueda híbrida BM25+semántica",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query de búsqueda"},
                    "filters": {"type": "object", "description": "Filtros opcionales"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="assess_risk",
            description="Evalúa riesgo de documento en 6 dimensiones",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "ID del documento"},
                    "weights": {"type": "object", "description": "Pesos personalizados"}
                },
                "required": ["document_id"]
            }
        ),
        Tool(
            name="check_compliance",
            description="Verifica cumplimiento GDPR/LOPDGDD",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string"},
                    "regulations": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["document_id"]
            }
        ),
        Tool(
            name="ask_question",
            description="Pregunta sobre documentos con RAG (respuestas fundamentadas)",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "document_ids": {"type": "array", "items": {"type": "string"}},
                    "require_citations": {"type": "boolean", "default": True}
                },
                "required": ["question"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Ejecuta una herramienta"""
    
    if name == "search_documents":
        result = await search_tool.execute(**arguments)
        return [TextContent(type="text", text=str(result))]
    
    elif name == "assess_risk":
        result = await risk_tool.execute(**arguments)
        return [TextContent(type="text", text=str(result))]
    
    elif name == "check_compliance":
        result = await compliance_tool.execute(**arguments)
        return [TextContent(type="text", text=str(result))]
    
    elif name == "ask_question":
        result = await rag_tool.execute(**arguments)
        return [TextContent(type="text", text=str(result))]
    
    else:
        raise ValueError(f"Tool {name} not found")


if __name__ == "__main__":
    # Ejecutar servidor
    asyncio.run(app.run())
```

---

## 5. Validación Terceros

### 5.1 Integración OFAC

#### `backend/services/third_party_validation_service.py`

```python
"""
Servicio de Validación de Terceros
Verifica contra listas de sanciones y registros oficiales
"""
import aiohttp
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ThirdPartyValidationService:
    """Validación contra bases de datos externas"""
    
    def __init__(self):
        self.ofac_api = "https://api.ofac.gov/v1"  # Ejemplo
        self.eu_sanctions_api = "https://webgate.ec.europa.eu/fsd/fsf"
        
    async def validate_entity(self, entity_name: str, 
                             entity_type: str = "PERSON") -> Dict:
        """
        Valida entidad contra listas de sanciones
        
        Args:
            entity_name: Nombre a validar
            entity_type: PERSON | ORGANIZATION | COUNTRY
            
        Returns:
            Dict con resultado de validación
        """
        results = {
            "entity": entity_name,
            "type": entity_type,
            "is_sanctioned": False,
            "checks": []
        }
        
        # Check OFAC
        ofac_result = await self._check_ofac(entity_name, entity_type)
        results["checks"].append(ofac_result)
        
        # Check EU Sanctions
        eu_result = await self._check_eu_sanctions(entity_name)
        results["checks"].append(eu_result)
        
        # Determinar si está sancionado
        results["is_sanctioned"] = any(
            check["found"] for check in results["checks"]
        )
        
        if results["is_sanctioned"]:
            logger.warning(f"⚠️ Entity {entity_name} found in sanction lists!")
        
        return results
    
    async def _check_ofac(self, name: str, entity_type: str) -> Dict:
        """Verifica contra lista OFAC"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ofac_api}/search",
                    params={"name": name, "type": entity_type}
                ) as resp:
                    data = await resp.json()
                    
                    return {
                        "source": "OFAC",
                        "found": len(data.get("results", [])) > 0,
                        "matches": data.get("results", []),
                        "confidence": data.get("confidence", 0.0)
                    }
        except Exception as e:
            logger.error(f"OFAC check failed: {e}")
            return {
                "source": "OFAC",
                "found": False,
                "error": str(e)
            }
    
    async def _check_eu_sanctions(self, name: str) -> Dict:
        """Verifica contra lista sanciones UE"""
        # Similar a OFAC
        try:
            # Implementación real aquí
            return {
                "source": "EU_SANCTIONS",
                "found": False,
                "matches": []
            }
        except Exception as e:
            logger.error(f"EU sanctions check failed: {e}")
            return {
                "source": "EU_SANCTIONS",
                "found": False,
                "error": str(e)
            }


# Singleton
third_party_validation_service = ThirdPartyValidationService()
```

---

## 6. Plan de Acción Técnico

### Sprint 1-2: Quick Wins (2 semanas)
- [ ] Implementar jerarquía de conceptos en `classification_service.py`
- [ ] Crear API `/ontology` endpoints
- [ ] Desarrollar widget `OntologyExplorer.tsx`
- [ ] Testing e integración

### Sprint 3-4: Ontología (4 semanas)
- [ ] Diseñar ontología OWL con Protégé
- [ ] Desplegar Apache Jena Fuseki
- [ ] Implementar `ontology_service.py`
- [ ] Integrar con pipelines existentes

### Sprint 5-6: MCP Server (3 semanas)
- [ ] Estructura servidor MCP
- [ ] Implementar 6 tools principales
- [ ] Cliente TypeScript frontend
- [ ] Documentación y ejemplos

### Sprint 7-8: Validación Terceros (3 semanas)
- [ ] Integración APIs OFAC, EU, BOE
- [ ] Servicio de validación
- [ ] UI alertas y bloqueos
- [ ] Auditoría de validaciones

---

## 📊 Métricas de Éxito

| Métrica | Baseline | Target | Medición |
|---------|----------|--------|----------|
| Precisión clasificación | 85% | 92% | F1-score |
| Cobertura RFP | 92% | 100% | Checklist |
| API response time | 250ms | <200ms | p95 |
| Validaciones/día | 0 | 500+ | Contador |

---

**Última actualización**: 9 de Octubre 2025  
**Próxima revisión**: Sprint Planning 14 Octubre
