# 🚀 Quick Start - Integración GPU Service

## ✅ Archivos Creados

1. **`services/gpu_embedding_client.py`** - Cliente para GPU service
2. **`services/embedding_service_v2.py`** - Wrapper con fallback automático
3. **`.env.gpu`** - Variables de entorno

---

## 📝 Paso a Paso

### 1. Configurar Variables de Entorno

```bash
# Copiar configuración
cp .env.gpu .env

# O añadir a tu .env existente:
echo "" >> .env
cat .env.gpu >> .env

# Editar .env y cambiar:
USE_GPU_EMBEDDINGS=true  # Activar GPU
```

### 2. Modificar Tu Código Actual

#### Opción A: Reemplazar Servicio Actual (Recomendado)

```python
# En tu backend/main.py o donde inicialices servicios

# ANTES:
from services.embedding_service import EmbeddingService
embedding_service = EmbeddingService()

# DESPUÉS:
from services.embedding_service import EmbeddingService
from services.embedding_service_v2 import EmbeddingServiceV2

# Tu servicio actual (como fallback)
current_service = EmbeddingService()

# Nuevo servicio con GPU + fallback
embedding_service = EmbeddingServiceV2(fallback_service=current_service)

# Usar igual que antes - ¡no cambias nada más!
embeddings = await embedding_service.generate_embeddings(texts)
```

#### Opción B: Testing A/B

```python
# En tu endpoint de embeddings
from services.gpu_embedding_client import get_gpu_client

@app.post("/api/embeddings")
async def generate_embeddings(texts: List[str], use_gpu: bool = False):
    if use_gpu:
        gpu_client = get_gpu_client()
        embeddings = await gpu_client.generate_embeddings(texts)
        if embeddings:
            return {"embeddings": embeddings, "method": "gpu"}
    
    # Fallback
    embeddings = await current_service.generate_embeddings(texts)
    return {"embeddings": embeddings, "method": "cpu"}
```

### 3. Reiniciar Backend

```bash
# Parar backend
docker-compose restart backend

# O si usas docker-compose-local.yml
docker-compose -f docker-compose-local.yml restart backend

# Ver logs
docker logs financia_backend -f
```

### 4. Probar Integración

```bash
# Test 1: Verificar que GPU service está disponible
curl http://localhost:8001/health

# Test 2: Llamar a tu backend (debería usar GPU si está activado)
curl -X POST http://localhost:8000/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test desde backend"]}'

# Test 3: Ver estadísticas (añadir endpoint)
curl http://localhost:8000/api/embeddings/stats
```

---

## 📊 Añadir Endpoint de Estadísticas

```python
# En tu backend/api/endpoints.py o similar

from services.embedding_service_v2 import embedding_service

@app.get("/api/embeddings/stats")
async def get_embedding_stats():
    """Ver estadísticas de uso GPU vs CPU"""
    return embedding_service.get_stats()

# Respuesta:
# {
#   "gpu_calls": 150,
#   "fallback_calls": 10,
#   "gpu_errors": 2,
#   "total_calls": 160,
#   "gpu_percentage": 93.75,
#   "gpu_enabled": true
# }
```

---

## 🧪 Testing

### Test Manual

```python
# backend/test_gpu_integration.py
import asyncio
from services.embedding_service_v2 import EmbeddingServiceV2
from services.embedding_service import EmbeddingService

async def test_gpu():
    # Setup
    current = EmbeddingService()
    service = EmbeddingServiceV2(fallback_service=current)
    
    # Test
    texts = ["Hola mundo", "Hello world", "Bonjour monde"]
    embeddings = await service.generate_embeddings(texts)
    
    print(f"✅ Generated {len(embeddings)} embeddings")
    print(f"📊 Stats: {service.get_stats()}")

if __name__ == "__main__":
    asyncio.run(test_gpu())
```

```bash
# Ejecutar test
python backend/test_gpu_integration.py
```

### Test con pytest

```python
# backend/tests/test_gpu_service.py
import pytest
from services.embedding_service_v2 import EmbeddingServiceV2

@pytest.mark.asyncio
async def test_gpu_embeddings(mock_fallback_service):
    service = EmbeddingServiceV2(fallback_service=mock_fallback_service)
    
    texts = ["test1", "test2"]
    embeddings = await service.generate_embeddings(texts)
    
    assert len(embeddings) == 2
    assert all(isinstance(emb, list) for emb in embeddings)

@pytest.mark.asyncio
async def test_fallback_on_gpu_error(mock_fallback_service):
    # GPU service no disponible
    service = EmbeddingServiceV2(fallback_service=mock_fallback_service)
    service.gpu_client.enabled = False
    
    embeddings = await service.generate_embeddings(["test"])
    
    # Debe usar fallback
    assert service.stats["fallback_calls"] == 1
    assert service.stats["gpu_calls"] == 0
```

---

## 🔧 Troubleshooting

### GPU Service No Responde

```bash
# Verificar que está corriendo
docker ps | grep gpu-embedding

# Ver logs
docker logs financia_gpu_embedding -f

# Reiniciar
docker-compose -f docker-compose.quantum-gpu.yml restart gpu-embedding-service
```

### Backend No Puede Conectar

```bash
# Verificar red Docker
docker network inspect financia-network

# Verificar que ambos están en la misma red
docker inspect financia_backend | grep NetworkMode
docker inspect financia_gpu_embedding | grep NetworkMode

# Si están en redes diferentes, conectar:
docker network connect financia-network financia_gpu_embedding
```

### Performance No Mejora

```bash
# Verificar que GPU está siendo usada
curl http://localhost:8000/api/embeddings/stats

# Si gpu_percentage es 0%, verificar:
# 1. USE_GPU_EMBEDDINGS=true en .env
# 2. Backend reiniciado después de cambiar .env
# 3. GPU service está corriendo
```

---

## 📈 Métricas Esperadas

### Con GPU (NVIDIA RTX 4070)
- **Throughput**: 500-1000 embeddings/segundo
- **Latencia**: <10ms por documento
- **Batch 100**: ~100ms total

### Sin GPU (CPU Fallback)
- **Throughput**: 20-50 embeddings/segundo
- **Latencia**: ~200ms por documento
- **Batch 100**: ~2000ms total

**Mejora esperada: 10-20x más rápido** 🚀

---

## ✅ Checklist

- [ ] GPU service está corriendo (`docker ps`)
- [ ] Variables de entorno configuradas (`.env`)
- [ ] Código integrado (`embedding_service_v2.py`)
- [ ] Backend reiniciado
- [ ] Test manual funciona
- [ ] Estadísticas muestran uso GPU
- [ ] Performance mejorada

---

## 🎯 Próximos Pasos

1. **Monitorear** uso GPU vs CPU durante 1 semana
2. **Medir** mejora de performance
3. **Ajustar** configuración según métricas
4. **Integrar** más servicios (Quantum, RAG)

---

**© 2025 FinancIA 2030 Team**
