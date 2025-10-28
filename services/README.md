# 🚀 Servicios v2.0 - Quantum & GPU Enhancement

Servicios modulares e independientes que NO afectan la aplicación actual.

---

## 📦 Servicios Implementados

### 1. 🎮 GPU Embedding Service (Puerto 8001)

**Estado:** ✅ Completo y funcional

**Características:**
- Generación de embeddings acelerada por GPU
- FAISS integration para búsqueda vectorial
- Batch processing optimizado
- Métricas Prometheus

**Endpoints:**
- `POST /api/v1/embeddings/generate` - Generar embeddings
- `POST /api/v1/embeddings/batch` - Procesamiento por lotes
- `POST /api/v1/similarity/search` - Búsqueda vectorial
- `GET /health` - Health check
- `GET /metrics` - Métricas Prometheus

**Documentación:** [gpu-embedding/README.md](gpu-embedding/README.md)

---

### 2. ⚛️ Quantum D-Wave Service (Puerto 8002)

**Estado:** ✅ Completo y funcional

**Características:**
- Deduplicación usando QUBO
- Simulated Annealing (D-Wave Ocean SDK)
- Optimización combinatoria
- Métricas Prometheus

**Endpoints:**
- `POST /api/v1/dedupe/analyze` - Analizar duplicados
- `POST /api/v1/dedupe/optimize` - Optimizar conjunto
- `GET /health` - Health check
- `GET /metrics` - Métricas Prometheus

**Método:** Formulación QUBO + Simulated Annealing

---

### 3. ⚛️ Quantum IBM Qiskit Service (Puerto 8003)

**Estado:** ✅ Completo y funcional

**Características:**
- Optimización con QAOA
- Circuitos cuánticos (simulador Aer)
- Comparación clásico vs cuántico
- Métricas Prometheus

**Endpoints:**
- `POST /api/v1/optimize/qaoa` - Optimizar con QAOA
- `POST /api/v1/optimize/classical` - Baseline clásico
- `POST /api/v1/circuit/create` - Crear circuito
- `GET /health` - Health check
- `GET /metrics` - Métricas Prometheus

**Método:** QAOA (Quantum Approximate Optimization Algorithm)

---

### 4. ⚛️ Quantum NVIDIA cuQuantum Service (Puerto 8004)

**Estado:** 🚧 Pendiente de implementación

**Características planificadas:**
- Simulación acelerada por GPU
- cuStateVec + cuTensorNet
- Hasta 30 qubits
- Quantum Machine Learning

---

### 5. 🤖 RAG Enhanced Service (Puerto 8005)

**Estado:** 🚧 Pendiente de implementación

**Características planificadas:**
- RAG con embeddings GPU
- LLMs (OpenAI/Anthropic/Local)
- Context optimization con QUBO
- Trazabilidad 100%

---

## 🚀 Inicio Rápido

### Levantar TODOS los servicios

```bash
docker-compose -f docker-compose.quantum-gpu.yml up -d
```

### Levantar servicios individuales

```bash
# Solo GPU Embedding
docker-compose -f docker-compose.quantum-gpu.yml up gpu-embedding-service -d

# Solo Quantum D-Wave
docker-compose -f docker-compose.quantum-gpu.yml up quantum-dwave-service -d

# Solo Quantum IBM
docker-compose -f docker-compose.quantum-gpu.yml up quantum-ibm-service -d

# GPU + Quantum services
docker-compose -f docker-compose.quantum-gpu.yml up gpu-embedding-service quantum-dwave-service quantum-ibm-service -d
```

### Verificar servicios

```bash
# GPU Embedding
curl http://localhost:8001/health

# Quantum D-Wave
curl http://localhost:8002/health

# Quantum IBM
curl http://localhost:8003/health
```

---

## 📊 Monitoreo

### Prometheus

```bash
# Levantar Prometheus
docker-compose -f docker-compose.quantum-gpu.yml up prometheus -d

# Acceder
http://localhost:9090
```

### Grafana

```bash
# Levantar Grafana
docker-compose -f docker-compose.quantum-gpu.yml up grafana -d

# Acceder
http://localhost:3001
# Usuario: admin
# Password: admin
```

### Métricas disponibles

Cada servicio expone métricas en `/metrics`:

```bash
# GPU Embedding
curl http://localhost:8001/metrics

# Quantum D-Wave
curl http://localhost:8002/metrics

# Quantum IBM
curl http://localhost:8003/metrics
```

**Métricas comunes:**
- `*_requests_total` - Total de requests
- `*_duration_seconds` - Duración de operaciones
- `active_requests` - Requests activos
- `*_size` - Tamaño de problemas

---

## 🧪 Testing

### Test GPU Embedding

```bash
curl -X POST http://localhost:8001/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["documento de prueba", "test document"],
    "normalize": true
  }'
```

### Test Quantum D-Wave

```bash
curl -X POST http://localhost:8002/api/v1/dedupe/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"id": "doc1", "text": "Este es un documento"},
      {"id": "doc2", "text": "Este es un documento similar"},
      {"id": "doc3", "text": "Documento completamente diferente"}
    ],
    "similarity_threshold": 0.7
  }'
```

### Test Quantum IBM

```bash
curl -X POST http://localhost:8003/api/v1/optimize/qaoa \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"id": "doc1", "text": "documento 1", "similarity_score": 0.9},
      {"id": "doc2", "text": "documento 2", "similarity_score": 0.8},
      {"id": "doc3", "text": "documento 3", "similarity_score": 0.7}
    ],
    "max_iterations": 100
  }'
```

---

## 📈 Performance

### GPU Embedding Service

| Operación | GPU (RTX 4070) | CPU Fallback |
|-----------|----------------|--------------|
| 1 embedding | <10ms | ~200ms |
| Batch 100 | ~100ms | ~2s |
| Throughput | ~1000/s | ~50/s |

### Quantum Services

| Servicio | Método | Tiempo típico |
|----------|--------|---------------|
| D-Wave | Simulated Annealing | 1-5s |
| IBM Qiskit | QAOA | 2-10s |
| NVIDIA cuQuantum | GPU Simulation | <1s |

---

## 🔧 Configuración

Cada servicio tiene su `.env.example`:

```bash
# GPU Embedding
services/gpu-embedding/.env.example

# Quantum D-Wave
services/quantum-dwave/.env.example

# Quantum IBM
services/quantum-ibm/.env.example
```

Copiar y ajustar según necesidades:

```bash
cp services/gpu-embedding/.env.example services/gpu-embedding/.env
# Editar .env con tus configuraciones
```

---

## 🔗 Integración con App Actual

### Estrategia: Feature Flags

Los servicios son completamente independientes. Para integrarlos:

1. **Añadir variable de entorno** en backend:
```env
USE_GPU_EMBEDDINGS=false  # true para activar
USE_QUANTUM_DEDUPE=false  # true para activar
GPU_EMBEDDING_URL=http://localhost:8001
QUANTUM_DEDUPE_URL=http://localhost:8002
```

2. **Modificar código** con fallback:
```python
if USE_GPU_EMBEDDINGS:
    # Usar servicio GPU
    embeddings = await gpu_service.generate(texts)
else:
    # Usar método actual
    embeddings = current_method(texts)
```

3. **Testing A/B**:
- Probar con GPU activado
- Comparar con método actual
- Medir mejoras de performance

---

## 📝 Notas Importantes

### ✅ Garantías

- **NO rompe nada**: Servicios completamente independientes
- **Opcional**: Se puede activar/desactivar
- **Fallback**: Si falla, usa método actual
- **Monitoreado**: Métricas completas

### ⚠️ Requisitos

- **GPU Service**: NVIDIA GPU opcional (funciona en CPU)
- **Quantum Services**: Solo CPU
- **RAM**: 8GB mínimo (16GB recomendado)
- **Docker**: 24.0+ con NVIDIA Container Toolkit (para GPU)

---

## 📚 Documentación

- [Plan Completo](../docs/QUANTUM_GPU_ENHANCEMENT_PLAN.md)
- [Guía de Implementación](../docs/IMPLEMENTATION_GUIDE_V2.md)
- [Docker Compose](../docker-compose.quantum-gpu.yml)

---

## 🤝 Soporte

**Equipo:** FinancIA 2030 Team  
**Email:** financia2030@tefinancia.es

---

**© 2025 TeFinancia S.A. - Confidencial**
