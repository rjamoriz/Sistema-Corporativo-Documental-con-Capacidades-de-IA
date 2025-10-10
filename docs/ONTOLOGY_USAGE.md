# Guía de Uso: Ontología OWL TeFinancia

## 📋 Índice

- [Introducción](#introducción)
- [Arquitectura de la Ontología](#arquitectura-de-la-ontología)
- [Casos de Uso](#casos-de-uso)
- [Uso del OntologyService](#uso-del-ontologyservice)
- [Endpoints de API REST](#endpoints-de-api-rest)
- [Ejemplos Prácticos](#ejemplos-prácticos)
- [Comparación con Taxonomía JSON](#comparación-con-taxonomía-json)

---

## Introducción

La **ontología OWL TeFinancia** es una representación formal del conocimiento del dominio financiero y documental de la organización. A diferencia de la taxonomía JSON (Sprint 1), la ontología utiliza estándares de la Web Semántica (OWL, RDF, SPARQL) para proporcionar:

✅ **Semántica formal**: Significado preciso de conceptos y relaciones  
✅ **Inferencia automática**: Deducción de información implícita  
✅ **Validación robusta**: Verificación contra restricciones formales  
✅ **Consultas avanzadas**: SPARQL para análisis complejos  
✅ **Interoperabilidad**: Estándares W3C ampliamente adoptados  

### Tecnologías Utilizadas

- **OWL 2** (Web Ontology Language): Lenguaje para definir ontologías
- **RDF/Turtle**: Formato de serialización legible para humanos
- **RDFLib 7.1.1**: Biblioteca Python para manipulación de grafos RDF
- **SPARQL**: Lenguaje de consulta para datos semánticos
- **OWLReady2**: Razonamiento y carga de ontologías OWL
- **SPARQLWrapper**: Consultas a endpoints SPARQL

---

## Arquitectura de la Ontología

### Estructura del Grafo RDF

La ontología está organizada como un **grafo RDF** donde:

- **Nodos**: Representan clases, individuos y valores literales
- **Aristas**: Representan propiedades (relaciones y atributos)
- **Triples**: Unidad básica `(sujeto, predicado, objeto)`

### Jerarquía de Clases

```
tf:Documento (Raíz)
├── tf:DocumentoContractual
│   ├── tf:ContratoFinanciacion
│   │   ├── tf:PrestamoHipotecario
│   │   ├── tf:PrestamoPersonal
│   │   ├── tf:LineaCredito
│   │   └── tf:Arrendamiento
│   ├── tf:ContratoTrabajo
│   └── tf:ContratoServicio
├── tf:DocumentoIdentidad
│   ├── tf:DNI
│   ├── tf:Pasaporte
│   └── tf:NIE
├── tf:DocumentoFinanciero
│   ├── tf:Factura
│   ├── tf:Nomina
│   ├── tf:EstadoCuenta
│   └── tf:Recibo
└── tf:DocumentoLegal
    ├── tf:Escritura
    ├── tf:Sentencia
    └── tf:ActaNotarial
```

### Object Properties (Relaciones)

Las **ObjectProperties** conectan instancias de clases entre sí:

| Propiedad | Dominio | Rango | Descripción |
|-----------|---------|-------|-------------|
| `tf:tieneCliente` | ContratoFinanciacion | Cliente | Relaciona contrato con cliente |
| `tf:requiereDocumento` | Documento | Documento | Documento requiere otro documento |
| `tf:derivaEn` | Documento | Documento | Documento genera otro documento |
| `tf:tieneGarantia` | ContratoFinanciacion | Garantia | Contrato tiene garantía asociada |
| `tf:requiereValoracion` | PrestamoHipotecario | Valoracion | Préstamo requiere valoración |
| `tf:firmadoPor` | DocumentoContractual | Persona | Contrato firmado por persona |
| `tf:emitidoPor` | DocumentoFinanciero | Entidad | Documento emitido por entidad |
| `tf:destinatario` | Documento | Persona | Documento dirigido a persona |

### Datatype Properties (Atributos)

Las **DatatypeProperties** asignan valores literales a instancias:

| Propiedad | Dominio | Rango | Descripción |
|-----------|---------|--------|-------------|
| `tf:titulo` | Documento | xsd:string | Título del documento |
| `tf:fechaCreacion` | Documento | xsd:date | Fecha de creación |
| `tf:importeFinanciado` | ContratoFinanciacion | xsd:decimal | Importe del financiamiento |
| `tf:tae` | ContratoFinanciacion | xsd:decimal | Tasa Anual Equivalente |
| `tf:tin` | ContratoFinanciacion | xsd:decimal | Tasa de Interés Nominal |
| `tf:plazoMeses` | ContratoFinanciacion | xsd:integer | Plazo en meses |
| `tf:cuotaMensual` | ContratoFinanciacion | xsd:decimal | Cuota mensual |
| `tf:ltv` | PrestamoHipotecario | xsd:decimal | Loan-to-Value ratio |
| `tf:valorTasacion` | PrestamoHipotecario | xsd:decimal | Valor de tasación |
| `tf:nif` | DocumentoIdentidad | xsd:string | NIF/NIE |
| `tf:nombreCompleto` | Persona | xsd:string | Nombre completo |
| `tf:scoringCrediticio` | Cliente | xsd:integer | Scoring crediticio |

### Restricciones OWL

La ontología define restricciones formales para validación:

#### Cardinalidad Exacta
```turtle
tf:PrestamoHipotecario rdfs:subClassOf [
    rdf:type owl:Restriction ;
    owl:onProperty tf:tieneCliente ;
    owl:cardinality 1
] .
```
➡️ **Cada préstamo hipotecario debe tener exactamente 1 cliente**

#### Cardinalidad Mínima
```turtle
tf:PrestamoHipotecario rdfs:subClassOf [
    rdf:type owl:Restriction ;
    owl:onProperty tf:requiereValoracion ;
    owl:minCardinality 1
] .
```
➡️ **Cada préstamo hipotecario requiere al menos 1 valoración**

#### Rangos Numéricos
```turtle
tf:PrestamoHipotecario
    tf:importeMinimo 30000 ;
    tf:importeMaximo 1000000 ;
    tf:plazoMinimo 60 ;
    tf:plazoMaximo 480 .
```
➡️ **Validación de rangos de valores**

### Anotaciones Semánticas

#### SKOS (Simple Knowledge Organization System)
```turtle
tf:PrestamoHipotecario
    rdfs:label "Préstamo Hipotecario"@es ;
    rdfs:comment "Contrato de financiación con garantía inmobiliaria"@es ;
    skos:definition "Préstamo a largo plazo garantizado con hipoteca sobre un inmueble" ;
    skos:altLabel "Hipoteca"@es .
```

#### Keywords para Clasificación
```turtle
tf:PrestamoHipotecario
    tf:keyword "préstamo hipotecario" ;
    tf:keyword "hipoteca" ;
    tf:keyword "garantía inmobiliaria" ;
    tf:keyword "vivienda" .
```

#### Regulaciones Aplicables
```turtle
tf:PrestamoHipotecario
    tf:regulacionAplicable "Ley Hipotecaria 5/2019" ;
    tf:regulacionAplicable "MiFID II" ;
    tf:regulacionAplicable "Ley de Crédito Inmobiliario" .
```

---

## Casos de Uso

### 1. Clasificación Automática de Documentos

**Escenario**: Un documento PDF llega al sistema sin metadata de clasificación.

**Proceso**:
1. Extracción de texto del PDF
2. Búsqueda de keywords en la ontología
3. Matching con clases OWL
4. Asignación de clase con confianza

**Ventajas vs Taxonomía**:
- Keywords semánticos (no solo nombres de clase)
- Sinónimos y variaciones (skos:altLabel)
- Confianza cuantificada (0-1)

### 2. Validación de Metadatos

**Escenario**: Validar que un préstamo hipotecario cumple requisitos formales.

**Proceso**:
1. Verificar campos requeridos (owl:minCardinality)
2. Validar rangos numéricos (importeMinimo/Maximo)
3. Comprobar tipos de datos
4. Retornar errores específicos

**Ventajas vs Taxonomía**:
- Restricciones formales en OWL
- Validación declarativa (no código imperativo)
- Mensajes de error estructurados

### 3. Inferencia de Riesgo

**Escenario**: Calcular automáticamente el nivel de riesgo de un contrato.

**Reglas implementadas**:
```python
# Regla 1: LTV alto
if metadata.get("ltv", 0) > 80:
    risk_level = "ALTO"

# Regla 2: TAE elevada
if metadata.get("tae", 0) > 10:
    risk_level = "ALTO"

# Regla 3: Datos sensibles
if metadata.get("esSensible"):
    risk_level = "ALTO"

# Regla 4: Tipo de contrato
if class_name == "LineaCredito":
    risk_level = "ALTO"

# Regla 5: Plazo muy largo
if metadata.get("plazoMeses", 0) > 240:
    if risk_level == "BAJO":
        risk_level = "MEDIO"
```

**Ventajas vs Taxonomía**:
- Reglas expresadas como axiomas OWL
- Razonamiento automático
- Trazabilidad de reglas aplicadas

### 4. Consultas SPARQL Complejas

**Escenario**: Análisis de contratos de alto riesgo con importe > 100.000€.

**Consulta**:
```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?contrato ?label ?riesgo ?importe WHERE {
    ?contrato rdfs:subClassOf* tf:ContratoFinanciacion .
    ?contrato rdfs:label ?label .
    ?contrato tf:nivelRiesgoBase ?riesgo .
    ?contrato tf:importeMinimo ?importe .
    
    FILTER(?riesgo = "ALTO" && ?importe > 100000)
}
ORDER BY DESC(?importe)
```

**Ventajas vs Taxonomía**:
- Consultas declarativas SQL-like
- Navegación transitiva (rdfs:subClassOf*)
- Filtros complejos y agregaciones

### 5. Extracción de Documentos Relacionados

**Escenario**: Encontrar todos los documentos requeridos para un préstamo hipotecario.

**Proceso**:
1. Query OWL para ObjectProperties con someValuesFrom
2. Extraer documentos relacionados via tf:requiereDocumento
3. Construir lista de dependencias

**Resultado esperado**:
- DNI del cliente
- Valoración del inmueble
- Certificado de ingresos
- Escritura de propiedad

**Ventajas vs Taxonomía**:
- Relaciones semánticas explícitas
- Navegación de grafo RDF
- Inferencia de dependencias

---

## Uso del OntologyService

### Inicialización

```python
from backend.services.ontology_service import ontology_service

# El servicio es un singleton, se inicializa automáticamente
# al importar el módulo
```

### Métodos Principales

#### 1. `get_class_info(class_uri)`

Extrae toda la información de una clase OWL.

```python
from rdflib import URIRef

# Obtener información de PrestamoHipotecario
class_uri = ontology_service.TF.PrestamoHipotecario
info = ontology_service.get_class_info(class_uri)

print(f"Etiqueta: {info['label']}")
print(f"Descripción: {info['comment']}")
print(f"Clases padre: {info['parent_classes']}")
print(f"Propiedades: {info['properties']}")
```

**Output esperado**:
```python
{
    "label": "Préstamo Hipotecario",
    "comment": "Contrato de financiación con garantía inmobiliaria",
    "parent_classes": ["ContratoFinanciacion", "DocumentoContractual"],
    "properties": {
        "nivelRiesgoBase": ["BAJO"],
        "importeMinimo": [30000],
        "plazoMinimo": [60],
        "taeMaximo": [15.0],
        "requiereGarantiaInmobiliaria": [True]
    }
}
```

#### 2. `get_subclasses(class_uri, direct_only=True)`

Navega la jerarquía de clases.

```python
# Subclases directas de Documento
class_uri = ontology_service.TF.Documento
direct_subclasses = ontology_service.get_subclasses(class_uri, direct_only=True)

print("Subclases directas:")
for sc in direct_subclasses:
    print(f"  - {sc.split('#')[-1]}")

# Todas las subclases (transitivas)
all_subclasses = ontology_service.get_subclasses(class_uri, direct_only=False)
print(f"\nTotal subclases (incluyendo transitivas): {len(all_subclasses)}")
```

**Output esperado**:
```
Subclases directas:
  - DocumentoContractual
  - DocumentoIdentidad
  - DocumentoFinanciero
  - DocumentoLegal

Total subclases (incluyendo transitivas): 35
```

#### 3. `classify_document(content, metadata={})`

Clasifica un documento basándose en keywords.

```python
content = """
Contrato de préstamo hipotecario
Importe: 200.000 €
Plazo: 25 años
Garantía: Vivienda habitual
TAE: 3.5%
"""

result = ontology_service.classify_document(content, {})

print(f"Clase: {result['class_name']}")
print(f"Etiqueta: {result['class_label']}")
print(f"Confianza: {result['confidence']:.2%}")
print(f"Keywords encontradas: {result['matched_keywords']}")
```

**Output esperado**:
```
Clase: PrestamoHipotecario
Etiqueta: Préstamo Hipotecario
Confianza: 85.00%
Keywords encontradas: ['préstamo hipotecario', 'hipoteca', 'garantía inmobiliaria', 'vivienda']
```

#### 4. `get_required_fields(class_uri)`

Extrae campos requeridos de una clase.

```python
class_uri = ontology_service.TF.PrestamoHipotecario
required_fields = ontology_service.get_required_fields(class_uri)

print("Campos requeridos:")
for field in required_fields:
    print(f"  - {field}")
```

**Output esperado**:
```
Campos requeridos:
  - tieneCliente
  - requiereValoracion
```

#### 5. `validate_metadata(class_uri, metadata)`

Valida metadatos contra restricciones OWL.

```python
class_uri = ontology_service.TF.PrestamoHipotecario
metadata = {
    "importeFinanciado": 200000,
    "tae": 3.5,
    "plazoMeses": 240,
    "ltv": 80.0
}

is_valid, errors = ontology_service.validate_metadata(class_uri, metadata)

if is_valid:
    print("✅ Metadatos válidos")
else:
    print("❌ Errores de validación:")
    for error in errors:
        print(f"  - {error}")
```

**Output esperado** (con error):
```
❌ Errores de validación:
  - importeFinanciado debe ser >= 30000 (importeMinimo)
  - plazoMeses debe ser >= 60 (plazoMinimo)
```

#### 6. `infer_risk_level(class_uri, metadata)`

Infiere nivel de riesgo aplicando reglas.

```python
class_uri = ontology_service.TF.PrestamoHipotecario
metadata = {
    "importeFinanciado": 250000,
    "ltv": 85.0,  # > 80% → ALTO
    "tae": 4.2,
    "plazoMeses": 300
}

risk_level = ontology_service.infer_risk_level(class_uri, metadata)
print(f"Nivel de riesgo: {risk_level}")
```

**Output esperado**:
```
Nivel de riesgo: ALTO
```

#### 7. `query_sparql(sparql_query)`

Ejecuta consultas SPARQL personalizadas.

```python
query = """
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?riesgo WHERE {
    ?class rdfs:subClassOf tf:ContratoFinanciacion .
    ?class rdfs:label ?label .
    ?class tf:nivelRiesgoBase ?riesgo .
}
ORDER BY ?riesgo
"""

results = ontology_service.query_sparql(query)

for result in results:
    print(f"{result['label']} - Riesgo: {result['riesgo']}")
```

**Output esperado**:
```
Préstamo Hipotecario - Riesgo: BAJO
Préstamo Personal - Riesgo: MEDIO
Línea de Crédito - Riesgo: ALTO
```

#### 8. `get_hierarchy(root_uri)`

Construye árbol de jerarquía completo.

```python
class_uri = ontology_service.TF.Documento
hierarchy = ontology_service.get_hierarchy(class_uri)

def print_tree(node, indent=0):
    print("  " * indent + f"- {node['label']}")
    for child in node.get('children', []):
        print_tree(child, indent + 1)

print_tree(hierarchy)
```

**Output esperado**:
```
- Documento
  - Documento Contractual
    - Contrato de Financiación
      - Préstamo Hipotecario
      - Préstamo Personal
      - Línea de Crédito
  - Documento de Identidad
    - DNI
    - Pasaporte
  - Documento Financiero
    - Factura
    - Nómina
```

#### 9. `get_statistics()`

Obtiene estadísticas del grafo RDF.

```python
stats = ontology_service.get_statistics()

print(f"Total triples: {stats['total_triples']}")
print(f"Total clases: {stats['total_classes']}")
print(f"Object Properties: {stats['total_object_properties']}")
print(f"Datatype Properties: {stats['total_datatype_properties']}")
```

**Output esperado**:
```
Total triples: 1250
Total clases: 35
Object Properties: 8
Datatype Properties: 18
```

---

## Endpoints de API REST

### Base URL
```
http://localhost:8000/api/v1/ontology
```

### 1. POST /ontology/classify

Clasifica un documento usando la ontología.

**Request**:
```json
{
  "content": "Contrato de préstamo hipotecario con garantía inmobiliaria...",
  "metadata": {
    "importeFinanciado": 200000,
    "ltv": 80.0,
    "plazoMeses": 240
  }
}
```

**Response**:
```json
{
  "class_uri": "http://tefinancia.es/ontology#PrestamoHipotecario",
  "class_name": "PrestamoHipotecario",
  "class_label": "Préstamo Hipotecario",
  "confidence": 0.85,
  "matched_keywords": ["préstamo hipotecario", "hipoteca", "garantía inmobiliaria"],
  "class_info": {
    "label": "Préstamo Hipotecario",
    "properties": {...}
  }
}
```

### 2. POST /ontology/validate

Valida metadatos contra restricciones OWL.

**Request**:
```json
{
  "class_name": "PrestamoHipotecario",
  "metadata": {
    "importeFinanciado": 200000,
    "tae": 3.5,
    "plazoMeses": 240,
    "ltv": 80.0
  }
}
```

**Response**:
```json
{
  "is_valid": true,
  "errors": [],
  "required_fields": ["tieneCliente", "requiereValoracion"],
  "missing_fields": []
}
```

### 3. POST /ontology/infer-risk

Infiere nivel de riesgo.

**Request**:
```json
{
  "class_name": "PrestamoHipotecario",
  "metadata": {
    "importeFinanciado": 250000,
    "ltv": 85.0,
    "tae": 4.2,
    "plazoMeses": 300
  }
}
```

**Response**:
```json
{
  "risk_level": "ALTO",
  "base_risk": "BAJO",
  "applied_rules": ["LTV > 80%", "Plazo > 20 años"],
  "explanation": "Riesgo base de PrestamoHipotecario: BAJO. LTV superior al 80% aumenta el riesgo. Plazo muy largo aumenta exposición al riesgo."
}
```

### 4. POST /ontology/sparql

Ejecuta consulta SPARQL personalizada.

**Request**:
```json
{
  "query": "PREFIX tf: <http://tefinancia.es/ontology#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n\nSELECT ?class ?label ?riskLevel WHERE {\n  ?class rdfs:subClassOf tf:ContratoFinanciacion .\n  ?class rdfs:label ?label .\n  ?class tf:nivelRiesgoBase ?riskLevel .\n}"
}
```

**Response**:
```json
{
  "results": [
    {
      "class": "http://tefinancia.es/ontology#PrestamoHipotecario",
      "label": "Préstamo Hipotecario",
      "riskLevel": "BAJO"
    },
    {
      "class": "http://tefinancia.es/ontology#PrestamoPersonal",
      "label": "Préstamo Personal",
      "riskLevel": "MEDIO"
    }
  ],
  "count": 2
}
```

### 5. GET /ontology/class/{class_name}

Obtiene información completa de una clase.

**Request**:
```
GET /ontology/class/PrestamoHipotecario
```

**Response**:
```json
{
  "uri": "http://tefinancia.es/ontology#PrestamoHipotecario",
  "label": "Préstamo Hipotecario",
  "comment": "Contrato de financiación con garantía inmobiliaria",
  "parent_classes": ["ContratoFinanciacion", "DocumentoContractual"],
  "properties": {
    "nivelRiesgoBase": ["BAJO"],
    "importeMinimo": [30000],
    "plazoMinimo": [60]
  },
  "required_fields": ["tieneCliente", "requiereValoracion"],
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
  "compliance_regulations": ["Ley Hipotecaria 5/2019", "MiFID II"]
}
```

### 6. GET /ontology/hierarchy

Obtiene jerarquía completa de clases.

**Request**:
```
GET /ontology/hierarchy?root_class=Documento
```

**Response**:
```json
{
  "root": {
    "uri": "http://tefinancia.es/ontology#Documento",
    "name": "Documento",
    "label": "Documento",
    "children": [
      {
        "uri": "http://tefinancia.es/ontology#DocumentoContractual",
        "name": "DocumentoContractual",
        "label": "Documento Contractual",
        "children": [...]
      }
    ]
  },
  "total_classes": 35
}
```

### 7. GET /ontology/statistics

Obtiene estadísticas de la ontología.

**Request**:
```
GET /ontology/statistics
```

**Response**:
```json
{
  "total_triples": 1250,
  "total_classes": 35,
  "total_object_properties": 8,
  "total_datatype_properties": 18
}
```

---

## Ejemplos Prácticos

### Ejemplo 1: Pipeline Completo de Clasificación y Validación

```python
from backend.services.ontology_service import ontology_service

# Paso 1: Clasificar documento
document_text = """
CONTRATO DE PRÉSTAMO HIPOTECARIO
Importe: 250.000 €
Plazo: 25 años (300 meses)
TAE: 3.8%
TIN: 3.2%
Garantía: Vivienda habitual en Madrid
Valor de tasación: 300.000 €
LTV: 83.33%
"""

classification = ontology_service.classify_document(document_text, {})
print(f"✅ Clasificado como: {classification['class_label']}")
print(f"   Confianza: {classification['confidence']:.2%}")

# Paso 2: Validar metadatos
class_uri = ontology_service.TF[classification['class_name']]
metadata = {
    "importeFinanciado": 250000,
    "tae": 3.8,
    "tin": 3.2,
    "plazoMeses": 300,
    "ltv": 83.33,
    "valorTasacion": 300000
}

is_valid, errors = ontology_service.validate_metadata(class_uri, metadata)
if is_valid:
    print("✅ Metadatos válidos")
else:
    print("❌ Errores:")
    for error in errors:
        print(f"   - {error}")

# Paso 3: Inferir nivel de riesgo
risk = ontology_service.infer_risk_level(class_uri, metadata)
print(f"⚠️  Nivel de riesgo: {risk}")

# Paso 4: Obtener documentos relacionados
related_docs = ontology_service.get_related_documents(class_uri)
print("\n📄 Documentos requeridos:")
for doc in related_docs:
    print(f"   - {doc['property']}: {doc['target']}")

# Paso 5: Obtener regulaciones
regulations = ontology_service.get_compliance_regulations(class_uri)
print("\n⚖️  Regulaciones aplicables:")
for reg in regulations:
    print(f"   - {reg}")
```

**Output esperado**:
```
✅ Clasificado como: Préstamo Hipotecario
   Confianza: 92.00%
✅ Metadatos válidos
⚠️  Nivel de riesgo: ALTO

📄 Documentos requeridos:
   - tieneCliente: Cliente
   - requiereValoracion: Valoracion
   - requiereDocumento: DNI

⚖️  Regulaciones aplicables:
   - Ley Hipotecaria 5/2019
   - MiFID II
   - Ley de Crédito Inmobiliario
```

### Ejemplo 2: Consulta SPARQL Avanzada

Encontrar todos los contratos de alto riesgo con TAE > 5%:

```python
query = """
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?contrato ?label ?riesgo ?taeMax WHERE {
    ?contrato rdfs:subClassOf* tf:ContratoFinanciacion .
    ?contrato rdfs:label ?label .
    ?contrato tf:nivelRiesgoBase ?riesgo .
    ?contrato tf:taeMaximo ?taeMax .
    
    FILTER(?riesgo = "ALTO" || ?taeMax > 5.0)
}
ORDER BY DESC(?taeMax)
"""

results = ontology_service.query_sparql(query)

print("🔴 Contratos de alto riesgo o TAE > 5%:")
for r in results:
    print(f"  - {r['label']}: Riesgo {r['riesgo']}, TAE máx {r['taeMax']}%")
```

### Ejemplo 3: Integración con API REST (curl)

```bash
# 1. Clasificar documento
curl -X POST http://localhost:8000/api/v1/ontology/classify \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Contrato de préstamo hipotecario...",
    "metadata": {"importeFinanciado": 200000}
  }'

# 2. Validar metadatos
curl -X POST http://localhost:8000/api/v1/ontology/validate \
  -H "Content-Type: application/json" \
  -d '{
    "class_name": "PrestamoHipotecario",
    "metadata": {"importeFinanciado": 200000, "tae": 3.5}
  }'

# 3. Inferir riesgo
curl -X POST http://localhost:8000/api/v1/ontology/infer-risk \
  -H "Content-Type: application/json" \
  -d '{
    "class_name": "PrestamoHipotecario",
    "metadata": {"ltv": 85.0, "tae": 4.2}
  }'

# 4. Obtener jerarquía
curl http://localhost:8000/api/v1/ontology/hierarchy

# 5. Información de clase
curl http://localhost:8000/api/v1/ontology/class/PrestamoHipotecario

# 6. Estadísticas
curl http://localhost:8000/api/v1/ontology/statistics
```

---

## Comparación con Taxonomía JSON

| Aspecto | Taxonomía JSON (Sprint 1) | Ontología OWL (Sprint 2+3) |
|---------|---------------------------|----------------------------|
| **Formato** | JSON jerárquico | RDF/Turtle (Grafo) |
| **Estándar** | Propietario | W3C (OWL 2, RDF, SPARQL) |
| **Jerarquía** | Árboles simples | Herencia múltiple |
| **Relaciones** | Implícitas | Explícitas (ObjectProperties) |
| **Validación** | Código Python | Restricciones OWL declarativas |
| **Inferencia** | No soportada | Razonamiento automático |
| **Consultas** | Navegación manual | SPARQL (SQL-like) |
| **Keywords** | No soportadas | SKOS annotations |
| **Regulaciones** | No asociadas | Anotaciones semánticas |
| **Interoperabilidad** | Baja | Alta (estándares abiertos) |
| **Complejidad** | Baja | Media-Alta |
| **Performance** | Muy rápida | Rápida (con índices) |
| **Mantenimiento** | Manual (editar JSON) | Manual (editar Turtle) |
| **Extensibilidad** | Limitada | Alta (importar ontologías) |

### Cuándo Usar Cada Una

#### Usar Taxonomía JSON cuando:
- ✅ Necesitas respuesta ultrarrápida
- ✅ Clasificación simple por nombre
- ✅ No requieres validación compleja
- ✅ Jerarquía estática y pequeña
- ✅ No necesitas interoperabilidad

#### Usar Ontología OWL cuando:
- ✅ Requieres validación formal
- ✅ Necesitas inferencia automática
- ✅ Consultas complejas (SPARQL)
- ✅ Relaciones semánticas explícitas
- ✅ Cumplimiento normativo estricto
- ✅ Interoperabilidad con sistemas externos
- ✅ Dominio complejo con muchas reglas

### Estrategia Híbrida (Recomendada)

1. **Primera clasificación**: Taxonomía JSON (rápida)
2. **Validación detallada**: Ontología OWL (precisa)
3. **Inferencia**: Ontología OWL (razonamiento)
4. **Navegación simple**: Taxonomía JSON
5. **Consultas avanzadas**: Ontología OWL (SPARQL)

```python
# Ejemplo de uso híbrido
from backend.services.taxonomy_service import taxonomy_service
from backend.services.ontology_service import ontology_service

# Clasificación rápida con taxonomía
taxonomy_class = taxonomy_service.classify_by_keywords(content)

# Validación precisa con ontología
ontology_class_uri = ontology_service.TF[taxonomy_class]
is_valid, errors = ontology_service.validate_metadata(
    ontology_class_uri, 
    metadata
)

# Inferencia con ontología
risk = ontology_service.infer_risk_level(ontology_class_uri, metadata)
```

---

## Próximos Pasos

### Mejoras Futuras

1. **Razonador OWL completo**: Integrar Pellet o HermiT para inferencia avanzada
2. **Importar ontologías externas**: FIBO (Financial Industry Business Ontology)
3. **Endpoint SPARQL público**: Triplestore como Apache Jena Fuseki
4. **Visualización de ontología**: Herramientas como WebVOWL o Protégé
5. **Versionado de ontología**: Control de cambios en OWL con Git
6. **Anotaciones semánticas automáticas**: NLP para enriquecer metadata

### Recursos Adicionales

- **OWL 2 Primer**: https://www.w3.org/TR/owl2-primer/
- **SPARQL 1.1 Query Language**: https://www.w3.org/TR/sparql11-query/
- **RDFLib Documentation**: https://rdflib.readthedocs.io/
- **Protégé Editor**: https://protege.stanford.edu/
- **SPARQL Examples**: Ver `docs/SPARQL_EXAMPLES.md`

---

## Soporte y Contacto

Para preguntas o problemas:
- **Documentación técnica**: `docs/TECHNICAL_ARCHITECTURE.md`
- **Ejemplos SPARQL**: `docs/SPARQL_EXAMPLES.md`
- **Resumen Sprint 2+3**: `docs/SPRINT2_3_SUMMARY.md`
- **Issues GitHub**: [Repositorio del proyecto]
