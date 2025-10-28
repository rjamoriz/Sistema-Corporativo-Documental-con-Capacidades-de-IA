# 🔍 Arize Phoenix - Integración con Servicios v2.0

## 📊 Estado Actual

### ✅ Phoenix Implementado en v1.0

Tienes Arize Phoenix configurado en:
- **Archivo:** `infrastructure/docker/docker-compose.yml`
- **Puerto:** 6006 (UI), 4317 (OTLP gRPC), 4318 (OTLP HTTP)
- **Documentación:** `docs/PHOENIX_OBSERVABILITY.md`
- **Configuración:** `backend/core/phoenix_config.py`

### 🎯 Objetivo

Integrar Phoenix con los nuevos servicios v2.0:
- GPU Embedding Service
- Quantum Services (D-Wave, IBM, NVIDIA)
- RAG Enhanced Service
- Prometheus/Grafana

---

## 🚀 Paso 1: Levantar Phoenix

### Opción A: Con tu Docker Compose Actual

```bash
# Ir al directorio de infraestructura
cd infrastructure/docker

# Levantar Phoenix
docker-compose up -d phoenix

# Verificar
docker ps | findstr phoenix

# Acceder a UI
# http://localhost:6006
```

### Opción B: Standalone

```bash
docker run -d \
  --name financia-phoenix \
  -p 6006:6006 \
  -p 4317:4317 \
  -p 4318:4318 \
  -v phoenix_data:/phoenix-data \
  --network financia-network \
  arizephoenix/phoenix:latest
```

---

## 🔗 Paso 2: Integrar con Servicios v2.0

### 2.1 Instrumentar RAG Enhanced Service

El RAG Enhanced Service ya tiene soporte para Phoenix. Solo necesitas configurarlo:

```python
# services/rag-enhanced/main.py ya tiene la estructura
# Solo necesitas añadir las variables de entorno
```

**Configuración en `.env`:**

```env
# Phoenix Configuration
PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:4317
PHOENIX_PROJECT_NAME=financia-rag-v2
ENABLE_PHOENIX_TRACING=true
```

### 2.2 Añadir Instrumentación a GPU Service

Crear archivo de instrumentación:

```python
# services/gpu-embedding/phoenix_instrumentation.py
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_phoenix_tracing():
    """Setup Phoenix tracing for GPU service"""
    if os.getenv("ENABLE_PHOENIX_TRACING", "false").lower() != "true":
        return
    
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:4317")
    
    # Setup tracer
    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()
    
    # Setup OTLP exporter
    otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    print(f"✅ Phoenix tracing enabled: {endpoint}")

# En main.py, añadir al inicio:
from phoenix_instrumentation import setup_phoenix_tracing
setup_phoenix_tracing()
```

### 2.3 Dashboard Unificado

Phoenix mostrará:

- **App v1.0**: Traces de tu backend actual
- **GPU Service**: Traces de embeddings
- **RAG Service**: Traces de queries LLM
- **Quantum Services**: Métricas de optimización

---

## 📊 Paso 3: Configuración Completa

### 3.1 Levantar Todo el Stack

```bash
# 1. Levantar Phoenix
cd infrastructure/docker
docker-compose up -d phoenix

# 2. Levantar servicios v2.0
cd ../..
docker-compose -f docker-compose.quantum-gpu.yml up -d

# 3. Verificar todo está corriendo
docker ps

# Deberías ver:
# - financia_backend
# - financia_frontend
# - financia-phoenix
# - financia_gpu_embedding
# - financia_quantum_dwave
# - etc.
```

### 3.2 Acceder a Phoenix UI

```
http://localhost:6006
```

**Verás:**

1. **Traces Tab**: Todas las llamadas a servicios
2. **Projects**: 
   - `financia-main` (app v1.0)
   - `financia-gpu` (GPU service)
   - `financia-rag-v2` (RAG enhanced)
3. **Evaluations**: Métricas de calidad
4. **Datasets**: Datos de training/testing

---

## 🎯 Paso 4: Monitoreo Integrado

### 4.1 Phoenix + Prometheus + Grafana

Tienes 3 sistemas de monitoreo:

| Sistema | Puerto | Propósito |
|---------|--------|----------|
| **Phoenix** | 6006 | Observabilidad LLM, traces, evaluaciones |
| **Prometheus** | 9090 | Métricas técnicas, performance |
| **Grafana** | 3001 | Dashboards visuales |

**Estrategia:**

- **Phoenix**: Para debugging LLM, calidad de respuestas, RAG
- **Prometheus**: Para métricas de sistema, latencia, throughput
- **Grafana**: Para visualización unificada

### 4.2 Crear Dashboard Unificado en Grafana

Grafana puede mostrar métricas de Phoenix:

```yaml
# monitoring/grafana/dashboards/unified-dashboard.json
{
  "dashboard": {
    "title": "FinancIA v2.0 - Unified Monitoring",
    "panels": [
      {
        "title": "GPU Embeddings Throughput",
        "targets": [{"expr": "rate(embeddings_generated_total[5m])"}]
      },
      {
        "title": "RAG Query Latency",
        "targets": [{"expr": "histogram_quantile(0.95, rag_duration_seconds)"}]
      },
      {
        "title": "Phoenix Traces (iframe)",
        "type": "text",
        "content": "<iframe src='http://localhost:6006' width='100%' height='600px'></iframe>"
      }
    ]
  }
}
```

---

## 🧪 Paso 5: Testing

### 5.1 Test Phoenix con RAG Service

```bash
# 1. Hacer una query RAG
curl -X POST http://localhost:8005/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué es la inteligencia artificial?",
    "documents": [
      {"id": "doc1", "text": "La IA es..."}
    ],
    "llm_provider": "openai"
  }'

# 2. Ver trace en Phoenix
# Abrir: http://localhost:6006
# Ir a "Traces" tab
# Verás el trace completo con:
#   - Query input
#   - Documents retrieved
#   - LLM call
#   - Response
#   - Latency
#   - Tokens used
```

### 5.2 Test Phoenix con GPU Service

```bash
# 1. Generar embeddings
curl -X POST http://localhost:8001/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test 1", "test 2"]}'

# 2. Ver en Phoenix
# Si instrumentación está activa, verás:
#   - Input texts
#   - Model used
#   - Device (GPU/CPU)
#   - Latency
```

---

## 📈 Métricas Clave en Phoenix

### Para RAG Service

- **Latency**: Tiempo total de query
- **Token Usage**: Tokens de input/output
- **Cost**: Costo estimado por query
- **Relevance**: Relevancia de documentos recuperados
- **Hallucination Score**: Detección de alucinaciones

### Para GPU Service

- **Throughput**: Embeddings por segundo
- **Batch Size**: Tamaño de batches
- **Device**: GPU vs CPU usage
- **Model**: Modelo usado

### Para Quantum Services

- **Problem Size**: Tamaño del problema QUBO
- **Solution Quality**: Energía de la solución
- **Iterations**: Iteraciones del algoritmo
- **Method**: QAOA, Simulated Annealing, etc.

---

## 🔧 Troubleshooting

### Phoenix No Muestra Traces

```bash
# 1. Verificar Phoenix está corriendo
docker logs financia-phoenix

# 2. Verificar endpoint OTLP
curl http://localhost:4318/v1/traces

# 3. Verificar variables de entorno en servicios
docker exec financia_gpu_embedding env | grep PHOENIX
```

### Servicios No Pueden Conectar a Phoenix

```bash
# Verificar red Docker
docker network inspect financia-network

# Conectar servicio a red si es necesario
docker network connect financia-network financia-phoenix
```

---

## 📚 Recursos

- **Phoenix UI**: http://localhost:6006
- **Phoenix Docs**: https://docs.arize.com/phoenix
- **OpenTelemetry**: https://opentelemetry.io/
- **Tu Documentación**: `docs/PHOENIX_OBSERVABILITY.md`

---

## ✅ Checklist de Integración

- [ ] Phoenix está corriendo (puerto 6006)
- [ ] Variables de entorno configuradas
- [ ] Servicios v2.0 levantados
- [ ] Phoenix UI accesible
- [ ] Traces aparecen en Phoenix
- [ ] Métricas en Prometheus
- [ ] Dashboard en Grafana

---

## 🎯 Próximos Pasos

1. **Configurar evaluaciones automáticas** en Phoenix
2. **Crear alertas** para calidad de respuestas
3. **A/B testing** de diferentes modelos
4. **Optimizar prompts** basado en métricas
5. **Integrar con CI/CD** para testing continuo

---

**© 2025 FinancIA 2030 Team**
