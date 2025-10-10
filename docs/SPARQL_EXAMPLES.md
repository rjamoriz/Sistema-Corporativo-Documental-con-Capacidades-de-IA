# Ejemplos de Consultas SPARQL - TeFinancia Ontology

## 📋 Índice

- [Introducción a SPARQL](#introducción-a-sparql)
- [Prefijos y Namespaces](#prefijos-y-namespaces)
- [Consultas Básicas](#consultas-básicas)
- [Consultas de Jerarquía](#consultas-de-jerarquía)
- [Consultas con Filtros](#consultas-con-filtros)
- [Consultas de Propiedades](#consultas-de-propiedades)
- [Consultas de Restricciones](#consultas-de-restricciones)
- [Consultas Avanzadas](#consultas-avanzadas)
- [Consultas de Compliance](#consultas-de-compliance)
- [Optimización y Buenas Prácticas](#optimización-y-buenas-prácticas)

---

## Introducción a SPARQL

**SPARQL** (SPARQL Protocol and RDF Query Language) es un lenguaje de consulta para datos RDF, similar a SQL para bases de datos relacionales.

### Sintaxis Básica

```sparql
PREFIX prefijo: <URI_namespace>

SELECT ?variables
WHERE {
    ?sujeto predicado ?objeto .
    FILTER (condiciones)
}
ORDER BY ?variable
LIMIT 10
```

### Componentes Principales

- **PREFIX**: Define namespaces abreviados
- **SELECT**: Variables a retornar
- **WHERE**: Patrón de triples RDF (grafo a consultar)
- **FILTER**: Condiciones de filtrado
- **OPTIONAL**: Patrones opcionales
- **UNION**: Unión de patrones alternativos
- **ORDER BY**: Ordenamiento de resultados
- **LIMIT/OFFSET**: Paginación

---

## Prefijos y Namespaces

### Namespaces Usados en TeFinancia

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
```

### Significado de Cada Namespace

- **tf**: Ontología TeFinancia (clases y propiedades propias)
- **rdf**: Modelo RDF básico (tipo, subject, object)
- **rdfs**: RDF Schema (subClassOf, label, comment)
- **owl**: Web Ontology Language (Restriction, cardinality)
- **xsd**: XML Schema Datatypes (string, integer, decimal)
- **skos**: Simple Knowledge Organization System (definiciones, keywords)

---

## Consultas Básicas

### 1. Listar Todas las Clases OWL

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?class ?label
WHERE {
    ?class rdf:type owl:Class .
    OPTIONAL { ?class rdfs:label ?label }
}
ORDER BY ?label
```

**Uso en Python**:
```python
query = """..."""  # Query de arriba
results = ontology_service.query_sparql(query)
for r in results:
    print(f"{r['label']}: {r['class']}")
```

### 2. Obtener Información de una Clase Específica

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?property ?value
WHERE {
    tf:PrestamoHipotecario ?property ?value .
}
```

**Resultado esperado**:
```
property: rdfs:label, value: "Préstamo Hipotecario"
property: rdfs:subClassOf, value: tf:ContratoFinanciacion
property: tf:nivelRiesgoBase, value: "BAJO"
property: tf:importeMinimo, value: 30000
```

### 3. Contar Clases, Propiedades y Triples

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>

# Contar clases
SELECT (COUNT(DISTINCT ?class) AS ?total_classes)
WHERE {
    ?class rdf:type owl:Class .
}

# Contar Object Properties
SELECT (COUNT(DISTINCT ?prop) AS ?total_object_properties)
WHERE {
    ?prop rdf:type owl:ObjectProperty .
}

# Contar Datatype Properties
SELECT (COUNT(DISTINCT ?prop) AS ?total_datatype_properties)
WHERE {
    ?prop rdf:type owl:DatatypeProperty .
}

# Contar todos los triples
SELECT (COUNT(*) AS ?total_triples)
WHERE {
    ?s ?p ?o .
}
```

---

## Consultas de Jerarquía

### 4. Obtener Subclases Directas

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subclass ?label
WHERE {
    ?subclass rdfs:subClassOf tf:Documento .
    OPTIONAL { ?subclass rdfs:label ?label }
}
ORDER BY ?label
```

**Resultado esperado**:
```
DocumentoContractual - "Documento Contractual"
DocumentoIdentidad - "Documento de Identidad"
DocumentoFinanciero - "Documento Financiero"
DocumentoLegal - "Documento Legal"
```

### 5. Obtener Todas las Subclases (Transitivas)

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subclass ?label
WHERE {
    ?subclass rdfs:subClassOf* tf:Documento .
    ?subclass rdfs:label ?label .
    FILTER(?subclass != tf:Documento)
}
ORDER BY ?label
```

**Nota**: `rdfs:subClassOf*` significa "0 o más saltos" (transitivo).

### 6. Obtener la Ruta de Jerarquía Completa

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?child ?parent
WHERE {
    ?child rdfs:subClassOf ?parent .
    ?child rdfs:label ?childLabel .
    ?parent rdfs:label ?parentLabel .
}
ORDER BY ?parent ?child
```

**Visualización del resultado**:
```
PrestamoHipotecario -> ContratoFinanciacion
PrestamoPersonal -> ContratoFinanciacion
ContratoFinanciacion -> DocumentoContractual
DocumentoContractual -> Documento
```

### 7. Encontrar Clases Hoja (Sin Subclases)

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?leaf ?label
WHERE {
    ?leaf rdf:type owl:Class .
    ?leaf rdfs:label ?label .
    
    # No tiene subclases
    FILTER NOT EXISTS {
        ?subclass rdfs:subClassOf ?leaf .
        FILTER(?subclass != ?leaf)
    }
}
ORDER BY ?label
```

**Resultado esperado**: PrestamoHipotecario, DNI, Factura, etc.

---

## Consultas con Filtros

### 8. Documentos con Alto Riesgo

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?riesgo
WHERE {
    ?class tf:nivelRiesgoBase ?riesgo .
    ?class rdfs:label ?label .
    
    FILTER(?riesgo = "ALTO")
}
ORDER BY ?label
```

**Resultado esperado**:
```
LineaCredito - "Línea de Crédito" - ALTO
```

### 9. Contratos con Importe Mínimo Alto

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?importeMin
WHERE {
    ?class rdfs:subClassOf* tf:ContratoFinanciacion .
    ?class rdfs:label ?label .
    ?class tf:importeMinimo ?importeMin .
    
    FILTER(?importeMin >= 30000)
}
ORDER BY DESC(?importeMin)
```

**Resultado esperado**:
```
PrestamoHipotecario - "Préstamo Hipotecario" - 30000
```

### 10. Contratos con Plazo Largo

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?plazoMin ?plazoMax
WHERE {
    ?class rdfs:subClassOf* tf:ContratoFinanciacion .
    ?class rdfs:label ?label .
    OPTIONAL { ?class tf:plazoMinimo ?plazoMin }
    OPTIONAL { ?class tf:plazoMaximo ?plazoMax }
    
    FILTER(?plazoMax > 240)
}
ORDER BY DESC(?plazoMax)
```

### 11. Documentos Sensibles (GDPR)

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label
WHERE {
    ?class tf:esSensible true .
    ?class rdfs:label ?label .
}
ORDER BY ?label
```

**Resultado esperado**: DNI, Pasaporte, NIE, etc.

### 12. Filtro con Múltiples Condiciones (AND/OR)

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?riesgo ?taeMax
WHERE {
    ?class rdfs:subClassOf* tf:ContratoFinanciacion .
    ?class rdfs:label ?label .
    ?class tf:nivelRiesgoBase ?riesgo .
    OPTIONAL { ?class tf:taeMaximo ?taeMax }
    
    # Alto riesgo O TAE > 10%
    FILTER(?riesgo = "ALTO" || ?taeMax > 10.0)
}
ORDER BY ?label
```

---

## Consultas de Propiedades

### 13. Listar Todas las Object Properties

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?property ?label ?domain ?range
WHERE {
    ?property rdf:type owl:ObjectProperty .
    OPTIONAL { ?property rdfs:label ?label }
    OPTIONAL { ?property rdfs:domain ?domain }
    OPTIONAL { ?property rdfs:range ?range }
}
ORDER BY ?label
```

**Resultado esperado**:
```
tf:tieneCliente - "tiene cliente" - ContratoFinanciacion - Cliente
tf:requiereDocumento - "requiere documento" - Documento - Documento
tf:tieneGarantia - "tiene garantía" - ContratoFinanciacion - Garantia
```

### 14. Listar Todas las Datatype Properties

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?property ?label ?domain ?range
WHERE {
    ?property rdf:type owl:DatatypeProperty .
    OPTIONAL { ?property rdfs:label ?label }
    OPTIONAL { ?property rdfs:domain ?domain }
    OPTIONAL { ?property rdfs:range ?range }
}
ORDER BY ?label
```

### 15. Propiedades de una Clase Específica

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?property ?value
WHERE {
    # Propiedades directas
    tf:PrestamoHipotecario ?property ?value .
    
    # Excluir propiedades de sistema
    FILTER(?property != rdf:type)
}
```

### 16. Propiedades con Dominio Específico

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?property ?label ?range
WHERE {
    ?property rdf:type owl:DatatypeProperty .
    ?property rdfs:domain tf:ContratoFinanciacion .
    ?property rdfs:label ?label .
    OPTIONAL { ?property rdfs:range ?range }
}
ORDER BY ?label
```

**Resultado esperado**:
```
tf:importeFinanciado - "importe financiado" - xsd:decimal
tf:tae - "TAE" - xsd:decimal
tf:tin - "TIN" - xsd:decimal
tf:plazoMeses - "plazo en meses" - xsd:integer
```

---

## Consultas de Restricciones

### 17. Restricciones de Cardinalidad

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?class ?property ?cardinality
WHERE {
    ?class rdfs:subClassOf ?restriction .
    ?restriction rdf:type owl:Restriction .
    ?restriction owl:onProperty ?property .
    ?restriction owl:cardinality ?cardinality .
    
    ?class rdfs:label ?classLabel .
}
ORDER BY ?class ?property
```

**Resultado esperado**:
```
PrestamoHipotecario - tieneCliente - 1 (exactamente 1 cliente)
```

### 18. Restricciones de Cardinalidad Mínima

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?class ?property ?minCard
WHERE {
    ?class rdfs:subClassOf ?restriction .
    ?restriction rdf:type owl:Restriction .
    ?restriction owl:onProperty ?property .
    ?restriction owl:minCardinality ?minCard .
    
    ?class rdfs:label ?classLabel .
    FILTER(?minCard >= 1)
}
ORDER BY ?class ?property
```

**Resultado esperado**:
```
PrestamoHipotecario - requiereValoracion - 1 (al menos 1 valoración)
```

### 19. Restricciones someValuesFrom (Relaciones Obligatorias)

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?class ?property ?requiredClass
WHERE {
    ?class rdfs:subClassOf ?restriction .
    ?restriction rdf:type owl:Restriction .
    ?restriction owl:onProperty ?property .
    ?restriction owl:someValuesFrom ?requiredClass .
    
    ?class rdfs:label ?classLabel .
    ?requiredClass rdfs:label ?requiredLabel .
}
ORDER BY ?class ?property
```

**Uso**: Encontrar qué documentos requiere un contrato.

---

## Consultas Avanzadas

### 20. Análisis de Riesgo por Categoría

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?riesgo (COUNT(?class) AS ?total)
WHERE {
    ?class rdf:type owl:Class .
    ?class tf:nivelRiesgoBase ?riesgo .
}
GROUP BY ?riesgo
ORDER BY ?riesgo
```

**Resultado esperado**:
```
BAJO - 15 clases
MEDIO - 10 clases
ALTO - 3 clases
```

### 21. Documentos con Múltiples Regulaciones

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label (COUNT(?reg) AS ?num_regulaciones)
WHERE {
    ?class rdfs:label ?label .
    ?class tf:regulacionAplicable ?reg .
}
GROUP BY ?class ?label
HAVING (COUNT(?reg) > 1)
ORDER BY DESC(?num_regulaciones)
```

**Resultado esperado**:
```
PrestamoHipotecario - "Préstamo Hipotecario" - 3 regulaciones
```

### 22. Búsqueda por Keywords (Clasificación)

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?keyword
WHERE {
    ?class rdfs:label ?label .
    ?class tf:keyword ?keyword .
    
    # Buscar keywords que contengan "préstamo"
    FILTER(CONTAINS(LCASE(?keyword), "préstamo"))
}
ORDER BY ?class
```

**Uso**: Clasificar documentos por coincidencia de keywords.

### 23. Rango de Importes por Tipo de Contrato

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?importeMin ?importeMax
WHERE {
    ?class rdfs:subClassOf* tf:ContratoFinanciacion .
    ?class rdfs:label ?label .
    OPTIONAL { ?class tf:importeMinimo ?importeMin }
    OPTIONAL { ?class tf:importeMaximo ?importeMax }
}
ORDER BY ?importeMin
```

### 24. Documentos con Retención Larga

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?retencion
WHERE {
    ?class rdf:type owl:Class .
    ?class rdfs:label ?label .
    ?class tf:retencionAnios ?retencion .
    
    FILTER(?retencion >= 10)
}
ORDER BY DESC(?retencion)
```

**Resultado esperado**:
```
PrestamoHipotecario - "Préstamo Hipotecario" - 20 años
Escritura - "Escritura" - 30 años
```

### 25. UNION: Buscar en Múltiples Categorías

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?class ?label ?categoria
WHERE {
    {
        ?class rdfs:subClassOf* tf:ContratoFinanciacion .
        BIND("Contrato de Financiación" AS ?categoria)
    }
    UNION
    {
        ?class rdfs:subClassOf* tf:DocumentoIdentidad .
        BIND("Documento de Identidad" AS ?categoria)
    }
    
    ?class rdfs:label ?label .
}
ORDER BY ?categoria ?label
```

### 26. Construcción de Grafo de Dependencias

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?source ?sourceLabel ?target ?targetLabel
WHERE {
    ?source rdfs:label ?sourceLabel .
    ?source tf:requiereDocumento ?target .
    ?target rdfs:label ?targetLabel .
}
ORDER BY ?source
```

**Visualización**:
```
PrestamoHipotecario --requiereDocumento--> DNI
PrestamoHipotecario --requiereDocumento--> Valoracion
ContratoTrabajo --requiereDocumento--> DNI
```

### 27. OPTIONAL: Propiedades Opcionales

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?riesgo ?taeMax ?plazoMax
WHERE {
    ?class rdf:type owl:Class .
    ?class rdfs:label ?label .
    
    # Obligatorio
    ?class tf:nivelRiesgoBase ?riesgo .
    
    # Opcionales
    OPTIONAL { ?class tf:taeMaximo ?taeMax }
    OPTIONAL { ?class tf:plazoMaximo ?plazoMax }
}
ORDER BY ?label
```

---

## Consultas de Compliance

### 28. Listar Regulaciones por Documento

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?regulacion
WHERE {
    ?class rdf:type owl:Class .
    ?class rdfs:label ?label .
    ?class tf:regulacionAplicable ?regulacion .
}
ORDER BY ?label ?regulacion
```

**Resultado esperado**:
```
PrestamoHipotecario - "Préstamo Hipotecario" - "Ley Hipotecaria 5/2019"
PrestamoHipotecario - "Préstamo Hipotecario" - "MiFID II"
PrestamoHipotecario - "Préstamo Hipotecario" - "Ley de Crédito Inmobiliario"
DNI - "DNI" - "GDPR"
```

### 29. Documentos que Cumplen GDPR

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label
WHERE {
    ?class rdf:type owl:Class .
    ?class rdfs:label ?label .
    ?class tf:regulacionAplicable ?reg .
    
    FILTER(CONTAINS(?reg, "GDPR"))
}
ORDER BY ?label
```

### 30. Documentos Sensibles con Regulación

```sparql
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?regulacion
WHERE {
    ?class rdf:type owl:Class .
    ?class rdfs:label ?label .
    ?class tf:esSensible true .
    ?class tf:regulacionAplicable ?regulacion .
}
ORDER BY ?label
```

---

## Optimización y Buenas Prácticas

### 1. Usar FILTER en Lugar de BIND cuando Sea Posible

❌ **Ineficiente**:
```sparql
SELECT ?class WHERE {
    ?class rdf:type owl:Class .
    BIND(?class AS ?temp)
    FILTER(?temp = tf:PrestamoHipotecario)
}
```

✅ **Eficiente**:
```sparql
SELECT ?class WHERE {
    tf:PrestamoHipotecario rdf:type owl:Class .
    BIND(tf:PrestamoHipotecario AS ?class)
}
```

### 2. Limitar Resultados con LIMIT

```sparql
SELECT ?class ?label
WHERE {
    ?class rdf:type owl:Class .
    ?class rdfs:label ?label .
}
ORDER BY ?label
LIMIT 10
```

### 3. Usar OPTIONAL para Propiedades No Obligatorias

```sparql
SELECT ?class ?label ?riesgo ?taeMax
WHERE {
    ?class rdf:type owl:Class .
    ?class rdfs:label ?label .
    OPTIONAL { ?class tf:nivelRiesgoBase ?riesgo }
    OPTIONAL { ?class tf:taeMaximo ?taeMax }
}
```

### 4. Índices: Variables Más Específicas Primero

❌ **Lento**:
```sparql
SELECT ?class WHERE {
    ?class ?property ?value .
    ?class rdf:type owl:Class .
}
```

✅ **Rápido**:
```sparql
SELECT ?class WHERE {
    ?class rdf:type owl:Class .
    ?class ?property ?value .
}
```

### 5. Evitar Negaciones Complejas

Las consultas con `FILTER NOT EXISTS` pueden ser lentas en grafos grandes.

### 6. Usar COUNT(*) en Lugar de COUNT(?variable)

```sparql
SELECT (COUNT(*) AS ?total)
WHERE {
    ?class rdf:type owl:Class .
}
```

---

## Uso desde Python

### Ejemplo Completo

```python
from backend.services.ontology_service import ontology_service

# Query SPARQL
query = """
PREFIX tf: <http://tefinancia.es/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?riesgo WHERE {
    ?class rdfs:subClassOf* tf:ContratoFinanciacion .
    ?class rdfs:label ?label .
    ?class tf:nivelRiesgoBase ?riesgo .
    FILTER(?riesgo = "ALTO")
}
ORDER BY ?label
"""

# Ejecutar
results = ontology_service.query_sparql(query)

# Procesar resultados
for r in results:
    print(f"Clase: {r['label']}")
    print(f"  URI: {r['class']}")
    print(f"  Riesgo: {r['riesgo']}\n")
```

---

## Recursos Adicionales

- **SPARQL 1.1 Query Language**: https://www.w3.org/TR/sparql11-query/
- **SPARQL by Example**: https://www.w3.org/2009/Talks/0615-qbe/
- **RDFLib SPARQL**: https://rdflib.readthedocs.io/en/stable/intro_to_sparql.html
- **SPARQL Playground**: https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service

---

## Próximos Pasos

Ver también:
- `docs/ONTOLOGY_USAGE.md` - Guía completa de uso de la ontología
- `docs/SPRINT2_3_SUMMARY.md` - Resumen de implementación
- `ontology/tefinancia.ttl` - Archivo de ontología OWL
