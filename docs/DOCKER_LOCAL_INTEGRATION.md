# 🐳 Guía de Integración con Docker Local

**Objetivo:** Integrar los nuevos servicios v2.0 (Quantum + GPU) con tu entorno Docker local existente **sin romper nada**.

---

## 📋 Situación Actual

### Entorno Existente (v1.0)

Tu Docker local actual tiene:
- ✅ Backend (FastAPI) - Puerto 8000
- ✅ Frontend (React) - Puerto 3000
- ✅ PostgreSQL - Puerto 5432
- ✅ OpenSearch - Puerto 9200
- ✅ Qdrant - Puerto 6333
- ✅ Redis - Puerto 6379
- ✅ MinIO - Puerto 9000/9001
- ✅ Celery Workers
- ✅ Arize Phoenix - Puerto 6006

**Archivo:** `docker-compose.yml`

### Nuevos Servicios (v2.0)

Los nuevos servicios están en:
- ✨ GPU Embedding Service - Puerto 8001
- ✨ Quantum D-Wave Service - Puerto 8002
- ✨ Quantum IBM Service - Puerto 8003
- ✨ Quantum NVIDIA Service - Puerto 8004
- ✨ RAG Enhanced Service - Puerto 8005
- ✨ Prometheus - Puerto 9090
- ✨ Grafana - Puerto 3001

**Archivo:** `docker-compose.quantum-gpu.yml`

---

## 🎯 Estrategia de Integración

### Opción 1: Entornos Separados (RECOMENDADO para empezar)

**Ventajas:**
- ✅ Cero riesgo de romper app actual
- ✅ Puedes probar servicios v2.0 independientemente
- ✅ Fácil rollback
- ✅ Desarrollo y producción separados

**Cómo funciona:**
```bash
# Terminal 1: App actual (v1.0)
docker-compose up -d

# Terminal 2: Servicios nuevos (v2.0)
docker-compose -f docker-compose.quantum-gpu.yml up -d
```

**Resultado:**
- App actual funciona en puertos 3000, 8000, etc.
- Servicios nuevos funcionan en puertos 8001-8005, 9090, 3001
- Ambos pueden comunicarse si es necesario

---

### Opción 2: Integración Gradual (Para producción)

**Ventajas:**
- ✅ Un solo comando para levantar todo
- ✅ Red Docker compartida
- ✅ Más fácil de gestionar
- ✅ Preparado para producción

**Cómo funciona:**
Crear un nuevo `docker-compose.integrated.yml` que incluya ambos.

---

## 🚀 PASO A PASO: Opción 1 (Recomendado)

### Paso 1: Verificar App Actual

```bash
# Ir a tu directorio del proyecto
cd "Sistema-Corporativo-Documental-con-Capacidades-de-IA"

# Verificar que tu app actual funciona
docker-compose ps

# Si no está corriendo, levantarla
docker-compose up -d

# Verificar que funciona
curl http://localhost:8000/health  # Backend
curl http://localhost:3000         # Frontend
```

### Paso 2: Levantar Servicios v2.0

```bash
# En el mismo directorio
# Levantar SOLO los servicios que quieras probar

# Opción A: Solo GPU Embedding (más ligero)
docker-compose -f docker-compose.quantum-gpu.yml up gpu-embedding-service -d

# Opción B: GPU + 1 Quantum service
docker-compose -f docker-compose.quantum-gpu.yml up gpu-embedding-service quantum-dwave-service -d

# Opción C: Todos los servicios v2.0
docker-compose -f docker-compose.quantum-gpu.yml up -d
```

### Paso 3: Verificar que Ambos Funcionan

```bash
# App actual (v1.0)
curl http://localhost:8000/health
curl http://localhost:3000

# Servicios nuevos (v2.0)
curl http://localhost:8001/health  # GPU Embedding
curl http://localhost:8002/health  # Quantum D-Wave
curl http://localhost:8003/health  # Quantum IBM

# Ver todos los contenedores
docker ps
```

### Paso 4: Probar Comunicación Entre Servicios

```bash
# Desde tu backend actual, puedes llamar a los nuevos servicios
# Ejemplo: Generar embeddings con GPU service

curl -X POST http://localhost:8001/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test desde app actual"]}'
```

---

## 🔗 PASO A PASO: Opción 2 (Integración Completa)

### Paso 1: Crear Docker Compose Integrado

Voy a crear un archivo que combine ambos:

```yaml
# docker-compose.integrated.yml
version: '3.8'

services:
  # ========================================
  # SERVICIOS EXISTENTES v1.0
  # ========================================
  backend:
    # ... tu configuración actual del backend
    environment:
      # Añadir URLs de servicios v2.0
      - GPU_EMBEDDING_URL=http://gpu-embedding-service:8001
      - QUANTUM_DEDUPE_URL=http://quantum-dwave-service:8002
      - USE_GPU_EMBEDDINGS=false  # Feature flag
      - USE_QUANTUM_DEDUPE=false  # Feature flag

  frontend:
    # ... tu configuración actual del frontend

  postgres:
    # ... tu configuración actual

  # ... resto de servicios v1.0

  # ========================================
  # NUEVOS SERVICIOS v2.0
  # ========================================
  gpu-embedding-service:
    build: ./services/gpu-embedding
    ports:
      - "8001:8001"
    networks:
      - financia-network
    # ... resto de configuración

  quantum-dwave-service:
    build: ./services/quantum-dwave
    ports:
      - "8002:8002"
    networks:
      - financia-network

  # ... resto de servicios v2.0

networks:
  financia-network:
    driver: bridge
```

### Paso 2: Migrar Gradualmente

```bash
# 1. Parar app actual
docker-compose down

# 2. Levantar con compose integrado
docker-compose -f docker-compose.integrated.yml up -d

# 3. Verificar todo funciona
docker-compose -f docker-compose.integrated.yml ps
```

---

## 🧪 Testing de Integración

### Test 1: App Actual + GPU Embeddings

```python
# En tu backend actual (backend/services/embedding_service.py)
import os
import httpx

USE_GPU = os.getenv("USE_GPU_EMBEDDINGS", "false").lower() == "true"
GPU_URL = os.getenv("GPU_EMBEDDING_URL", "http://localhost:8001")

async def generate_embeddings(texts: list[str]):
    if USE_GPU:
        # Usar servicio GPU v2.0
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GPU_URL}/api/v1/embeddings/generate",
                json={"texts": texts},
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()["embeddings"]
    
    # Fallback: usar método actual
    return current_embedding_method(texts)
```

### Test 2: Deduplicación con Quantum

```python
# En tu backend actual (backend/services/document_service.py)
import os
import httpx

USE_QUANTUM = os.getenv("USE_QUANTUM_DEDUPE", "false").lower() == "true"
QUANTUM_URL = os.getenv("QUANTUM_DEDUPE_URL", "http://localhost:8002")

async def deduplicate_documents(documents: list):
    if USE_QUANTUM:
        # Usar servicio Quantum v2.0
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{QUANTUM_URL}/api/v1/dedupe/analyze",
                json={
                    "documents": [
                        {"id": doc.id, "text": doc.text}
                        for doc in documents
                    ],
                    "similarity_threshold": 0.7
                },
                timeout=60.0
            )
            if response.status_code == 200:
                return response.json()
    
    # Fallback: usar método actual
    return current_dedupe_method(documents)
```

---

## 📊 Monitoreo Integrado

### Configurar Prometheus para App Actual

Editar `monitoring/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  # Servicios v2.0 (ya configurados)
  - job_name: 'gpu-embedding'
    static_configs:
      - targets: ['gpu-embedding-service:8001']

  # AÑADIR: App actual v1.0
  - job_name: 'backend-v1'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'  # Si tu backend expone métricas

  - job_name: 'celery-workers'
    static_configs:
      - targets: ['celery-worker:9090']  # Si expones métricas
```

### Dashboards en Grafana

Crear dashboard que muestre:
- Métricas app v1.0 (existentes)
- Métricas servicios v2.0 (nuevos)
- Comparación de performance

---

## 🔧 Configuración de Feature Flags

### En Backend (.env)

```bash
# Feature Flags para servicios v2.0
USE_GPU_EMBEDDINGS=false          # true para activar
USE_QUANTUM_DEDUPE=false          # true para activar
USE_QUANTUM_OPTIMIZE=false        # true para activar
USE_RAG_ENHANCED=false            # true para activar

# URLs de servicios v2.0
GPU_EMBEDDING_URL=http://gpu-embedding-service:8001
QUANTUM_DEDUPE_URL=http://quantum-dwave-service:8002
QUANTUM_OPTIMIZE_URL=http://quantum-ibm-service:8003
RAG_ENHANCED_URL=http://rag-enhanced-service:8005

# Timeouts
GPU_EMBEDDING_TIMEOUT=30
QUANTUM_TIMEOUT=60
RAG_TIMEOUT=60
```

### Testing A/B

```python
# backend/core/feature_flags.py
import os
import random

class FeatureFlags:
    @staticmethod
    def use_gpu_embeddings(user_id: str = None) -> bool:
        """Decide si usar GPU embeddings"""
        # Opción 1: Siempre según variable de entorno
        if os.getenv("USE_GPU_EMBEDDINGS") == "true":
            return True
        
        # Opción 2: A/B testing (50% de usuarios)
        if os.getenv("AB_TEST_GPU") == "true":
            return hash(user_id) % 2 == 0
        
        return False
    
    @staticmethod
    def use_quantum_dedupe() -> bool:
        return os.getenv("USE_QUANTUM_DEDUPE", "false") == "true"
```

---

## 🚨 Troubleshooting

### Problema: Conflicto de Puertos

```bash
# Error: Port 3001 already in use

# Solución: Cambiar puerto de Grafana
# En docker-compose.quantum-gpu.yml:
grafana:
  ports:
    - "3002:3000"  # Usar 3002 en lugar de 3001
```

### Problema: Servicios no se Comunican

```bash
# Verificar que están en la misma red
docker network ls
docker network inspect financia-network

# Añadir servicios a la red si es necesario
docker network connect financia-network gpu-embedding-service
```

### Problema: Out of Memory

```bash
# Limitar memoria de servicios v2.0
# En docker-compose.quantum-gpu.yml:
gpu-embedding-service:
  deploy:
    resources:
      limits:
        memory: 4G
      reservations:
        memory: 2G
```

---

## 📈 Roadmap de Integración

### Fase 1: Testing (Semana 1)
- [ ] Levantar servicios v2.0 en paralelo
- [ ] Probar cada servicio independientemente
- [ ] Medir performance y comparar con v1.0
- [ ] Identificar issues

### Fase 2: Integración Soft (Semana 2)
- [ ] Añadir feature flags en backend
- [ ] Implementar llamadas a servicios v2.0 con fallback
- [ ] Testing A/B con 10% de tráfico
- [ ] Monitoreo y métricas

### Fase 3: Integración Completa (Semana 3-4)
- [ ] Aumentar tráfico a servicios v2.0 gradualmente
- [ ] Optimizar configuración según métricas
- [ ] Documentar mejoras de performance
- [ ] Preparar para producción

### Fase 4: Producción (Mes 2)
- [ ] Deploy en entorno de producción
- [ ] Monitoreo 24/7
- [ ] Alertas configuradas
- [ ] Documentación de operaciones

---

## 🎯 Recomendación Final

### Para Empezar HOY:

```bash
# 1. Mantén tu app actual corriendo
docker-compose up -d

# 2. Levanta SOLO GPU Embedding service para probar
docker-compose -f docker-compose.quantum-gpu.yml up gpu-embedding-service -d

# 3. Prueba el servicio
curl http://localhost:8001/health
curl -X POST http://localhost:8001/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test"]}'

# 4. Si funciona bien, añade más servicios gradualmente
docker-compose -f docker-compose.quantum-gpu.yml up quantum-dwave-service -d

# 5. Cuando estés listo, integra con tu backend usando feature flags
```

### Ventajas de este Enfoque:

✅ **Cero riesgo** - App actual sigue funcionando  
✅ **Testing gradual** - Pruebas un servicio a la vez  
✅ **Rollback fácil** - Solo parar servicios v2.0  
✅ **Aprendizaje** - Entiendes cada servicio antes de integrar  
✅ **Producción segura** - Feature flags permiten activar/desactivar  

---

## 📚 Próximos Pasos

1. **Leer:** [TESTING_GUIDE.md](TESTING_GUIDE.md)
2. **Probar:** Levantar servicios v2.0 en paralelo
3. **Medir:** Comparar performance con app actual
4. **Integrar:** Añadir feature flags en backend
5. **Desplegar:** Gradualmente a producción

---

**© 2025 TeFinancia S.A. - FinancIA 2030 Team**
