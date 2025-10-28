# 🐳 Guía Completa de Construcción Docker

## 📋 Servicios v2.0 - Arquitectura Completa

### Stack Completo (7 servicios + 2 infraestructura)

| Servicio | Puerto | Descripción | GPU | Estado |
|----------|--------|-------------|-----|--------|
| **GPU Embedding** | 8001 | Embeddings acelerados por GPU | ✅ | ✅ Listo |
| **Quantum D-Wave** | 8002 | QUBO + Simulated Annealing | ❌ | ✅ Listo |
| **Quantum IBM** | 8003 | QAOA + Qiskit | ❌ | ✅ Listo |
| **Quantum NVIDIA** | 8004 | Simulación cuántica GPU | ✅ | ✅ Listo |
| **RAG Enhanced** | 8005 | RAG con LLMs | ❌ | ✅ Listo |
| **Astra VectorDB** | 8006 | Vector search + HNSW | ❌ | ✅ Listo |
| **Redis** | 6379 | Cache | ❌ | ✅ Listo |
| **Prometheus** | 9090 | Monitoring | ❌ | ✅ Listo |
| **Grafana** | 3001 | Dashboards | ❌ | ✅ Listo |

---

## 🔧 Prerequisitos

### 1. Docker & Docker Compose

```bash
# Verificar Docker
docker --version  # >= 24.0

# Verificar Docker Compose
docker-compose --version  # >= 2.20
```

### 2. NVIDIA GPU (Opcional pero Recomendado)

```bash
# Verificar GPU
nvidia-smi

# Verificar Docker con GPU
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Si falla, instalar NVIDIA Container Toolkit:
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

### 3. Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Copiar ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

**Contenido mínimo del `.env`:**

```env
# DataStax Astra DB (REQUERIDO para servicio Astra DB)
ASTRA_DB_TOKEN=AstraCS:xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ASTRA_DB_API_ENDPOINT=https://xxxxx-xxxx-xxxx.apps.astra.datastax.com
ASTRA_DB_KEYSPACE=financia_vectors
ASTRA_DB_COLLECTION=documents

# OpenAI (REQUERIDO para RAG y Astra DB)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Cohere (Opcional)
COHERE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# D-Wave (Opcional - usa simulador si no está configurado)
DWAVE_API_TOKEN=

# IBM Qiskit (Opcional - usa simulador si no está configurado)
QISKIT_IBM_TOKEN=

# Grafana
GRAFANA_PASSWORD=admin
```

---

## 🚀 Construcción y Despliegue

### Opción 1: Construir y Levantar TODO

```bash
# Ir al directorio del proyecto
cd "Sistema-Corporativo-Documental-con-Capacidades-de-IA"

# Construir todas las imágenes
docker-compose -f docker-compose.quantum-gpu.yml build

# Levantar todos los servicios
docker-compose -f docker-compose.quantum-gpu.yml up -d

# Ver logs
docker-compose -f docker-compose.quantum-gpu.yml logs -f

# Ver estado
docker-compose -f docker-compose.quantum-gpu.yml ps
```

**Tiempo estimado:** 10-15 minutos (primera vez)

### Opción 2: Construir Servicios Individuales

```bash
# Solo GPU Embedding
docker-compose -f docker-compose.quantum-gpu.yml build gpu-embedding-service
docker-compose -f docker-compose.quantum-gpu.yml up -d gpu-embedding-service

# Solo Astra DB + Redis
docker-compose -f docker-compose.quantum-gpu.yml build astra-vector-db-service
docker-compose -f docker-compose.quantum-gpu.yml up -d redis astra-vector-db-service

# Solo Quantum services
docker-compose -f docker-compose.quantum-gpu.yml build quantum-dwave-service quantum-ibm-service
docker-compose -f docker-compose.quantum-gpu.yml up -d quantum-dwave-service quantum-ibm-service
```

### Opción 3: Stack Mínimo (Sin GPU)

```bash
# Servicios que NO requieren GPU
docker-compose -f docker-compose.quantum-gpu.yml up -d \
  quantum-dwave-service \
  quantum-ibm-service \
  rag-enhanced-service \
  astra-vector-db-service \
  redis \
  prometheus \
  grafana
```

---

## 📊 Verificación de Servicios

### Health Checks

```bash
# GPU Embedding
curl http://localhost:8001/health

# Quantum D-Wave
curl http://localhost:8002/health

# Quantum IBM
curl http://localhost:8003/health

# Quantum NVIDIA
curl http://localhost:8004/health

# RAG Enhanced
curl http://localhost:8005/health

# Astra VectorDB
curl http://localhost:8006/health

# Redis
docker exec financia_redis redis-cli ping

# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3001/api/health
```

### Script de Verificación Automática

```bash
# Crear script
cat > check_services.sh << 'EOF'
#!/bin/bash

services=(
  "GPU Embedding:8001"
  "Quantum D-Wave:8002"
  "Quantum IBM:8003"
  "Quantum NVIDIA:8004"
  "RAG Enhanced:8005"
  "Astra VectorDB:8006"
)

echo "🔍 Verificando servicios..."
for service in "${services[@]}"; do
  name="${service%%:*}"
  port="${service##*:}"
  
  if curl -s -f "http://localhost:$port/health" > /dev/null; then
    echo "✅ $name (Puerto $port): OK"
  else
    echo "❌ $name (Puerto $port): FAIL"
  fi
done

echo ""
echo "📊 Servicios de infraestructura:"
if docker exec financia_redis redis-cli ping > /dev/null 2>&1; then
  echo "✅ Redis: OK"
else
  echo "❌ Redis: FAIL"
fi

if curl -s -f "http://localhost:9090/-/healthy" > /dev/null; then
  echo "✅ Prometheus: OK"
else
  echo "❌ Prometheus: FAIL"
fi

if curl -s -f "http://localhost:3001/api/health" > /dev/null; then
  echo "✅ Grafana: OK"
else
  echo "❌ Grafana: FAIL"
fi
EOF

chmod +x check_services.sh
./check_services.sh
```

---

## 🐛 Troubleshooting

### Problema 1: Error de Build

```bash
# Limpiar cache de Docker
docker system prune -a

# Reconstruir sin cache
docker-compose -f docker-compose.quantum-gpu.yml build --no-cache

# Ver logs de build
docker-compose -f docker-compose.quantum-gpu.yml build --progress=plain
```

### Problema 2: GPU No Detectada

```bash
# Verificar NVIDIA driver
nvidia-smi

# Verificar NVIDIA Container Toolkit
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Reinstalar toolkit si es necesario
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Problema 3: Puerto Ocupado

```bash
# Ver qué está usando el puerto
netstat -ano | findstr :8001  # Windows
lsof -i :8001                 # Linux/Mac

# Cambiar puerto en docker-compose.quantum-gpu.yml
# ports:
#   - "8011:8001"  # Usar 8011 externamente
```

### Problema 4: Out of Memory

```bash
# Limitar memoria de servicios
# En docker-compose.quantum-gpu.yml, añadir:
# deploy:
#   resources:
#     limits:
#       memory: 4G

# Liberar memoria
docker system prune -a
```

### Problema 5: Servicio No Inicia

```bash
# Ver logs detallados
docker logs financia_astra_vectordb --tail 100 -f

# Entrar al contenedor
docker exec -it financia_astra_vectordb /bin/bash

# Verificar variables de entorno
docker exec financia_astra_vectordb env | grep ASTRA

# Reiniciar servicio
docker-compose -f docker-compose.quantum-gpu.yml restart astra-vector-db-service
```

---

## 🔄 Actualización de Servicios

### Actualizar un Servicio

```bash
# 1. Parar servicio
docker-compose -f docker-compose.quantum-gpu.yml stop astra-vector-db-service

# 2. Reconstruir
docker-compose -f docker-compose.quantum-gpu.yml build astra-vector-db-service

# 3. Levantar
docker-compose -f docker-compose.quantum-gpu.yml up -d astra-vector-db-service

# 4. Verificar
docker logs financia_astra_vectordb -f
```

### Actualizar Todo

```bash
# Pull cambios de Git
git pull origin main

# Reconstruir todo
docker-compose -f docker-compose.quantum-gpu.yml build

# Reiniciar con nuevas imágenes
docker-compose -f docker-compose.quantum-gpu.yml up -d
```

---

## 🧹 Limpieza

### Parar Servicios

```bash
# Parar todos
docker-compose -f docker-compose.quantum-gpu.yml stop

# Parar y eliminar contenedores
docker-compose -f docker-compose.quantum-gpu.yml down

# Parar, eliminar contenedores y volúmenes
docker-compose -f docker-compose.quantum-gpu.yml down -v
```

### Limpieza Completa

```bash
# Parar todo
docker-compose -f docker-compose.quantum-gpu.yml down -v

# Eliminar imágenes
docker rmi $(docker images 'financia*' -q)

# Limpiar sistema
docker system prune -a --volumes

# ADVERTENCIA: Esto elimina TODO (imágenes, contenedores, volúmenes)
```

---

## 📈 Monitoreo

### Prometheus

```bash
# Acceder a Prometheus UI
open http://localhost:9090

# Queries útiles:
# - rate(ingest_requests_total[5m])
# - histogram_quantile(0.95, search_duration_seconds_bucket)
# - documents_total
# - cache_hits_total / (cache_hits_total + cache_misses_total)
```

### Grafana

```bash
# Acceder a Grafana
open http://localhost:3001

# Login: admin / admin (o tu GRAFANA_PASSWORD)

# Datasource ya configurado: Prometheus
# Crear dashboards para:
# - GPU Embedding throughput
# - Astra DB search latency
# - Cache hit rate
# - Service health
```

### Logs Centralizados

```bash
# Ver logs de todos los servicios
docker-compose -f docker-compose.quantum-gpu.yml logs -f

# Ver logs de un servicio específico
docker logs financia_astra_vectordb -f --tail 100

# Buscar errores
docker-compose -f docker-compose.quantum-gpu.yml logs | grep ERROR

# Exportar logs
docker logs financia_astra_vectordb > astra_logs.txt 2>&1
```

---

## 🎯 Comandos Útiles

### Información de Contenedores

```bash
# Ver todos los contenedores
docker ps -a

# Ver solo servicios v2.0
docker ps --filter "label=com.financia.version=2.0"

# Ver uso de recursos
docker stats

# Inspeccionar contenedor
docker inspect financia_astra_vectordb

# Ver redes
docker network ls
docker network inspect financia-network
```

### Backup y Restore

```bash
# Backup de volúmenes
docker run --rm -v financia_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz /data

# Restore
docker run --rm -v financia_redis_data:/data -v $(pwd):/backup alpine tar xzf /backup/redis_backup.tar.gz -C /
```

---

## ✅ Checklist de Despliegue

### Pre-Despliegue

- [ ] Docker y Docker Compose instalados
- [ ] NVIDIA GPU configurada (opcional)
- [ ] Archivo `.env` configurado
- [ ] Credenciales de Astra DB obtenidas
- [ ] API keys configuradas (OpenAI, Cohere)

### Construcción

- [ ] Todas las imágenes construidas sin errores
- [ ] Servicios levantados correctamente
- [ ] Health checks respondiendo OK
- [ ] Logs sin errores críticos

### Verificación

- [ ] Endpoints accesibles
- [ ] Prometheus recolectando métricas
- [ ] Grafana mostrando datos
- [ ] Redis funcionando
- [ ] Astra DB conectado

### Post-Despliegue

- [ ] Documentación revisada
- [ ] Tests básicos ejecutados
- [ ] Monitoreo configurado
- [ ] Backups programados (si aplica)

---

## 📚 Recursos Adicionales

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Guía de testing completa
- **[DOCKER_LOCAL_INTEGRATION.md](DOCKER_LOCAL_INTEGRATION.md)** - Integración con app actual
- **[PHOENIX_V2_INTEGRATION.md](PHOENIX_V2_INTEGRATION.md)** - Arize Phoenix
- **[services/README.md](../services/README.md)** - Documentación de servicios

---

**© 2025 FinancIA 2030 Team**
