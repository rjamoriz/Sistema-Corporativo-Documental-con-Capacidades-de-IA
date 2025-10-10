# Servidor MCP para Ontología TEFinancia

## 📋 Descripción

Servidor **Model Context Protocol (MCP)** que expone la ontología OWL de TEFinancia a Claude Desktop, permitiendo consultas semánticas, clasificación inteligente y validación de documentos financieros.

## 🎯 Casos de Uso

### 1. **Exploración de Ontología**
```
Usuario: ¿Qué tipos de documentos financieros puedes clasificar?
Claude: [Usa get_ontology_classes] Puedo clasificar 20+ tipos...
```

### 2. **Consultas SPARQL**
```
Usuario: Muéstrame todos los préstamos hipotecarios con LTV > 80%
Claude: [Usa execute_sparql con query específica] Aquí están los resultados...
```

### 3. **Clasificación Inteligente**
```
Usuario: Clasifica este documento: "Contrato de préstamo hipotecario..."
Claude: [Usa classify_document] Este documento es un PrestamoHipotecario (93% confianza)...
```

### 4. **Validación de Metadatos**
```
Usuario: ¿Son válidos estos metadatos para un préstamo hipotecario?
Claude: [Usa validate_metadata] Los metadatos tienen 2 errores...
```

### 5. **Análisis de Riesgo**
```
Usuario: ¿Cuál es el nivel de riesgo de este préstamo con LTV=85%?
Claude: [Usa infer_risk_level] El nivel de riesgo es ALTO porque...
```

## 🛠️ Herramientas MCP Disponibles

### 1. `get_ontology_classes`
Obtiene la lista completa de clases OWL.

**Parámetros:**
- `include_properties` (bool): Incluir propiedades de cada clase

**Retorna:**
```json
[
  {
    "uri": "http://www.tefinancia.com/ontology#PrestamoHipotecario",
    "name": "PrestamoHipotecario",
    "label": "Préstamo Hipotecario",
    "comment": "Préstamo garantizado con hipoteca sobre inmueble",
    "parent_classes": ["http://www.tefinancia.com/ontology#Prestamo"]
  }
]
```

### 2. `get_class_details`
Información detallada de una clase específica.

**Parámetros:**
- `class_name` (str): Nombre de la clase (ej: "PrestamoHipotecario")

**Retorna:**
```json
{
  "name": "PrestamoHipotecario",
  "label": "Préstamo Hipotecario",
  "comment": "...",
  "parent_classes": [...],
  "subclasses": [...],
  "properties": [
    {
      "name": "importeFinanciado",
      "label": "Importe Financiado",
      "type": "DatatypeProperty"
    }
  ],
  "restrictions": [
    {
      "property": "importeFinanciado",
      "type": "MinInclusive",
      "value": 30000
    }
  ],
  "required_fields": ["tieneCliente", "requiereValoracion"]
}
```

### 3. `execute_sparql`
Ejecuta consulta SPARQL sobre la ontología.

**Parámetros:**
- `query` (str): Consulta SPARQL
- `limit` (int): Límite de resultados (default: 100)

**Ejemplo de consulta:**
```sparql
PREFIX tf: <http://www.tefinancia.com/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?class ?label ?comment
WHERE {
  ?class rdfs:subClassOf tf:Prestamo .
  ?class rdfs:label ?label .
  OPTIONAL { ?class rdfs:comment ?comment }
}
```

**Retorna:**
```json
{
  "columns": ["class", "label", "comment"],
  "rows": [
    {
      "class": "PrestamoHipotecario",
      "label": "Préstamo Hipotecario",
      "comment": "..."
    }
  ],
  "count": 5
}
```

### 4. `classify_document`
Clasifica un documento usando ontología OWL.

**Parámetros:**
- `content` (str): Contenido textual del documento
- `metadata` (dict): Metadatos opcionales

**Retorna:**
```json
{
  "class_name": "PrestamoHipotecario",
  "class_label": "Préstamo Hipotecario",
  "confidence": 0.93,
  "matched_keywords": ["préstamo hipotecario", "hipoteca", "vivienda"],
  "method": "ontology_keywords"
}
```

### 5. `validate_metadata`
Valida metadatos contra restricciones OWL.

**Parámetros:**
- `class_name` (str): Nombre de la clase OWL
- `metadata` (dict): Metadatos a validar

**Retorna:**
```json
{
  "is_valid": false,
  "errors": [
    "importeFinanciado debe ser >= 30000",
    "ltv debe ser <= 100"
  ],
  "required_fields": ["tieneCliente", "requiereValoracion"]
}
```

### 6. `infer_risk_level`
Infiere nivel de riesgo basándose en reglas de negocio.

**Parámetros:**
- `class_name` (str): Nombre de la clase OWL
- `metadata` (dict): Metadatos del documento

**Retorna:**
```json
{
  "risk_level": "ALTO",
  "class_name": "PrestamoHipotecario",
  "metadata": {
    "ltv": 85,
    "tae": 8.5,
    "plazoMeses": 300
  }
}
```

**Reglas de inferencia:**
- LTV > 80% → ALTO
- TAE > 10% → ALTO
- esSensible = true → ALTO
- Tipo = LineaCredito → ALTO
- plazoMeses > 240 → MEDIO (upgrade de BAJO)

### 7. `get_ontology_hierarchy`
Obtiene jerarquía de clases en formato árbol.

**Parámetros:**
- `root_class` (str): Clase raíz (default: "DocumentoCorporativo")

**Retorna:**
```json
{
  "class_info": {
    "name": "DocumentoCorporativo",
    "label": "Documento Corporativo"
  },
  "children": [
    {
      "class_info": {
        "name": "ProductoFinanciero",
        "label": "Producto Financiero"
      },
      "children": [...]
    }
  ]
}
```

### 8. `search_by_keywords`
Búsqueda rápida por keywords usando taxonomía JSON.

**Parámetros:**
- `text` (str): Texto para buscar

**Retorna:**
```json
{
  "class_id": "PrestamoHipotecario",
  "class_label": "Préstamo Hipotecario",
  "confidence": 0.85,
  "path": ["ProductoFinanciero", "Prestamo", "PrestamoHipotecario"],
  "matched_keywords": ["hipoteca", "préstamo"]
}
```

## 📦 Instalación

### 1. Instalar dependencias MCP

```bash
pip install mcp
```

### 2. Configurar Claude Desktop

**En macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**En Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**En Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 3. Añadir configuración

Copiar el contenido de `claude_desktop_config.json` y **actualizar las rutas absolutas**:

```json
{
  "mcpServers": {
    "tefinancia-ontology": {
      "command": "python",
      "args": [
        "/ruta/absoluta/a/Sistema-Corporativo-Documental/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/ruta/absoluta/a/Sistema-Corporativo-Documental/backend"
      },
      "description": "Servidor MCP para Ontología TEFinancia",
      "disabled": false
    }
  }
}
```

### 4. Reiniciar Claude Desktop

Cerrar completamente Claude Desktop y volver a abrirlo.

## 🧪 Verificación

### Desde Claude Desktop

```
Usuario: ¿Qué herramientas MCP tienes disponibles?

Claude: Tengo disponibles las siguientes herramientas de TEFinancia:
- get_ontology_classes
- get_class_details
- execute_sparql
- classify_document
- validate_metadata
- infer_risk_level
- get_ontology_hierarchy
- search_by_keywords
```

### Prueba básica

```
Usuario: ¿Cuántas clases de documentos financieros existen en la ontología?

Claude: [Llama a get_ontology_classes]
Hay 23 clases de documentos financieros en la ontología TEFinancia:
1. Préstamo Hipotecario
2. Préstamo Personal
3. Tarjeta de Crédito
...
```

## 🎓 Ejemplos de Uso Avanzado

### Ejemplo 1: Análisis Completo de Documento

```
Usuario: Analiza completamente este documento:

"Contrato de Préstamo Hipotecario
Importe: 250,000€
Plazo: 25 años
LTV: 75%
TAE: 3.5%"

Claude:
1. [classify_document] → PrestamoHipotecario (95% confianza)
2. [validate_metadata] → Metadatos válidos ✓
3. [infer_risk_level] → Riesgo BAJO
4. [get_class_details] → Propiedades requeridas: ...

Análisis completo:
- Tipo: Préstamo Hipotecario
- Confianza: 95%
- Estado: Válido
- Riesgo: BAJO (LTV < 80%, TAE < 10%)
- Propiedades faltantes: Ninguna
```

### Ejemplo 2: Consulta Compleja SPARQL

```
Usuario: Muéstrame estadísticas de documentos por tipo de riesgo

Claude: [execute_sparql con agregaciones]

SELECT ?risk (COUNT(?doc) as ?count)
WHERE {
  ?doc rdf:type ?type .
  ?doc tf:nivelRiesgo ?risk .
}
GROUP BY ?risk
ORDER BY DESC(?count)

Resultados:
- BAJO: 150 documentos
- MEDIO: 75 documentos
- ALTO: 25 documentos
```

### Ejemplo 3: Validación Batch

```
Usuario: Valida estos 3 documentos y resume los errores

Claude:
[validate_metadata para cada uno]

Documento 1: ✓ Válido
Documento 2: ✗ 2 errores
  - importeFinanciado < 30000
  - plazoMeses > 480
Documento 3: ✓ Válido

Resumen: 2/3 válidos (66%)
```

## 🔧 Troubleshooting

### Error: "No se puede conectar al servidor MCP"

1. Verificar que las rutas en `claude_desktop_config.json` son absolutas y correctas
2. Verificar que Python está en el PATH
3. Revisar logs en: `~/Library/Logs/Claude/mcp-server-tefinancia-ontology.log`

### Error: "Módulo 'mcp' no encontrado"

```bash
pip install mcp
```

### Error: "No se puede importar ontology_service"

Asegurar que `PYTHONPATH` apunta al directorio `backend`:

```json
"env": {
  "PYTHONPATH": "/ruta/absoluta/backend"
}
```

### Error: "Ontología no cargada"

Verificar que el archivo `ontology/tefinancia.ttl` existe y es válido.

## 📊 Métricas de Rendimiento

### Tiempos de respuesta típicos

| Herramienta | Tiempo | Carga |
|-------------|--------|-------|
| get_ontology_classes | ~50ms | Ligera |
| get_class_details | ~20ms | Ligera |
| execute_sparql (simple) | ~100ms | Media |
| execute_sparql (compleja) | ~500ms | Alta |
| classify_document | ~200ms | Media |
| validate_metadata | ~10ms | Ligera |
| infer_risk_level | ~5ms | Ligera |

## 🚀 Próximas Mejoras

- [ ] Streaming de resultados SPARQL largos
- [ ] Cache de consultas frecuentes
- [ ] Soporte para múltiples ontologías
- [ ] Webhooks para actualizaciones de ontología
- [ ] Métricas y telemetría
- [ ] Rate limiting
- [ ] Autenticación y permisos

## 📚 Referencias

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [RDFLib Documentation](https://rdflib.readthedocs.io/)
- [SPARQL 1.1 Specification](https://www.w3.org/TR/sparql11-query/)
- [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/)

## 📄 Licencia

Este servidor MCP es parte del Sistema Corporativo Documental con Capacidades de IA.

## 👥 Soporte

Para issues o preguntas sobre el servidor MCP, abrir un issue en el repositorio GitHub.
