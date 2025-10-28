# 🧪 Guía Completa de Testing - Servicios v2.0

**Fecha:** Octubre 2025  
**Estado:** ✅ Todos los servicios implementados

---

## 📋 Tabla de Contenidos

- [Prerequisitos](#-prerequisitos)
- [Levantar Servicios](#-levantar-servicios)
- [Testing por Servicio](#-testing-por-servicio)
- [Testing Integrado](#-testing-integrado)
- [Benchmarks](#-benchmarks)
- [Troubleshooting](#-troubleshooting)

---

## 🔧 Prerequisitos

### Software Requerido

```bash
# Docker Desktop con NVIDIA Container Toolkit (para GPU)
docker --version  # >= 24.0

# Docker Compose
docker-compose --version  # >= 2.20

# curl (para testing)
curl --version

# (Opcional) Python 3.10+ para testing local
python --version
```

### Verificar GPU (Opcional)

```bash
# Verificar NVIDIA driver
nvidia-smi

# Verificar Docker con GPU
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

---

## 🚀 Levantar Servicios

### Opción 1: Todos los Servicios

```bash
cd "Sistema-Corporativo-Documental-con-Capacidades-de-IA"

# Levantar TODO (GPU + Quantum + RAG + Monitoring)
docker-compose -f docker-compose.quantum-gpu.yml up -d

# Ver logs
docker-compose -f docker-compose.quantum-gpu.yml logs -f

# Ver estado
docker-compose -f docker-compose.quantum-gpu.yml ps
```

### Opción 2: Servicios Individuales

```bash
# Solo GPU Embedding
docker-compose -f docker-compose.quantum-gpu.yml up gpu-embedding-service -d

# Solo Quantum services
docker-compose -f docker-compose.quantum-gpu.yml up quantum-dwave-service quantum-ibm-service quantum-nvidia-service -d

# Solo RAG Enhanced
docker-compose -f docker-compose.quantum-gpu.yml up rag-enhanced-service gpu-embedding-service -d

# Solo Monitoring
docker-compose -f docker-compose.quantum-gpu.yml up prometheus grafana -d
```

### Opción 3: Testing Mínimo

```bash
# GPU + 1 Quantum service para testing rápido
docker-compose -f docker-compose.quantum-gpu.yml up gpu-embedding-service quantum-dwave-service -d
```

---

## 🧪 Testing por Servicio

### 1. GPU Embedding Service (Puerto 8001)

#### Health Check

```bash
curl http://localhost:8001/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "gpu_available": true,
  "device": "cuda",
  "model_loaded": true,
  "faiss_index_size": 0
}
```

#### Test: Generar Embeddings

```bash
curl -X POST http://localhost:8001/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hola mundo", "Hello world", "Bonjour monde"],
    "normalize": true
  }'
```

**Validar:**
- ✅ Status code: 200
- ✅ Respuesta contiene `embeddings` array
- ✅ Cada embedding tiene 768 dimensiones
- ✅ `device_used`: "cuda" o "cpu"

#### Test: Batch Processing

```bash
curl -X POST http://localhost:8001/api/v1/embeddings/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["doc1", "doc2", "doc3", "doc4", "doc5"],
    "batch_size": 2
  }'
```

#### Test: Búsqueda Vectorial

```bash
# 1. Añadir documentos al índice
curl -X POST http://localhost:8001/api/v1/index/add \
  -H "Content-Type: application/json" \
  -d '["documento sobre IA", "documento sobre machine learning", "documento sobre cocina"]'

# 2. Buscar similares
curl -X POST http://localhost:8001/api/v1/similarity/search \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "inteligencia artificial",
    "top_k": 2
  }'
```

**Validar:**
- ✅ Documentos sobre IA/ML tienen mayor similitud
- ✅ Documento sobre cocina tiene menor similitud

#### Test: Métricas

```bash
curl http://localhost:8001/metrics | grep embeddings_generated_total
```

---

### 2. Quantum D-Wave Service (Puerto 8002)

#### Health Check

```bash
curl http://localhost:8002/health
```

#### Test: Deduplicación

```bash
curl -X POST http://localhost:8002/api/v1/dedupe/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"id": "doc1", "text": "Este es un documento sobre inteligencia artificial"},
      {"id": "doc2", "text": "Este es un documento sobre inteligencia artificial y ML"},
      {"id": "doc3", "text": "Documento completamente diferente sobre cocina"},
      {"id": "doc4", "text": "Receta de paella valenciana"},
      {"id": "doc5", "text": "Este documento trata sobre IA y machine learning"}
    ],
    "similarity_threshold": 0.7
  }'
```

**Validar:**
- ✅ doc1, doc2, doc5 deberían agruparse (similares)
- ✅ doc3, doc4 deberían estar separados
- ✅ `method_used`: "simulated_annealing_qubo"
- ✅ `energy` es un número negativo

#### Test: Optimización

```bash
curl -X POST http://localhost:8002/api/v1/dedupe/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"id": "doc1", "text": "documento 1"},
      {"id": "doc2", "text": "documento 2"},
      {"id": "doc3", "text": "documento 3"},
      {"id": "doc4", "text": "documento 4"}
    ],
    "target_reduction": 0.3
  }'
```

**Validar:**
- ✅ `reduction_percentage` cercano a 30%
- ✅ `optimized_documents` y `removed_documents` están balanceados

---

### 3. Quantum IBM Qiskit Service (Puerto 8003)

#### Health Check

```bash
curl http://localhost:8003/health
```

#### Test: Optimización QAOA

```bash
curl -X POST http://localhost:8003/api/v1/optimize/qaoa \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"id": "doc1", "text": "documento 1", "similarity_score": 0.9},
      {"id": "doc2", "text": "documento 2", "similarity_score": 0.8},
      {"id": "doc3", "text": "documento 3", "similarity_score": 0.7},
      {"id": "doc4", "text": "documento 4", "similarity_score": 0.6}
    ],
    "max_iterations": 50
  }'
```

**Validar:**
- ✅ `method_used`: "QAOA"
- ✅ `selected_documents` contiene IDs
- ✅ `reduction_percentage` > 0
- ✅ `optimal_value` es un número

#### Test: Comparación Clásico vs Cuántico

```bash
# Clásico
curl -X POST http://localhost:8003/api/v1/optimize/classical \
  -H "Content-Type: application/json" \
  -d '[
    {"id": "doc1", "text": "doc1", "similarity_score": 0.9},
    {"id": "doc2", "text": "doc2", "similarity_score": 0.5}
  ]'

# Cuántico (QAOA) - usar endpoint anterior
```

#### Test: Crear Circuito Cuántico

```bash
curl -X POST http://localhost:8003/api/v1/circuit/create?num_qubits=3&depth=2
```

**Validar:**
- ✅ `circuit_diagram` muestra el circuito
- ✅ `num_gates` > 0
- ✅ `operations` lista las operaciones

---

### 4. Quantum NVIDIA cuQuantum Service (Puerto 8004)

#### Health Check

```bash
curl http://localhost:8004/health
```

#### Test: Simulación Cuántica

```bash
curl -X POST http://localhost:8004/api/v1/simulate/circuit \
  -H "Content-Type: application/json" \
  -d '{
    "num_qubits": 5,
    "depth": 3,
    "shots": 1024,
    "use_gpu": true
  }'
```

**Validar:**
- ✅ `counts` contiene resultados de medición
- ✅ `device_used`: "GPU" o "CPU"
- ✅ `execution_time` < 1 segundo (con GPU)

#### Test: Quantum ML Classification

```bash
curl -X POST http://localhost:8004/api/v1/ml/classify \
  -H "Content-Type: application/json" \
  -d '{
    "features": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
    "labels": [0, 1],
    "test_features": [[0.15, 0.25, 0.35]]
  }'
```

**Validar:**
- ✅ `predictions` contiene clasificaciones (0 o 1)
- ✅ `method`: "quantum_variational_classifier"

#### Test: Benchmark GPU vs CPU

```bash
curl -X POST "http://localhost:8004/api/v1/benchmark/compare?num_qubits=10&depth=5&shots=1024"
```

**Validar:**
- ✅ `cpu_time` > 0
- ✅ `gpu_time` > 0 (si GPU disponible)
- ✅ `speedup` > 1 (GPU más rápido)

---

### 5. RAG Enhanced Service (Puerto 8005)

#### Health Check

```bash
curl http://localhost:8005/health
```

**Nota:** Requiere API keys de OpenAI o Anthropic configuradas.

#### Test: RAG Query (con OpenAI)

```bash
curl -X POST http://localhost:8005/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué es la inteligencia artificial?",
    "documents": [
      {"id": "doc1", "text": "La inteligencia artificial es una rama de la informática que busca crear sistemas capaces de realizar tareas que requieren inteligencia humana."},
      {"id": "doc2", "text": "El machine learning es un subcampo de la IA que permite a las máquinas aprender de datos."},
      {"id": "doc3", "text": "La paella es un plato tradicional de Valencia."}
    ],
    "top_k": 2,
    "llm_provider": "openai",
    "model": "gpt-3.5-turbo"
  }'
```

**Validar:**
- ✅ `answer` contiene respuesta coherente
- ✅ `sources` incluye doc1 y doc2 (no doc3)
- ✅ `num_sources` = 2
- ✅ Respuesta cita las fuentes

#### Test: Simple RAG

```bash
curl -X POST "http://localhost:8005/api/v1/rag/simple?query=¿Qué%20es%20IA?&context=La%20IA%20es%20inteligencia%20artificial&llm_provider=openai"
```

---

## 🔗 Testing Integrado

### Flujo Completo: GPU → Quantum → RAG

```bash
# 1. Generar embeddings con GPU
EMBEDDINGS=$(curl -s -X POST http://localhost:8001/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"texts": ["documento 1", "documento 2"]}')

echo $EMBEDDINGS

# 2. Deduplicar con Quantum D-Wave
DEDUPE=$(curl -s -X POST http://localhost:8002/api/v1/dedupe/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"id": "doc1", "text": "documento similar 1"},
      {"id": "doc2", "text": "documento similar 2"}
    ],
    "similarity_threshold": 0.7
  }')

echo $DEDUPE

# 3. RAG con documentos únicos
curl -X POST http://localhost:8005/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿De qué tratan los documentos?",
    "documents": [{"id": "doc1", "text": "documento similar 1"}],
    "top_k": 1,
    "llm_provider": "openai",
    "model": "gpt-3.5-turbo"
  }'
```

---

## 📊 Benchmarks

### GPU Embedding Performance

```bash
# Test con diferentes tamaños de batch
for batch in 1 10 100; do
  echo "Testing batch size: $batch"
  time curl -s -X POST http://localhost:8001/api/v1/embeddings/batch \
    -H "Content-Type: application/json" \
    -d "{\"texts\": $(python -c "print(['doc']*$batch)"), \"batch_size\": $batch}" > /dev/null
done
```

### Quantum Services Comparison

```bash
# D-Wave
echo "D-Wave Simulated Annealing:"
time curl -s -X POST http://localhost:8002/api/v1/dedupe/analyze \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"id":"d1","text":"doc1"},{"id":"d2","text":"doc2"}], "similarity_threshold": 0.7}' > /dev/null

# IBM Qiskit
echo "IBM Qiskit QAOA:"
time curl -s -X POST http://localhost:8003/api/v1/optimize/qaoa \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"id":"d1","text":"doc1","similarity_score":0.9}], "max_iterations": 50}' > /dev/null

# NVIDIA cuQuantum
echo "NVIDIA cuQuantum:"
time curl -s -X POST http://localhost:8004/api/v1/simulate/circuit \
  -H "Content-Type: application/json" \
  -d '{"num_qubits": 10, "depth": 5, "shots": 1024}' > /dev/null
```

---

## 📈 Monitoreo

### Prometheus Queries

```bash
# Acceder a Prometheus
open http://localhost:9090

# Queries útiles:
# - rate(embeddings_generated_total[5m])
# - histogram_quantile(0.95, rate(embedding_duration_seconds_bucket[5m]))
# - gpu_memory_used_bytes
# - dedupe_requests_total
# - rag_requests_total
```

### Grafana Dashboards

```bash
# Acceder a Grafana
open http://localhost:3001
# Login: admin / admin

# Crear dashboard con:
# - GPU Embedding throughput
# - Quantum services latency
# - RAG query duration
# - Error rates
```

---

## 🐛 Troubleshooting

### Servicio no inicia

```bash
# Ver logs
docker-compose -f docker-compose.quantum-gpu.yml logs [service-name]

# Reiniciar servicio
docker-compose -f docker-compose.quantum-gpu.yml restart [service-name]

# Reconstruir imagen
docker-compose -f docker-compose.quantum-gpu.yml build [service-name]
docker-compose -f docker-compose.quantum-gpu.yml up -d [service-name]
```

### GPU no detectada

```bash
# Verificar NVIDIA driver
nvidia-smi

# Verificar Docker GPU support
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Reinstalar NVIDIA Container Toolkit si es necesario
```

### Puerto ocupado

```bash
# Ver qué está usando el puerto
netstat -ano | findstr :8001

# Cambiar puerto en docker-compose.quantum-gpu.yml
# ports:
#   - "8011:8001"  # Usar 8011 en lugar de 8001
```

### RAG Service: API Key no configurada

```bash
# Editar .env
cd services/rag-enhanced
cp .env.example .env
# Editar .env y añadir:
# OPENAI_API_KEY=tu_key_aqui

# Reiniciar servicio
docker-compose -f ../../docker-compose.quantum-gpu.yml restart rag-enhanced-service
```

### Out of Memory (GPU)

```bash
# Reducir batch size
# Usar modelo más pequeño
# Liberar memoria GPU:
docker-compose -f docker-compose.quantum-gpu.yml restart gpu-embedding-service
```

---

## ✅ Checklist de Testing

### Testing Básico

- [ ] Todos los servicios levantan correctamente
- [ ] Health checks responden 200 OK
- [ ] Documentación Swagger accesible (/docs)
- [ ] Métricas Prometheus accesibles (/metrics)

### Testing Funcional

- [ ] GPU Embedding: Genera embeddings correctamente
- [ ] Quantum D-Wave: Deduplica documentos
- [ ] Quantum IBM: Optimiza con QAOA
- [ ] Quantum NVIDIA: Simula circuitos
- [ ] RAG Enhanced: Genera respuestas con fuentes

### Testing de Performance

- [ ] GPU Embedding: > 100 embeddings/segundo
- [ ] Quantum services: < 10 segundos por operación
- [ ] RAG: < 5 segundos por query
- [ ] Sin memory leaks después de 100 requests

### Testing de Integración

- [ ] GPU → Quantum pipeline funciona
- [ ] Quantum → RAG pipeline funciona
- [ ] Prometheus recolecta métricas
- [ ] Grafana muestra dashboards

---

## 📝 Reportar Resultados

### Template de Reporte

```markdown
## Test Results - [Fecha]

### Servicios Probados
- [x] GPU Embedding Service
- [x] Quantum D-Wave Service
- [x] Quantum IBM Service
- [x] Quantum NVIDIA Service
- [x] RAG Enhanced Service

### Performance
- GPU Embedding: XXX embeddings/s
- Quantum D-Wave: XX segundos
- Quantum IBM: XX segundos
- Quantum NVIDIA: XX segundos
- RAG: XX segundos

### Issues Encontrados
- [Ninguno / Listar issues]

### Conclusiones
- [Resumen de resultados]
```

---

**© 2025 TeFinancia S.A. - FinancIA 2030 Team**
