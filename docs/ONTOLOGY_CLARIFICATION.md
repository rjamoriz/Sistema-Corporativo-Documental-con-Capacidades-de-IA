# 🌐 Ontología Corporativa - Plan de Desarrollo

**Fecha**: 9 de Octubre 2025  
**Proyecto**: FinancIA 2030  
**Estado**: 🔶 Gap Identificado - Desarrollo Requerido

---

## 📋 Resumen Ejecutivo

### ¿Qué Tenemos Ahora?
✅ **Taxonomía simple** con 9 categorías planas de documentos

### ¿Qué Necesitamos Desarrollar?
🔶 **Ontología formal** con jerarquías, relaciones y capacidad de inferencia (OWL/SKOS)

### ¿Es Obligatorio Desarrollarlo?
**Depende del alcance del proyecto:**
- ✅ **SI el cliente requiere ontología formal** (mencionado en RFP) → **SÍ, es necesario**
- ⚠️ **SI el cliente acepta taxonomía simple** → NO es necesario (funciona con lo actual)

---

## 1. Situación Actual: Lo Que YA Tenemos ✅

### 1.1 Taxonomía Simple Implementada

```python
# backend/models/document.py (ACTUAL)
class DocumentClassification(str, Enum):
    """Categorías planas de documentos"""
    LEGAL = "LEGAL"                    # Contratos, pólizas, escrituras
    FINANCIAL = "FINANCIAL"            # Estados financieros, balances
    COMMERCIAL = "COMMERCIAL"          # Propuestas comerciales
    TECHNICAL = "TECHNICAL"            # Especificaciones técnicas
    PERSONAL = "PERSONAL"              # DNI, nóminas, certificados
    ADMINISTRATIVE = "ADMINISTRATIVE"  # Facturas, recibos
    CORRESPONDENCE = "CORRESPONDENCE"  # Emails, cartas
    COMPLIANCE = "COMPLIANCE"          # GDPR, ISO, auditorías
    SENSITIVE = "SENSITIVE"            # Datos personales sensibles
```

### 1.2 Clasificación Automática

```python
# backend/services/classification_service.py (ACTUAL)
class ClassificationService:
    """Clasifica documentos usando ML + reglas"""
    
    async def classify_document(self, content: str, filename: str):
        # 1. Clasificador ML (spaCy + custom model)
        ml_prediction = self.ml_classifier.predict(content)
        
        # 2. Reglas basadas en palabras clave
        keywords = {
            "LEGAL": ["contrato", "cláusula", "escritura", "poder"],
            "FINANCIAL": ["balance", "cuenta", "estado financiero"],
            "PERSONAL": ["dni", "nif", "nómina", "certificado"],
            # ...
        }
        
        rule_scores = self._apply_rules(content, keywords)
        
        # 3. Combinar predicciones
        final_class = self._merge_predictions(ml_prediction, rule_scores)
        
        return {
            "category": final_class,
            "confidence": 0.85,
            "method": "ml+rules"
        }
```

### 1.3 Limitaciones del Sistema Actual

| Característica | Sistema Actual | Ontología Requerida |
|---------------|----------------|---------------------|
| **Jerarquía** | ❌ No | ✅ Sí (4-5 niveles) |
| **Relaciones entre conceptos** | ❌ No | ✅ Sí (20+ propiedades) |
| **Inferencia automática** | ❌ No | ✅ Sí (razonadores OWL) |
| **Validación de metadata** | ⚠️ Básica | ✅ Completa según clase |
| **Vocabulario compartido** | ⚠️ Informal | ✅ Formal (OWL/SKOS) |
| **Extensibilidad** | ⚠️ Limitada | ✅ Alta (ontología modular) |

**Ejemplo de lo que NO podemos hacer ahora:**

```python
# ❌ NO POSIBLE CON TAXONOMÍA ACTUAL

# 1. No podemos expresar jerarquías:
#    "Préstamo Hipotecario" ES UN "Contrato de Financiación"
#    que ES UN "Documento Contractual"
#    que ES UN "Documento"

# 2. No podemos definir relaciones:
#    Préstamo --tieneCliente--> Cliente
#    Préstamo --requiereDocumento--> Valoración
#    Préstamo --derivaEn--> Póliza de Seguro

# 3. No podemos inferir automáticamente:
#    SI documento es "Préstamo Hipotecario"
#    ENTONCES requiere "Valoración Inmobiliaria"
#    Y requiere "Garantía Hipotecaria"
#    Y nivel de riesgo base es "BAJO"
```

---

## 2. Ontología Formal: Lo Que NECESITAMOS Desarrollar 🔶

### 2.1 Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────┐
│                CAPA DE APLICACIÓN                    │
│  ┌───────────────────────────────────────────────┐  │
│  │  Backend FastAPI (actual)                     │  │
│  │  - Clasificación de documentos                │  │
│  │  - Validación de metadata                     │  │
│  │  - Búsqueda semántica                         │  │
│  └─────────────┬─────────────────────────────────┘  │
└────────────────┼───────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│            CAPA DE ONTOLOGÍA (NUEVA)                 │
│  ┌───────────────────────────────────────────────┐  │
│  │  OntologyService                              │  │
│  │  - classify_by_ontology()                     │  │
│  │  - get_required_fields()                      │  │
│  │  - infer_risk_level()                         │  │
│  │  - get_related_concepts()                     │  │
│  └─────────────┬─────────────────────────────────┘  │
│                │                                      │
│  ┌─────────────▼─────────────────────────────────┐  │
│  │  RDFLib + SPARQLWrapper                       │  │
│  │  - Consultas SPARQL                           │  │
│  │  - Razonamiento OWL                           │  │
│  └─────────────┬─────────────────────────────────┘  │
└────────────────┼───────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         ONTOLOGÍA OWL/SKOS (NUEVA)                   │
│  ┌───────────────────────────────────────────────┐  │
│  │  tefinancia_ontology.owl                      │  │
│  │  - 30-40 clases (Documento, Contrato, etc.)  │  │
│  │  - 20-25 propiedades (relaciones)            │  │
│  │  - 100+ individuos (instancias específicas)  │  │
│  │  - Reglas de inferencia                      │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 2.2 Componentes a Desarrollar

#### **A. Ontología OWL (Diseño)**

**Herramienta**: Protégé (editor OWL)  
**Formato**: OWL 2 (Web Ontology Language)  
**Tamaño estimado**: 30-40 clases, 20-25 propiedades

**Ejemplo de jerarquía:**

```
Documento (raíz)
├── DocumentoAdministrativo
│   ├── Factura
│   ├── Recibo
│   └── NotaDebito
├── DocumentoContractual
│   ├── Contrato
│   │   ├── ContratoFinanciacion
│   │   │   ├── PrestamoPersonal
│   │   │   ├── PrestamoHipotecario
│   │   │   ├── PrestamoAutomovil
│   │   │   └── LineaCredito
│   │   ├── ContratoArrendamiento
│   │   └── ContratoServicio
│   └── PolizaSeguro
├── DocumentoIdentificacion
│   ├── DNI
│   ├── Pasaporte
│   └── NIE
└── DocumentoFinanciero
    ├── EstadoFinanciero
    ├── Balance
    └── CuentaResultados
```

**Archivo generado**: `ontology/tefinancia_ontology.owl` (nuevo)

---

#### **B. Servicio de Ontología (Backend)**

**Archivo nuevo**: `backend/services/ontology_service.py`

```python
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from SPARQLWrapper import SPARQLWrapper, JSON
from typing import List, Dict, Optional

class OntologyService:
    """Servicio para trabajar con la ontología OWL"""
    
    def __init__(self):
        # Cargar ontología
        self.graph = Graph()
        self.graph.parse("ontology/tefinancia_ontology.owl")
        
        # Namespace de TeFinancia
        self.TF = Namespace("http://tefinancia.es/onto#")
        
        # SPARQL endpoint (opcional, para inferencia)
        self.sparql = SPARQLWrapper("http://localhost:3030/tefinancia")
    
    async def classify_by_ontology(
        self, 
        content: str, 
        metadata: Dict
    ) -> Dict[str, any]:
        """Clasifica documento usando ontología + razonador"""
        
        # 1. Extraer entidades del contenido
        entities = await self._extract_entities(content)
        
        # 2. Consulta SPARQL para encontrar clase más específica
        query = f"""
        PREFIX tf: <http://tefinancia.es/onto#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?class ?label ?riskLevel WHERE {{
            ?class rdfs:subClassOf* tf:Documento .
            ?class rdfs:label ?label .
            OPTIONAL {{ ?class tf:nivelRiesgoBase ?riskLevel }}
            
            # Filtrar por patrones de contenido
            FILTER (
                # Si contiene términos clave de la clase
                ?class = tf:PrestamoHipotecario && 
                CONTAINS(LCASE("{content}"), "hipoteca")
            )
        }}
        ORDER BY DESC(?class)
        LIMIT 1
        """
        
        results = self._execute_sparql(query)
        
        if results:
            return {
                "class": results[0]["class"],
                "label": results[0]["label"],
                "risk_level": results[0].get("riskLevel", "MEDIO"),
                "confidence": 0.90,
                "method": "ontology_reasoning"
            }
        
        return self._fallback_classification(content)
    
    async def get_required_fields(self, doc_class: str) -> List[Dict]:
        """Obtiene campos obligatorios según la ontología"""
        
        query = f"""
        PREFIX tf: <http://tefinancia.es/onto#>
        
        SELECT ?field ?label ?type ?mandatory WHERE {{
            tf:{doc_class} tf:requiereCampo ?field .
            ?field rdfs:label ?label .
            ?field tf:tipoDato ?type .
            ?field tf:esObligatorio ?mandatory .
        }}
        """
        
        results = self._execute_sparql(query)
        
        return [
            {
                "name": r["field"],
                "label": r["label"],
                "type": r["type"],
                "required": r["mandatory"] == "true"
            }
            for r in results
        ]
    
    async def infer_relationships(
        self, 
        doc_class: str
    ) -> List[Dict]:
        """Infiere documentos relacionados según ontología"""
        
        query = f"""
        PREFIX tf: <http://tefinancia.es/onto#>
        
        SELECT ?relatedClass ?relation WHERE {{
            tf:{doc_class} ?relation ?relatedClass .
            FILTER(?relation IN (tf:requiereDocumento, tf:derivaEn))
        }}
        """
        
        results = self._execute_sparql(query)
        
        return [
            {
                "related_class": r["relatedClass"],
                "relationship": r["relation"],
                "description": f"{doc_class} {r['relation']} {r['relatedClass']}"
            }
            for r in results
        ]
    
    async def validate_metadata(
        self, 
        doc_class: str, 
        metadata: Dict
    ) -> Dict[str, List[str]]:
        """Valida metadata según restricciones de la ontología"""
        
        errors = []
        warnings = []
        
        # Obtener campos requeridos
        required_fields = await self.get_required_fields(doc_class)
        
        for field in required_fields:
            if field["required"] and field["name"] not in metadata:
                errors.append(f"Campo obligatorio faltante: {field['label']}")
            
            if field["name"] in metadata:
                # Validar tipo de dato
                value = metadata[field["name"]]
                expected_type = field["type"]
                
                if not self._validate_type(value, expected_type):
                    errors.append(
                        f"Tipo incorrecto para {field['label']}: "
                        f"esperado {expected_type}, recibido {type(value)}"
                    )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _execute_sparql(self, query: str) -> List[Dict]:
        """Ejecuta consulta SPARQL"""
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]
    
    async def _extract_entities(self, content: str) -> List[str]:
        """Extrae entidades del texto (usando spaCy actual)"""
        # Reutilizar servicio NER existente
        from backend.services.ner_service import ner_service
        return await ner_service.extract_entities(content)
    
    def _validate_type(self, value: any, expected_type: str) -> bool:
        """Valida tipo de dato"""
        type_mapping = {
            "string": str,
            "integer": int,
            "decimal": (int, float),
            "date": str,  # Validar formato ISO después
            "boolean": bool
        }
        expected = type_mapping.get(expected_type, str)
        return isinstance(value, expected)


# Singleton
ontology_service = OntologyService()
```

**Dependencias nuevas** (agregar a `requirements.txt`):
```
rdflib==7.0.0
SPARQLWrapper==2.0.0
owlready2==0.43  # Para razonamiento OWL
```

---

#### **C. API Endpoints (Extensión)**

**Archivo**: `backend/api/v1/ontology.py` (nuevo)

```python
from fastapi import APIRouter, Depends, HTTPException
from backend.services.ontology_service import ontology_service
from backend.models.schemas import OntologyClassification, MetadataValidation

router = APIRouter()

@router.post("/ontology/classify")
async def classify_document_ontology(
    content: str,
    metadata: dict,
    current_user = Depends(get_current_user)
):
    """Clasifica documento usando ontología"""
    
    result = await ontology_service.classify_by_ontology(content, metadata)
    
    return {
        "classification": result,
        "required_fields": await ontology_service.get_required_fields(
            result["class"]
        ),
        "related_documents": await ontology_service.infer_relationships(
            result["class"]
        )
    }

@router.post("/ontology/validate")
async def validate_document_metadata(
    doc_class: str,
    metadata: dict,
    current_user = Depends(get_current_user)
):
    """Valida metadata según ontología"""
    
    validation = await ontology_service.validate_metadata(doc_class, metadata)
    
    if not validation["valid"]:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Metadata inválida según ontología",
                "errors": validation["errors"]
            }
        )
    
    return {
        "valid": True,
        "warnings": validation.get("warnings", [])
    }

@router.get("/ontology/hierarchy")
async def get_ontology_hierarchy(
    current_user = Depends(get_current_user)
):
    """Obtiene jerarquía completa de la ontología"""
    
    # Query SPARQL para obtener árbol de clases
    query = """
    PREFIX tf: <http://tefinancia.es/onto#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?class ?label ?parent WHERE {
        ?class rdfs:subClassOf ?parent .
        ?class rdfs:label ?label .
        FILTER(?parent != owl:Thing)
    }
    """
    
    results = ontology_service._execute_sparql(query)
    
    # Construir árbol jerárquico
    hierarchy = _build_hierarchy_tree(results)
    
    return {
        "ontology": "TeFinancia Corporate Ontology",
        "version": "1.0",
        "classes_count": len(results),
        "hierarchy": hierarchy
    }
```

---

#### **D. Frontend UI (Opcional)**

**Archivo**: `frontend/src/components/OntologyBrowser.tsx` (nuevo)

```typescript
import React, { useState, useEffect } from 'react';

export const OntologyBrowser: React.FC = () => {
  const [hierarchy, setHierarchy] = useState<any>(null);
  
  useEffect(() => {
    fetchOntologyHierarchy();
  }, []);
  
  const fetchOntologyHierarchy = async () => {
    const response = await fetch('/api/v1/ontology/hierarchy');
    const data = await response.json();
    setHierarchy(data.hierarchy);
  };
  
  return (
    <div className="ontology-browser">
      <h2>🌐 Navegador de Ontología TeFinancia</h2>
      
      {hierarchy && (
        <TreeView
          data={hierarchy}
          onNodeClick={(node) => {
            console.log('Clase seleccionada:', node);
          }}
        />
      )}
    </div>
  );
};
```

---

## 3. Plan de Implementación

### 3.1 Fase 1: Diseño de Ontología (2 semanas)

**Semana 1: Workshops**
- [ ] Workshop 1: Identificar conceptos clave del dominio
- [ ] Workshop 2: Definir jerarquías de clases
- [ ] Workshop 3: Establecer propiedades y relaciones

**Semana 2: Modelado**
- [ ] Crear ontología en Protégé
- [ ] Validar con razonador HermiT
- [ ] Exportar a OWL 2

**Entregable**: `ontology/tefinancia_ontology.owl`

---

### 3.2 Fase 2: Integración Backend (1.5 semanas)

**Semana 3-4:**
- [ ] Implementar `OntologyService` (3 días)
- [ ] Crear endpoints API `/ontology/*` (2 días)
- [ ] Integrar con `IngestService` existente (2 días)
- [ ] Tests unitarios y de integración (1 día)

**Entregables**:
- `backend/services/ontology_service.py`
- `backend/api/v1/ontology.py`
- Tests: `tests/test_ontology_service.py`

---

### 3.3 Fase 3: Frontend y Documentación (1 semana)

**Semana 5:**
- [ ] Componente navegador de ontología (2 días)
- [ ] Actualizar wizard de clasificación (1 día)
- [ ] Documentación de uso (1 día)
- [ ] Guías de extensión de ontología (1 día)

**Entregables**:
- `frontend/src/components/OntologyBrowser.tsx`
- `docs/ONTOLOGY_USAGE.md`
- `docs/ONTOLOGY_EXTENSION_GUIDE.md`

---

### 3.4 Fase 4: Testing y Ajustes (0.5 semanas)

**Semana 6:**
- [ ] Testing end-to-end (1 día)
- [ ] Ajustes según feedback (1 día)
- [ ] Deploy a staging (0.5 días)

---

## 4. Esfuerzo Estimado

| Fase | Duración | Personas | Esfuerzo Total |
|------|----------|----------|----------------|
| **Fase 1: Diseño** | 2 semanas | 1 ontólogo + 1 BA | 40 horas |
| **Fase 2: Backend** | 1.5 semanas | 1 dev backend | 60 horas |
| **Fase 3: Frontend** | 1 semana | 1 dev frontend | 40 horas |
| **Fase 4: Testing** | 0.5 semanas | 1 QA + 1 dev | 20 horas |
| **TOTAL** | **5 semanas** | | **160 horas** |

**Coste estimado** (si se contrata externamente):
- Ontólogo: 40h × 80€/h = €3,200
- Backend Dev: 60h × 70€/h = €4,200
- Frontend Dev: 40h × 70€/h = €2,800
- QA: 20h × 50€/h = €1,000
- **TOTAL: €11,200**

---

## 5. ¿Es Necesario Desarrollar Esto?

### 5.1 Escenarios

#### **Escenario A: Cliente Requiere Ontología Formal** ✅

**SI el RFP explícitamente menciona:**
- "Ontología corporativa"
- "OWL/SKOS"
- "Razonamiento semántico"
- "Inferencia de conocimiento"

**ENTONCES**:
- ✅ **SÍ es necesario desarrollar**
- Prioridad: **ALTA**
- Tiempo: 5 semanas
- Coste: €11,200

---

#### **Escenario B: Cliente Acepta Taxonomía Simple** ⚠️

**SI el cliente está satisfecho con:**
- Clasificación básica (9 categorías)
- Sin jerarquías complejas
- Sin inferencia automática

**ENTONCES**:
- ❌ **NO es necesario desarrollar**
- Sistema actual es suficiente
- Ahorras 5 semanas y €11,200
- **RECOMENDACIÓN**: Clarificar con cliente en kickoff meeting

---

#### **Escenario C: Desarrollo Incremental** 🔶

**Opción híbrida:**
1. **Fase 1 (ahora)**: Usar taxonomía actual
2. **Fase 2 (3-6 meses)**: Añadir ontología light (solo jerarquías)
3. **Fase 3 (6-12 meses)**: Ontología completa con inferencia

**Ventajas**:
- Time-to-market rápido
- Validación con usuarios reales
- Desarrollo iterativo

---

## 6. Recomendación Final

### 📊 **Mi Recomendación Profesional**

```
┌─────────────────────────────────────────────────────┐
│  OPCIÓN RECOMENDADA: Desarrollo Incremental 🔶      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  SPRINT 1 (ACTUAL): Taxonomía Simple ✅              │
│  - Ya implementado                                   │
│  - Funcional al 95%                                  │
│  - Deploy inmediato                                  │
│                                                      │
│  SPRINT 2 (3 meses): Ontología Light 🔶             │
│  - Solo jerarquías (sin inferencia)                 │
│  - 2 semanas desarrollo                              │
│  - Validar con usuarios                              │
│                                                      │
│  SPRINT 3 (6 meses): Ontología Completa ✅          │
│  - Inferencia + razonamiento                         │
│  - 3 semanas desarrollo                              │
│  - Full compliance RFP                               │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 🎯 **Acción Inmediata**

**ANTES DE DESARROLLAR:**
1. ✅ Clarificar con cliente en kickoff:
   - "¿Requieren ontología formal OWL/SKOS?"
   - "¿Es suficiente una taxonomía jerárquica simple?"
   - "¿Necesitan capacidad de inferencia?"

2. ✅ Si respuesta es "Sí a todo" → Desarrollar ontología completa

3. ✅ Si respuesta es "Taxonomía simple OK" → NO desarrollar (usar actual)

4. ✅ Si respuesta es "No estamos seguros" → Desarrollo incremental

---

## 7. Entregables de Documentación

Si decides desarrollar la ontología, estos son los documentos que deberás crear:

- [ ] `docs/ONTOLOGY_DESIGN.md` - Diseño conceptual
- [ ] `docs/ONTOLOGY_USAGE.md` - Guía de uso
- [ ] `docs/ONTOLOGY_API.md` - Documentación API
- [ ] `docs/ONTOLOGY_EXTENSION.md` - Cómo extender la ontología
- [ ] `ontology/tefinancia_ontology.owl` - Archivo OWL
- [ ] `ontology/README.md` - Descripción de la ontología

---

## 8. Resumen para Stakeholders

### Para el Cliente:

> "Actualmente tenemos un **sistema de clasificación funcional con 9 categorías**. 
> 
> Si necesitan una **ontología formal con jerarquías e inferencia** (como menciona la RFP), 
> requerirá **5 semanas adicionales de desarrollo** con un coste de **€11,200**.
> 
> Recomendamos **clarificar en el kickoff** si esto es un requisito hard o si la taxonomía 
> actual es suficiente para sus necesidades."

### Para el Equipo:

> "**GAP IDENTIFICADO**: Ontología formal OWL/SKOS
> 
> **Estado actual**: Taxonomía simple funcional ✅
> 
> **Desarrollo necesario**: 
> - Ontología OWL (2 semanas)
> - Backend integration (1.5 semanas)
> - Frontend UI (1 semana)
> - Testing (0.5 semanas)
> 
> **Decisión**: Pendiente de kickoff con cliente"

---

**Última actualización**: 9 de Octubre 2025  
**Autor**: Equipo FinancIA 2030  
**Estado**: Análisis Completo - Esperando decisión de cliente
