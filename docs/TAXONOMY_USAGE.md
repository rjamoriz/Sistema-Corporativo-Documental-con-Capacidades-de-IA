# 📚 Guía de Uso - Taxonomía Jerárquica

**Versión**: 1.0.0  
**Sprint**: 1 (Taxonomía JSON con 3 niveles)  
**Fecha**: 9 de Octubre 2025

---

## 🎯 Introducción

Esta guía explica cómo usar la **taxonomía jerárquica de 3 niveles** implementada en el Sprint 1 del desarrollo incremental de ontología.

### ¿Qué se implementó en Sprint 1?

✅ **Taxonomía JSON** con 39 clases organizadas en 3 niveles  
✅ **TaxonomyService** para navegación jerárquica  
✅ **API REST** completa con 15 endpoints  
✅ **Tests unitarios** verificados  
✅ **Validación de metadatos** según reglas de negocio  

### ¿Qué NO incluye Sprint 1?

❌ Razonamiento semántico (OWL/SPARQL) → Sprint 3  
❌ Inferencia automática de relaciones → Sprint 3  
❌ Ontología formal con propiedades → Sprint 3  

---

## 📊 Estructura de la Taxonomía

### Niveles Jerárquicos

```
Nivel 0: DOCUMENTO (raíz)
│
├── Nivel 1: Categorías principales (6)
│   ├── DOC_CONTRACTUAL
│   ├── DOC_ADMINISTRATIVO
│   ├── DOC_IDENTIFICACION
│   ├── DOC_FINANCIERO
│   ├── DOC_OPERACIONAL
│   └── DOC_CUMPLIMIENTO
│
├── Nivel 2: Tipos específicos (18)
│   ├── CONTRATO_FINANCIACION
│   ├── CONTRATO_PROVEEDOR
│   ├── FACTURA
│   ├── DNI
│   ├── NOMINA
│   └── ...
│
└── Nivel 3: Subtipos más detallados (4)
    ├── PRESTAMO_PERSONAL
    ├── PRESTAMO_HIPOTECARIO
    ├── PRESTAMO_AUTOMOVIL
    └── LINEA_CREDITO
```

### Ejemplo de Jerarquía Completa

```
DOCUMENTO
└── Documento Contractual
    └── Contrato de Financiación
        └── Préstamo Hipotecario
```

**Path completo**:
```
Documento > Documento Contractual > Contrato de Financiación > Préstamo Hipotecario
```

---

## 🔧 Uso del TaxonomyService

### 1. Inicialización

```python
from backend.services.taxonomy_service import taxonomy_service

# El servicio es un singleton, ya está inicializado
taxonomy = taxonomy_service
```

### 2. Navegación Jerárquica

#### Obtener información de una clase

```python
prestamo_hipotecario = taxonomy.get_class("PRESTAMO_HIPOTECARIO")

print(prestamo_hipotecario)
# {
#   "id": "PRESTAMO_HIPOTECARIO",
#   "label": "Préstamo Hipotecario",
#   "level": 3,
#   "parent": "CONTRATO_FINANCIACION",
#   "description": "Préstamo con garantía inmobiliaria",
#   "required_fields": ["importe_financiado", "tae", "tin", ...],
#   "retention_years": 20,
#   "risk_level": "BAJO",
#   ...
# }
```

#### Obtener hijos de una clase

```python
children = taxonomy.get_children("CONTRATO_FINANCIACION")

for child in children:
    print(f"- {child['label']} (Nivel {child['level']})")

# Salida:
# - Préstamo Personal (Nivel 3)
# - Préstamo Hipotecario (Nivel 3)
# - Préstamo para Vehículos (Nivel 3)
# - Línea de Crédito (Nivel 3)
```

#### Obtener padre de una clase

```python
parent = taxonomy.get_parent("PRESTAMO_PERSONAL")

print(f"Padre: {parent['label']}")
# Salida: Padre: Contrato de Financiación
```

#### Obtener todos los ancestros

```python
ancestors = taxonomy.get_ancestors("PRESTAMO_PERSONAL")

for ancestor in ancestors:
    print(f"↑ {ancestor['label']}")

# Salida:
# ↑ Contrato de Financiación
# ↑ Documento Contractual
# ↑ Documento
```

#### Obtener path completo

```python
path = taxonomy.get_path("PRESTAMO_PERSONAL")

print(path)
# Salida: Documento > Documento Contractual > Contrato de Financiación > Préstamo Personal
```

#### Obtener jerarquía completa como árbol

```python
hierarchy = taxonomy.get_hierarchy()

# Devuelve un árbol JSON completo:
# {
#   "id": "DOCUMENTO",
#   "label": "Documento",
#   "level": 0,
#   "children": [
#     {
#       "id": "DOC_CONTRACTUAL",
#       "label": "Documento Contractual",
#       "level": 1,
#       "children": [...]
#     },
#     ...
#   ]
# }
```

---

### 3. Campos y Validación

#### Obtener campos obligatorios

```python
required_fields = taxonomy.get_required_fields("PRESTAMO_PERSONAL")

for field in required_fields:
    print(f"✓ {field['name']} (obligatorio)")

# Salida:
# ✓ importe_financiado (obligatorio)
# ✓ tae (obligatorio)
# ✓ tin (obligatorio)
# ✓ plazo_meses (obligatorio)
# ✓ cuota_mensual (obligatorio)
# ✓ cliente_nif (obligatorio)
# ✓ ingresos_mensuales (obligatorio)
# ✓ scoring_crediticio (obligatorio)
```

#### Validar metadatos

```python
metadata = {
    "importe_financiado": 10000,
    "tae": 8.5,
    "tin": 7.5,
    "plazo_meses": 48,
    "cuota_mensual": 250,
    "cliente_nif": "12345678A",
    "ingresos_mensuales": 2000,
    "scoring_crediticio": 750
}

is_valid, errors = taxonomy.validate_metadata("PRESTAMO_PERSONAL", metadata)

if is_valid:
    print("✅ Metadatos válidos")
else:
    print("❌ Errores de validación:")
    for error in errors:
        print(f"  - {error}")
```

#### Validación con reglas de negocio

```python
# Ejemplo: Importe fuera de rango
metadata_invalid = {
    "importe_financiado": 1000,  # Mínimo es 3000
    # ... otros campos ...
}

is_valid, errors = taxonomy.validate_metadata("PRESTAMO_PERSONAL", metadata_invalid)

print(errors)
# Salida:
# [
#   "Campo obligatorio faltante: tae",
#   "Campo obligatorio faltante: tin",
#   ...,
#   "Importe 1000 menor que mínimo permitido 3000"
# ]
```

---

### 4. Búsqueda y Clasificación

#### Buscar por keyword

```python
results = taxonomy.search_by_keyword("hipoteca")

for result in results:
    print(f"📄 {result['label']}")
    print(f"   Path: {result['path']}")

# Salida:
# 📄 Préstamo Hipotecario
#    Path: Documento > Documento Contractual > Contrato de Financiación > Préstamo Hipotecario
```

#### Clasificar texto por keywords

```python
text = """
Solicito un préstamo hipotecario de 200.000€ para comprar una vivienda.
Necesito tasación del inmueble y garantía hipotecaria.
"""

classifications = taxonomy.classify_by_keywords(text, top_n=3)

for i, result in enumerate(classifications, 1):
    print(f"{i}. {result['label']} (confianza: {result['confidence']})")
    print(f"   Matches: {result['matches']} keywords")
    print(f"   Path: {result['path']}")

# Salida:
# 1. Préstamo Hipotecario (confianza: 0.4)
#    Matches: 2 keywords
#    Path: Documento > Documento Contractual > Contrato de Financiación > Préstamo Hipotecario
```

---

### 5. Propiedades y Metadatos

#### Nivel de riesgo

```python
risk_prestamo_hipotecario = taxonomy.get_risk_level("PRESTAMO_HIPOTECARIO")
print(f"Riesgo: {risk_prestamo_hipotecario}")  # Salida: BAJO

risk_linea_credito = taxonomy.get_risk_level("LINEA_CREDITO")
print(f"Riesgo: {risk_linea_credito}")  # Salida: ALTO
```

#### Años de retención

```python
retention = taxonomy.get_retention_years("PRESTAMO_HIPOTECARIO")
print(f"Retención: {retention} años")  # Salida: 20 años
```

#### Datos sensibles (GDPR)

```python
is_sensitive_dni = taxonomy.is_sensitive("DNI")
print(f"DNI es sensible: {is_sensitive_dni}")  # Salida: True

is_sensitive_factura = taxonomy.is_sensitive("FACTURA")
print(f"Factura es sensible: {is_sensitive_factura}")  # Salida: False
```

#### Regulaciones de compliance

```python
regulations = taxonomy.get_compliance_regulations("PRESTAMO_HIPOTECARIO")

print("Regulaciones aplicables:")
for reg in regulations:
    print(f"  ✓ {reg}")

# Salida:
# Regulaciones aplicables:
#   ✓ Ley Hipotecaria
#   ✓ Ley Crédito Inmobiliario
#   ✓ GDPR
```

#### Documentos relacionados

```python
related = taxonomy.get_related_documents("PRESTAMO_HIPOTECARIO")

print("Documentos típicamente asociados:")
for doc in related:
    print(f"  → {doc}")

# Salida:
# Documentos típicamente asociados:
#   → VALORACION_INMUEBLE
#   → ESCRITURA_COMPRAVENTA
#   → POLIZA_SEGURO
```

---

### 6. Estadísticas

```python
stats = taxonomy.get_statistics()

print(f"Total de clases: {stats['total_classes']}")
print(f"Profundidad máxima: {stats['max_depth']}")
print(f"Clases hoja: {stats['leaf_classes']}")
print(f"Clases sensibles: {stats['sensitive_classes']}")

print("\nClases por nivel:")
for level, count in stats['classes_by_level'].items():
    print(f"  Nivel {level}: {count} clases")

print("\nClases por riesgo:")
for risk, count in stats['classes_by_risk'].items():
    print(f"  {risk}: {count} clases")

# Salida:
# Total de clases: 29
# Profundidad máxima: 3
# Clases hoja: 22
# Clases sensibles: 5
#
# Clases por nivel:
#   Nivel 0: 1 clases
#   Nivel 1: 6 clases
#   Nivel 2: 18 clases
#   Nivel 3: 4 clases
#
# Clases por riesgo:
#   BAJO: 12 clases
#   MEDIO: 10 clases
#   ALTO: 5 clases
```

---

## 🌐 Uso de la API REST

### Base URL

```
http://localhost:8000/api/v1/taxonomy
```

### Endpoints Disponibles

#### 1. **GET** `/taxonomy/` - Información general

```bash
curl http://localhost:8000/api/v1/taxonomy/
```

**Respuesta**:
```json
{
  "name": "TeFinancia Corporate Taxonomy",
  "version": "1.0.0",
  "type": "hierarchical",
  "max_levels": 3,
  "description": "Taxonomía jerárquica de 3 niveles para documentos corporativos",
  "statistics": {
    "total_classes": 29,
    "max_depth": 3,
    ...
  }
}
```

---

#### 2. **GET** `/taxonomy/hierarchy` - Jerarquía completa

```bash
curl http://localhost:8000/api/v1/taxonomy/hierarchy
```

**Respuesta**: Árbol JSON completo con toda la jerarquía.

---

#### 3. **GET** `/taxonomy/class/{class_id}` - Detalles de clase

```bash
curl http://localhost:8000/api/v1/taxonomy/class/PRESTAMO_HIPOTECARIO
```

**Respuesta**:
```json
{
  "id": "PRESTAMO_HIPOTECARIO",
  "label": "Préstamo Hipotecario",
  "level": 3,
  "description": "Préstamo con garantía inmobiliaria",
  "parent": "CONTRATO_FINANCIACION",
  "children": [],
  "required_fields": ["importe_financiado", "tae", "tin", ...],
  "optional_fields": ["tipo_interes_fijo_variable", "seguro_vida", ...],
  "retention_years": 20,
  "risk_level": "BAJO",
  "is_sensitive": false,
  "keywords": ["préstamo hipotecario", "hipoteca", ...],
  "compliance_regulations": ["Ley Hipotecaria", "Ley Crédito Inmobiliario", "GDPR"],
  "validation_rules": {
    "importe_minimo": 30000,
    "importe_maximo": 1000000,
    ...
  },
  "related_documents": ["VALORACION_INMUEBLE", "ESCRITURA_COMPRAVENTA", "POLIZA_SEGURO"],
  "path": "Documento > Documento Contractual > Contrato de Financiación > Préstamo Hipotecario"
}
```

---

#### 4. **GET** `/taxonomy/class/{class_id}/children` - Hijos

```bash
curl http://localhost:8000/api/v1/taxonomy/class/CONTRATO_FINANCIACION/children
```

---

#### 5. **GET** `/taxonomy/class/{class_id}/parent` - Padre

```bash
curl http://localhost:8000/api/v1/taxonomy/class/PRESTAMO_PERSONAL/parent
```

---

#### 6. **GET** `/taxonomy/class/{class_id}/ancestors` - Ancestros

```bash
curl http://localhost:8000/api/v1/taxonomy/class/PRESTAMO_PERSONAL/ancestors
```

---

#### 7. **GET** `/taxonomy/class/{class_id}/path` - Path completo

```bash
curl http://localhost:8000/api/v1/taxonomy/class/PRESTAMO_PERSONAL/path
```

---

#### 8. **GET** `/taxonomy/search?keyword={keyword}` - Búsqueda

```bash
curl "http://localhost:8000/api/v1/taxonomy/search?keyword=hipoteca"
```

---

#### 9. **POST** `/taxonomy/classify?text={text}&top_n=3` - Clasificar

```bash
curl -X POST "http://localhost:8000/api/v1/taxonomy/classify?text=Quiero%20solicitar%20un%20pr%C3%A9stamo%20hipotecario&top_n=3"
```

**Respuesta**:
```json
[
  {
    "class_id": "PRESTAMO_HIPOTECARIO",
    "label": "Préstamo Hipotecario",
    "path": "Documento > Documento Contractual > Contrato de Financiación > Préstamo Hipotecario",
    "confidence": 0.4,
    "matches": 2,
    "method": "keyword_matching"
  }
]
```

---

#### 10. **POST** `/taxonomy/validate` - Validar metadatos

```bash
curl -X POST "http://localhost:8000/api/v1/taxonomy/validate?class_id=PRESTAMO_PERSONAL" \
  -H "Content-Type: application/json" \
  -d '{
    "importe_financiado": 10000,
    "tae": 8.5,
    "tin": 7.5,
    "plazo_meses": 48,
    "cuota_mensual": 250,
    "cliente_nif": "12345678A",
    "ingresos_mensuales": 2000,
    "scoring_crediticio": 750
  }'
```

**Respuesta**:
```json
{
  "valid": true,
  "errors": [],
  "class_id": "PRESTAMO_PERSONAL",
  "class_label": "Préstamo Personal"
}
```

---

#### 11. **GET** `/taxonomy/leaves` - Clases hoja

```bash
curl http://localhost:8000/api/v1/taxonomy/leaves
```

---

#### 12. **GET** `/taxonomy/statistics` - Estadísticas

```bash
curl http://localhost:8000/api/v1/taxonomy/statistics
```

---

#### 13. **GET** `/taxonomy/risk/{risk_level}` - Clases por riesgo

```bash
curl http://localhost:8000/api/v1/taxonomy/risk/ALTO
```

---

#### 14. **GET** `/taxonomy/sensitive` - Clases con datos sensibles

```bash
curl http://localhost:8000/api/v1/taxonomy/sensitive
```

---

#### 15. **GET** `/taxonomy/compliance/{regulation}` - Clases por regulación

```bash
curl http://localhost:8000/api/v1/taxonomy/compliance/GDPR
```

---

## 🧪 Testing

### Ejecutar tests

```bash
# Test rápido sin pytest
python -c "
exec(open('backend/services/taxonomy_service.py').read())
taxonomy = TaxonomyService()
print(f'Clases: {taxonomy.get_statistics()[\"total_classes\"]}')
print(f'✅ Taxonomía OK')
"
```

### Tests incluidos

✅ Carga de taxonomía  
✅ Navegación jerárquica (get_class, get_children, get_parent, get_ancestors)  
✅ Paths completos  
✅ Campos y validación  
✅ Búsqueda por keywords  
✅ Clasificación de texto  
✅ Propiedades (riesgo, retención, sensibilidad)  
✅ Estadísticas  

---

## 📝 Casos de Uso

### Caso 1: Clasificar un documento al subirlo

```python
def classify_document(file_content: str, filename: str):
    """Clasifica un documento usando la taxonomía"""
    
    # 1. Clasificar por keywords
    classifications = taxonomy.classify_by_keywords(file_content, top_n=3)
    
    if not classifications:
        return {"class_id": "OTRO", "confidence": 0.0}
    
    # 2. Obtener la clase con mayor confianza
    best_match = classifications[0]
    
    # 3. Obtener información adicional
    class_info = taxonomy.get_class(best_match["class_id"])
    
    return {
        "class_id": best_match["class_id"],
        "class_label": best_match["label"],
        "confidence": best_match["confidence"],
        "path": best_match["path"],
        "retention_years": class_info.get("retention_years"),
        "risk_level": class_info.get("risk_level"),
        "is_sensitive": class_info.get("is_sensitive", False)
    }
```

---

### Caso 2: Validar metadatos antes de guardar

```python
def validate_document_metadata(class_id: str, metadata: dict):
    """Valida metadatos según taxonomía"""
    
    # 1. Validar con taxonomía
    is_valid, errors = taxonomy.validate_metadata(class_id, metadata)
    
    if not is_valid:
        raise ValueError(f"Metadatos inválidos: {', '.join(errors)}")
    
    # 2. Enriquecer con propiedades de la clase
    class_info = taxonomy.get_class(class_id)
    
    metadata["_taxonomy"] = {
        "class_id": class_id,
        "class_label": class_info.get("label"),
        "retention_years": class_info.get("retention_years"),
        "risk_level": class_info.get("risk_level"),
        "compliance_regulations": class_info.get("compliance_regulations", [])
    }
    
    return metadata
```

---

### Caso 3: Buscar documentos similares

```python
def find_related_documents(doc_class_id: str):
    """Encuentra documentos relacionados según taxonomía"""
    
    # 1. Obtener documentos relacionados directos
    related = taxonomy.get_related_documents(doc_class_id)
    
    # 2. Obtener hermanos (misma categoría padre)
    parent = taxonomy.get_parent(doc_class_id)
    siblings = []
    if parent:
        siblings = [
            c["id"] for c in taxonomy.get_children(parent["id"])
            if c["id"] != doc_class_id
        ]
    
    # 3. Obtener documentos del mismo nivel de riesgo
    class_info = taxonomy.get_class(doc_class_id)
    risk_level = class_info.get("risk_level")
    
    # Query en base de datos (pseudocódigo)
    # documents = db.query(Document).filter(
    #     Document.classification.in_(related + siblings),
    #     Document.risk_level == risk_level
    # ).all()
    
    return {
        "direct_related": related,
        "siblings": siblings,
        "risk_level": risk_level
    }
```

---

## 🚀 Próximos Pasos (Sprint 2 y 3)

### Sprint 2: Ontología OWL Light (3 meses)

- [ ] Diseñar ontología OWL básica en Protégé
- [ ] 20-30 clases con jerarquías formales
- [ ] Relaciones básicas (sin inferencia)
- [ ] Exportar a OWL/Turtle

### Sprint 3: Ontología Completa (6 meses)

- [ ] Implementar OntologyService con RDFLib
- [ ] SPARQL endpoint
- [ ] Razonamiento automático (HermiT/Pellet)
- [ ] Inferencia de relaciones
- [ ] Validación semántica completa

---

## 📚 Referencias

- **Archivo de taxonomía**: `backend/config/taxonomy.json`
- **Servicio**: `backend/services/taxonomy_service.py`
- **API**: `backend/api/v1/taxonomy.py`
- **Tests**: `tests/test_taxonomy.py`
- **Documentación completa**: `docs/ONTOLOGY_CLARIFICATION.md`

---

**Última actualización**: 9 de Octubre 2025  
**Autor**: Equipo FinancIA 2030  
**Sprint**: 1 - Taxonomía Jerárquica JSON
