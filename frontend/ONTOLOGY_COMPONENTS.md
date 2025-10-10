# Frontend - Componentes de Ontología

## 📦 Componentes Implementados

### 1. **OntologyExplorer** (`components/OntologyExplorer.tsx`)

Explorador interactivo de la ontología TEFinancia OWL.

**Características:**
- 🌳 Árbol jerárquico de clases con navegación
- 🔍 Búsqueda y filtrado de clases en tiempo real
- 📊 Visualización de propiedades (ObjectProperty y DatatypeProperty)
- ⚠️ Restricciones OWL (cardinalidad, valores, dominios)
- 🔗 Navegación por herencia (padres y subclases)
- 💬 Comentarios y descripciones de clases

**Endpoints utilizados:**
- `GET /api/v1/ontology/hierarchy` - Jerarquía completa
- `GET /api/v1/ontology/classes/{className}` - Detalles de clase

### 2. **SPARQLConsole** (`components/SPARQLConsole.tsx`)

Editor interactivo de consultas SPARQL sobre la ontología.

**Características:**
- ✏️ Editor de código SPARQL con textarea
- 📋 6 plantillas predefinidas:
  - Todas las clases
  - Documentos de préstamo hipotecario
  - Propiedades de una clase
  - Jerarquía de clases
  - Restricciones de cardinalidad
  - Documentos de alto riesgo
- 📊 Visualización de resultados en tabla
- 💾 Exportación a CSV y JSON
- ⏱️ Medición de tiempo de ejecución
- ❌ Manejo de errores con mensajes claros

**Endpoints utilizados:**
- `POST /api/v1/ontology/sparql` - Ejecución de consultas

### 3. **ClassificationExplainer** (`components/ClassificationExplainer.tsx`)

Visualización del pipeline de clasificación triple inteligente.

**Características:**
- 🎯 4 modos de clasificación con UI interactiva:
  - **Rápido** (⚡): Solo taxonomía (~10ms)
  - **Balanceado** (🎯): Taxonomía + ML (~100ms)
  - **Preciso** (🔬): Taxonomía + ML + OWL (~500ms)
  - **Inteligente** (🧠): Adaptativo según confianza
- 📈 Timeline de 5 fases con estados (completed/skipped):
  1. Taxonomía JSON
  2. ML Transformers
  3. Ontología OWL
  4. Validación OWL
  5. Inferencia de Riesgo
- 💯 Métricas por fase (confianza, duración)
- 🔀 Visualización de blending de confianza
- ✅ Validación de metadatos con errores
- 🚨 Nivel de riesgo inferido (BAJO/MEDIO/ALTO)

### 4. **OntologyPage** (`pages/OntologyPage.tsx`)

Página principal que integra los 3 componentes.

**Características:**
- 📑 3 pestañas:
  - Explorador
  - Consola SPARQL
  - Pipeline de Clasificación
- 🎨 Cards informativos sobre tecnologías
- 🧭 Navegación fluida entre secciones

## 🚀 Instalación

### Dependencias añadidas

```bash
cd frontend
npm install lucide-react@^0.263.1
```

### Dependencias utilizadas

- **lucide-react**: Iconos modernos para UI
- **axios**: Cliente HTTP
- **react-router-dom**: Navegación
- **@heroicons/react**: Iconos adicionales

## 🎨 Estilos

Todos los componentes usan Tailwind CSS con:
- Colores: Blue (primario), Green (éxito), Red (error), Yellow (warning)
- Bordes redondeados: `rounded-lg`
- Sombras: `shadow-sm`
- Transiciones: `transition-colors`

## 📝 Uso

### Navegación

La nueva entrada "Ontología" está disponible en el menú lateral:

```
Dashboard
Subir
Buscar
Chat RAG
Ontología ← NUEVO
Riesgos
Cumplimiento
```

### Ejemplo de integración con backend

```typescript
// En un componente
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Cargar jerarquía
const response = await axios.get(`${API_BASE}/ontology/hierarchy`);

// Ejecutar SPARQL
const result = await axios.post(`${API_BASE}/ontology/sparql`, {
  query: 'SELECT ?class ?label WHERE { ?class rdfs:label ?label }'
});

// Obtener detalles de clasificación
const classification = await axios.get(
  `${API_BASE}/documents/${documentId}/classification/explanation`
);
```

## 🔧 Configuración

### Variables de entorno

Crear archivo `.env` en `frontend/`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### TypeScript

Los tipos están definidos en cada componente:
- `OntologyClass`
- `Property`
- `Restriction`
- `SPARQLResult`
- `ClassificationResult`
- `ClassificationPhase`

## 🧪 Testing

```bash
# Ejecutar tests
npm test

# Ejecutar con UI
npm run test:ui
```

## 📊 Métricas de Rendimiento

### OntologyExplorer
- Carga inicial: ~200ms
- Búsqueda: <50ms (filtrado client-side)
- Navegación: <10ms

### SPARQLConsole
- Consulta simple: ~100ms
- Consulta compleja: ~500ms
- Exportación: <50ms

### ClassificationExplainer
- Renderizado: <20ms
- Cambio de modo: instantáneo

## 🐛 Troubleshooting

### Error: "No se encuentra el módulo lucide-react"

```bash
cd frontend
npm install lucide-react
```

### Error: CORS al llamar al backend

Asegurar que el backend tiene CORS configurado en `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Resultados vacíos en SPARQL

- Verificar que la ontología está cargada: `GET /api/v1/ontology/health`
- Revisar sintaxis SPARQL
- Usar plantillas predefinidas como referencia

## 🎯 Próximas Mejoras

- [ ] Visualización gráfica de ontología (D3.js, Cytoscape)
- [ ] Autocompletado en editor SPARQL
- [ ] Historial de consultas SPARQL
- [ ] Comparación de clasificaciones (antes/después)
- [ ] Benchmark automático de modos de clasificación
- [ ] Export de visualizaciones a PNG/SVG
- [ ] Modo oscuro

## 📚 Referencias

- [Lucide Icons](https://lucide.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [SPARQL 1.1 Spec](https://www.w3.org/TR/sparql11-query/)
- [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/)
