# 🐳 FinancIA 2030 - Guía de Docker Hub

**Fecha:** 9 de octubre de 2025  
**Usuario Docker Hub:** rjamoriz  
**Namespace:** rjamoriz/financia2030-*

---

## 📋 Índice

1. [Configuración Inicial](#configuración-inicial)
2. [Build y Push de Imágenes](#build-y-push-de-imágenes)
3. [Deployment con Docker Hub](#deployment-con-docker-hub)
4. [Gestión de Imágenes](#gestión-de-imágenes)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Configuración Inicial

### 1. Credenciales de Docker Hub

Ya configuradas en `.docker.env`:

```bash
DOCKER_USERNAME=rjamoriz
DOCKER_TOKEN=dckr_pat_YOUR_TOKEN_HERE
DOCKER_REGISTRY=docker.io
DOCKER_NAMESPACE=rjamoriz
DOCKER_IMAGE_PREFIX=financia2030
DOCKER_TAG=latest
```

**⚠️ IMPORTANTE:** Este archivo está en `.gitignore` y NO se sube a GitHub.

### 2. Login en Docker Hub

```bash
# Login automático
docker login -u rjamoriz -p YOUR_DOCKER_TOKEN_HERE

# O usar el token de forma segura
echo "YOUR_DOCKER_TOKEN_HERE" | docker login -u rjamoriz --password-stdin
```

✅ **Ya estás autenticado en Docker Hub**

---

## 🏗️ Build y Push de Imágenes

### Opción 1: Script Automatizado (RECOMENDADO)

```bash
# Construir y subir todas las imágenes
./docker-build-push.sh
```

Este script:
- ✅ Hace login en Docker Hub
- ✅ Construye 5 imágenes (backend, frontend, 3 workers)
- ✅ Sube todas las imágenes a Docker Hub
- ✅ Muestra URLs de las imágenes

**Tiempo estimado:** 10-15 minutos (primera vez)

### Opción 2: Manual (para imágenes individuales)

```bash
# Backend
docker build -f infrastructure/docker/backend/Dockerfile -t rjamoriz/financia2030-backend:latest backend/
docker push rjamoriz/financia2030-backend:latest

# Frontend
docker build -f infrastructure/docker/frontend/Dockerfile -t rjamoriz/financia2030-frontend:latest frontend/
docker push rjamoriz/financia2030-frontend:latest

# Workers
docker build -f infrastructure/docker/workers/Dockerfile.ingest -t rjamoriz/financia2030-worker-ingest:latest backend/
docker push rjamoriz/financia2030-worker-ingest:latest

docker build -f infrastructure/docker/workers/Dockerfile.process -t rjamoriz/financia2030-worker-process:latest backend/
docker push rjamoriz/financia2030-worker-process:latest

docker build -f infrastructure/docker/workers/Dockerfile.index -t rjamoriz/financia2030-worker-index:latest backend/
docker push rjamoriz/financia2030-worker-index:latest
```

### Imágenes Resultantes

Una vez subidas, tendrás 5 imágenes en Docker Hub:

1. **rjamoriz/financia2030-backend:latest**
   - FastAPI backend con todos los servicios
   - Puerto: 8000
   - Tamaño: ~1.2 GB

2. **rjamoriz/financia2030-frontend:latest**
   - React + Nginx
   - Puerto: 80
   - Tamaño: ~150 MB

3. **rjamoriz/financia2030-worker-ingest:latest**
   - Kafka consumer para ingesta
   - Tamaño: ~800 MB

4. **rjamoriz/financia2030-worker-process:latest**
   - Pipeline de procesamiento (OCR, NER, embeddings)
   - Tamaño: ~2.5 GB (incluye modelos spaCy)

5. **rjamoriz/financia2030-worker-index:latest**
   - Indexación en OpenSearch
   - Tamaño: ~800 MB

**Total:** ~5.5 GB de imágenes

---

## 🚀 Deployment con Docker Hub

### Opción 1: Deployment Completo Automatizado (RECOMENDADO)

```bash
# Deployment completo con un solo comando
./deploy-dockerhub.sh
```

Este script:
1. ✅ Login en Docker Hub
2. ✅ Pregunta si quieres build/push (opcional)
3. ✅ Verifica imágenes en Docker Hub
4. ✅ Detiene contenedores existentes
5. ✅ Descarga últimas imágenes
6. ✅ Inicia todos los servicios (13 contenedores)
7. ✅ Verifica health checks
8. ✅ Muestra información de acceso

**Tiempo:** 2-3 minutos (sin build), 15-20 minutos (con build)

### Opción 2: Docker Compose Manual

```bash
cd infrastructure/docker

# Pull de imágenes
docker-compose -f docker-compose.hub.yml pull

# Iniciar servicios
docker-compose -f docker-compose.hub.yml up -d

# Ver logs
docker-compose -f docker-compose.hub.yml logs -f

# Detener todo
docker-compose -f docker-compose.hub.yml down
```

---

## 📊 Gestión de Imágenes

### Ver Imágenes en Docker Hub

**Web UI:**
```
https://hub.docker.com/u/rjamoriz
```

Ahí verás todas tus imágenes con:
- Tags disponibles
- Tamaño de cada imagen
- Fecha de última actualización
- Número de pulls

### Comandos de Gestión

```bash
# Listar imágenes locales
docker images | grep rjamoriz

# Pull de una imagen específica
docker pull rjamoriz/financia2030-backend:latest

# Eliminar imagen local (no afecta Docker Hub)
docker rmi rjamoriz/financia2030-backend:latest

# Ver información de imagen
docker inspect rjamoriz/financia2030-backend:latest

# Ver capas de imagen
docker history rjamoriz/financia2030-backend:latest
```

### Tagging y Versiones

```bash
# Crear nuevo tag para versión específica
docker tag rjamoriz/financia2030-backend:latest rjamoriz/financia2030-backend:v1.0.0
docker push rjamoriz/financia2030-backend:v1.0.0

# Crear tag para ambiente
docker tag rjamoriz/financia2030-backend:latest rjamoriz/financia2030-backend:production
docker push rjamoriz/financia2030-backend:production
```

### Actualizar Imágenes

```bash
# 1. Hacer cambios en el código

# 2. Rebuild y push
./docker-build-push.sh

# 3. Pull nueva versión en servidor
docker-compose -f docker-compose.hub.yml pull

# 4. Restart con nueva imagen
docker-compose -f docker-compose.hub.yml up -d --force-recreate
```

---

## 🔍 Verificación del Deployment

### 1. Ver Estado de Contenedores

```bash
cd infrastructure/docker
docker-compose -f docker-compose.hub.yml ps
```

**Deberías ver 13 contenedores:**
- ✅ financia-postgres
- ✅ financia-opensearch
- ✅ financia-redis
- ✅ financia-zookeeper
- ✅ financia-kafka
- ✅ financia-minio
- ✅ financia-prometheus
- ✅ financia-grafana
- ✅ financia-mlflow
- ✅ financia-phoenix
- ✅ financia-backend
- ✅ financia-frontend
- ✅ financia-worker-ingest
- ✅ financia-worker-process
- ✅ financia-worker-index

### 2. Verificar Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000/health

# Phoenix
curl http://localhost:6006/healthz

# OpenSearch
curl http://localhost:9200/_cluster/health
```

### 3. Ver Logs

```bash
# Todos los servicios
docker-compose -f docker-compose.hub.yml logs -f

# Servicio específico
docker-compose -f docker-compose.hub.yml logs -f backend
docker-compose -f docker-compose.hub.yml logs -f worker-process

# Últimas 100 líneas
docker-compose -f docker-compose.hub.yml logs --tail=100 backend
```

---

## 🌐 Acceso a Servicios

Una vez deployed, accede a:

| Servicio | URL | Usuario | Password |
|----------|-----|---------|----------|
| **Frontend** | http://localhost:3000 | - | - |
| **Backend API** | http://localhost:8000 | - | - |
| **API Docs** | http://localhost:8000/docs | - | - |
| **Phoenix UI** | http://localhost:6006 | - | - |
| **OpenSearch** | http://localhost:9200 | admin | Admin@123 |
| **MinIO** | http://localhost:9001 | minioadmin | minioadmin |
| **Grafana** | http://localhost:3001 | admin | admin |
| **Prometheus** | http://localhost:9090 | - | - |
| **MLflow** | http://localhost:5000 | - | - |

---

## 🐛 Troubleshooting

### Problema: Login fallido en Docker Hub

```bash
# Error: "unauthorized: incorrect username or password"

# Solución 1: Verificar credenciales
cat .docker.env | grep DOCKER

# Solución 2: Login manual
docker login -u rjamoriz

# Solución 3: Logout y login
docker logout
docker login -u rjamoriz
```

### Problema: Build falla

```bash
# Error: "Cannot connect to Docker daemon"

# Solución 1: Verificar Docker está corriendo
docker info

# Solución 2: Verificar permisos
sudo usermod -aG docker $USER
newgrp docker

# Solución 3: Reiniciar Docker
sudo systemctl restart docker
```

### Problema: Push falla por tamaño

```bash
# Error: "Error pushing image: blob size mismatch"

# Solución: Limpiar y reintentar
docker system prune -a
./docker-build-push.sh
```

### Problema: Imagen no se encuentra

```bash
# Error: "manifest unknown"

# Verificar que existe en Docker Hub
docker search rjamoriz/financia2030

# Pull manual
docker pull rjamoriz/financia2030-backend:latest

# Si no existe, hacer build y push
./docker-build-push.sh
```

### Problema: Contenedor no inicia

```bash
# Ver logs del contenedor
docker logs financia-backend

# Ver eventos
docker events

# Inspeccionar contenedor
docker inspect financia-backend

# Verificar dependencias
docker-compose -f docker-compose.hub.yml ps
```

### Problema: Puerto ya en uso

```bash
# Error: "port is already allocated"

# Ver qué usa el puerto
lsof -i :8000

# Matar proceso
kill -9 <PID>

# O cambiar puerto en docker-compose.hub.yml
ports:
  - "8080:8000"  # En lugar de 8000:8000
```

---

## 📦 Limpieza y Mantenimiento

### Limpiar imágenes locales sin usar

```bash
# Ver espacio usado
docker system df

# Limpiar todo lo no usado (CUIDADO!)
docker system prune -a

# Solo imágenes antiguas
docker image prune -a

# Solo contenedores detenidos
docker container prune
```

### Limpiar volúmenes

```bash
# Ver volúmenes
docker volume ls

# Limpiar volúmenes no usados
docker volume prune

# Eliminar volumen específico
docker volume rm financia_postgres_data
```

### Recrear todo desde cero

```bash
# 1. Detener y eliminar todo
docker-compose -f docker-compose.hub.yml down -v

# 2. Limpiar imágenes locales
docker system prune -a

# 3. Pull de imágenes frescas
docker-compose -f docker-compose.hub.yml pull

# 4. Iniciar de nuevo
docker-compose -f docker-compose.hub.yml up -d
```

---

## 🔄 Workflow Recomendado

### Desarrollo Local

```bash
# 1. Hacer cambios en el código
vim backend/services/rag_service.py

# 2. Test local (sin Docker)
cd backend
python -m pytest tests/

# 3. Commit cambios
git add .
git commit -m "feat: mejora en RAG service"
git push
```

### Deploy a Docker Hub

```bash
# 1. Build y push de imágenes actualizadas
./docker-build-push.sh

# 2. Pull en servidor/ambiente
docker-compose -f docker-compose.hub.yml pull

# 3. Restart servicios
docker-compose -f docker-compose.hub.yml up -d --force-recreate backend

# 4. Verificar
curl http://localhost:8000/health
docker-compose -f docker-compose.hub.yml logs -f backend
```

### Rollback

```bash
# Si algo sale mal, volver a versión anterior

# 1. Pull de tag anterior
docker pull rjamoriz/financia2030-backend:v1.0.0

# 2. Re-tag como latest
docker tag rjamoriz/financia2030-backend:v1.0.0 rjamoriz/financia2030-backend:latest

# 3. Restart
docker-compose -f docker-compose.hub.yml up -d --force-recreate backend
```

---

## 📊 Resumen de Comandos Clave

```bash
# Login
docker login -u rjamoriz

# Build y Push todas las imágenes
./docker-build-push.sh

# Deployment completo
./deploy-dockerhub.sh

# Ver estado
docker-compose -f infrastructure/docker/docker-compose.hub.yml ps

# Ver logs
docker-compose -f infrastructure/docker/docker-compose.hub.yml logs -f

# Detener todo
docker-compose -f infrastructure/docker/docker-compose.hub.yml down

# Limpiar
docker system prune -a
```

---

## ✅ Checklist de Deployment

- [ ] ✅ Login en Docker Hub
- [ ] ✅ Build de imágenes locales
- [ ] ✅ Push de imágenes a Docker Hub
- [ ] ✅ Verificar imágenes en hub.docker.com
- [ ] ✅ Configurar backend/.env con API keys
- [ ] ✅ Pull de imágenes en servidor
- [ ] ✅ Iniciar servicios con docker-compose
- [ ] ✅ Verificar health checks
- [ ] ✅ Acceder a Frontend (localhost:3000)
- [ ] ✅ Acceder a Backend API (localhost:8000/docs)
- [ ] ✅ Acceder a Phoenix UI (localhost:6006)
- [ ] ✅ Test de query RAG
- [ ] ✅ Verificar logs sin errores

---

**🎉 ¡Tu sistema está listo para usar con Docker Hub!**

**Docker Hub:** https://hub.docker.com/u/rjamoriz
