# 🚀 Guía de Implementación v2.0 - Quantum & GPU Enhancement

**Fecha:** Octubre 2025  
**Estado:** ✅ Fase 1 Iniciada - GPU Embedding Service

---

## ✅ Estado Actual de Implementación

### Completado

- ✅ Estructura de carpetas creada (`services/`)
- ✅ **GPU Embedding Service** implementado y listo
  - `main.py` - Servicio FastAPI completo
  - `requirements.txt` - Dependencias
  - `Dockerfile` - Contenedor con soporte CUDA
  - `README.md` - Documentación completa
  - `.env.example` - Configuración de ejemplo
- ✅ `docker-compose.quantum-gpu.yml` - Orquestación de nuevos servicios
- ✅ Prometheus + Grafana configurados para monitoreo

### En Progreso

- 🚧 Quantum services (pendientes de implementación)
- 🚧 RAG Enhanced service (pendiente)
- 🚧 Configuración de Prometheus
- 🚧 Dashboards de Grafana

---

## 🎯 Cómo Usar el GPU Embedding Service

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Levantar SOLO el servicio GPU (sin afectar app actual)
docker-compose -f docker-compose.quantum-gpu.yml up gpu-embedding-service -d

# 2. Verificar que está corriendo
curl http://localhost:8001/health

# 3. Ver logs
docker logs financia_gpu_embedding -f

# 4. Probar generación de embeddings
curl -X POST http://localhost:8001/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hola mundo", "Hello world"]}'
```

### Opción 2: Levantar TODO (GPU + Monitoring)

```bash
# Levantar GPU service + Prometheus + Grafana
docker-compose -f docker-compose.quantum-gpu.yml up -d

# Acceder a servicios:
# - GPU Service: http://localhost:8001
# - GPU Docs: http://localhost:8001/docs
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001 (admin/admin)
```

### Opción 3: Desarrollo Local

```bash
cd services/gpu-embedding

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py

# Servicio disponible en http://localhost:8001
```

---

## 🔗 Integración con App Actual

### Estrategia: Feature Flag (Recomendado)

El servicio GPU es **completamente independiente**. Para integrarlo:

#### 1. Añadir Variable de Entorno

En `backend/.env`:
```env
# Feature Flag para GPU Embeddings
USE_GPU_EMBEDDINGS=false  # Cambiar a true para activar
GPU_EMBEDDING_URL=http://localhost:8001
```

#### 2. Modificar Servicio de Embeddings (Opcional)

En `backend/services/embedding_service.py` (o similar):

```python
import os
import httpx

USE_GPU = os.getenv("USE_GPU_EMBEDDINGS", "false").lower() == "true"
GPU_URL = os.getenv("GPU_EMBEDDING_URL", "http://localhost:8001")

async def generate_embeddings(texts: List[str]):
    if USE_GPU:
        # Usar servicio GPU
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GPU_URL}/api/v1/embeddings/generate",
                json={"texts": texts}
            )
            return response.json()["embeddings"]
    else:
        # Usar método actual (fallback)
        return current_embedding_method(texts)
```

#### 3. Testing

```bash
# Test con GPU desactivado (usa método actual)
USE_GPU_EMBEDDINGS=false python test_embeddings.py

# Test con GPU activado
USE_GPU_EMBEDDINGS=true python test_embeddings.py
```

---

## 📊 Monitoreo y Métricas

### Prometheus

Accede a métricas en:
- GPU Service: http://localhost:8001/metrics
- Prometheus UI: http://localhost:9090

Métricas disponibles:
```
embeddings_generated_total
embedding_duration_seconds
gpu_memory_used_bytes
active_requests
```

### Grafana

1. Accede a http://localhost:3001
2. Login: `admin` / `admin`
3. Importar dashboard (próximamente)

---

## 🧪 Testing y Validación

### Test Básico

```bash
# Health check
curl http://localhost:8001/health

# Respuesta esperada:
{
  "status": "healthy",
  "gpu_available": true,
  "device": "cuda",
  "model_loaded": true,
  "faiss_index_size": 0
}
```

### Test de Embeddings

```bash
curl -X POST http://localhost:8001/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["documento de prueba", "test document"],
    "normalize": true
  }'
```

### Test de Búsqueda

```bash
# 1. Añadir documentos al índice
curl -X POST http://localhost:8001/api/v1/index/add \
  -H "Content-Type: application/json" \
  -d '["documento 1", "documento 2", "documento 3"]'

# 2. Buscar similares
curl -X POST http://localhost:8001/api/v1/similarity/search \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "documento",
    "top_k": 5
  }'
```

---

## 📈 Benchmarks Esperados

### Con GPU (NVIDIA RTX 4070)

| Operación | Tiempo | Throughput |
|-----------|--------|------------|
| 1 embedding | <10ms | ~100 docs/s |
| Batch 10 | ~15ms | ~666 docs/s |
| Batch 100 | ~100ms | ~1000 docs/s |
| Batch 1000 | ~1s | ~1000 docs/s |

### Sin GPU (CPU Fallback)

| Operación | Tiempo | Throughput |
|-----------|--------|------------|
| 1 embedding | ~200ms | ~5 docs/s |
| Batch 10 | ~500ms | ~20 docs/s |
| Batch 100 | ~2s | ~50 docs/s |

**Mejora esperada: 10-20x más rápido con GPU**

---

## 🔧 Troubleshooting

### GPU No Detectada

```bash
# Verificar NVIDIA driver
nvidia-smi

# Verificar Docker con GPU
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Verificar NVIDIA Container Toolkit
docker run --rm --gpus all ubuntu nvidia-smi
```

### Servicio No Inicia

```bash
# Ver logs
docker logs financia_gpu_embedding

# Verificar puerto
netstat -an | findstr 8001

# Reiniciar servicio
docker-compose -f docker-compose.quantum-gpu.yml restart gpu-embedding-service
```

### Out of Memory

```bash
# Reducir batch size en requests
# Usar modelo más pequeño
# Editar .env:
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Reiniciar
docker-compose -f docker-compose.quantum-gpu.yml restart gpu-embedding-service
```

---

## 🚀 Próximos Pasos

### Semana 1-2: Validación GPU Service

- [ ] Levantar servicio GPU
- [ ] Ejecutar benchmarks
- [ ] Comparar con método actual
- [ ] Documentar resultados
- [ ] Decidir si integrar en app principal

### Semana 3-4: Quantum Services (Fase 2)

- [ ] Implementar `quantum-dwave-service`
- [ ] Implementar `quantum-ibm-service`
- [ ] Testing de deduplicación
- [ ] Benchmarks vs método clásico

### Semana 5-6: RAG Enhanced (Fase 5)

- [ ] Implementar `rag-enhanced-service`
- [ ] Integrar con GPU embeddings
- [ ] Testing de calidad de respuestas
- [ ] Comparar con RAG actual

---

## 📝 Notas Importantes

### ✅ Garantías

- **NO rompe nada**: Servicios completamente independientes
- **Opcional**: Se puede activar/desactivar con feature flags
- **Fallback**: Si falla, usa método actual automáticamente
- **Monitoreado**: Métricas completas en Prometheus

### ⚠️ Requisitos

- **GPU**: NVIDIA con CUDA 12.1+ (opcional, funciona en CPU)
- **RAM**: 8GB mínimo (16GB recomendado)
- **Disco**: 10GB para modelos
- **Docker**: 24.0+ con NVIDIA Container Toolkit

### 🔐 Seguridad

- Todos los servicios en red privada Docker
- Sin exposición externa por defecto
- API keys en variables de entorno
- Logs sin información sensible

---

## 📚 Documentación Adicional

- [Plan Completo](QUANTUM_GPU_ENHANCEMENT_PLAN.md)
- [GPU Service README](../services/gpu-embedding/README.md)
- [Docker Compose](../docker-compose.quantum-gpu.yml)

---

## 🤝 Soporte

**Equipo:** FinancIA 2030 Team  
**Email:** financia2030@tefinancia.es  
**Docs:** [docs/](.)

---

**© 2025 TeFinancia S.A. - Confidencial**
