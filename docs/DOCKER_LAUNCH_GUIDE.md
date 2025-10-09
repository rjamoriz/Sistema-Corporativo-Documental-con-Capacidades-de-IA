# 🐳 Guía para Lanzar la APP con Docker

**Fecha**: 9 de Octubre 2025  
**Versión**: 1.0

---

## 📋 Índice

1. [Pre-requisitos](#pre-requisitos)
2. [Opción 1: Usar Imágenes de Docker Hub (Rápido)](#opción-1-usar-imágenes-de-docker-hub-rápido)
3. [Opción 2: Build Local](#opción-2-build-local)
4. [Opción 3: Build y Push Actualizado](#opción-3-build-y-push-actualizado)
5. [Configuración de Variables](#configuración-de-variables)
6. [Verificación y Testing](#verificación-y-testing)
7. [Troubleshooting](#troubleshooting)

---

## Pre-requisitos

### 1. Espacio en Disco

```bash
# Verificar espacio disponible
df -h

# Recomendado:
# - Mínimo: 20 GB libres
# - Recomendado: 50 GB libres
```

### 2. Docker Instalado

```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar que Docker está corriendo
docker ps
```

### 3. Memoria RAM

- **Mínimo**: 8 GB
- **Recomendado**: 16 GB (para todos los servicios)

---

## Opción 1: Usar Imágenes de Docker Hub (Rápido)

Esta opción usa las imágenes pre-construidas en Docker Hub.

### ⚠️ IMPORTANTE
Las imágenes actuales en Docker Hub **NO incluyen el código nuevo** de generación sintética. Fueron subidas antes del commit de hoy.

### Pasos

#### 1. Clonar el repositorio

```bash
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA.git
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA
```

#### 2. Crear archivo de variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus valores:
```bash
# OpenAI
OPENAI_API_KEY=sk-your-actual-key-here

# Database
DATABASE_URL=postgresql+asyncpg://financia:financia2030@postgres:5432/financia_db

# Servicios
OPENSEARCH_HOST=opensearch
REDIS_URL=redis://redis:6379/0
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
MINIO_ENDPOINT=minio:9000

# Configuración
ENVIRONMENT=development
```

#### 3. Iniciar servicios

```bash
# Usar archivo docker-compose.hub.yml (imágenes de Docker Hub)
docker-compose -f infrastructure/docker/docker-compose.hub.yml up -d
```

#### 4. Verificar que están corriendo

```bash
docker-compose -f infrastructure/docker/docker-compose.hub.yml ps
```

#### 5. Ver logs

```bash
# Todos los servicios
docker-compose -f infrastructure/docker/docker-compose.hub.yml logs -f

# Solo backend
docker-compose -f infrastructure/docker/docker-compose.hub.yml logs -f backend

# Solo un servicio específico
docker-compose -f infrastructure/docker/docker-compose.hub.yml logs -f postgres
```

#### 6. Acceder a la aplicación

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend** (si está habilitado): http://localhost:3000
- **Phoenix (Observability)**: http://localhost:6006
- **MinIO (Storage)**: http://localhost:9001
- **Grafana (Monitoring)**: http://localhost:3001

#### 7. Actualizar código SIN rebuild

Si quieres probar el código nuevo sin rebuild:

```bash
# Entrar al contenedor
docker exec -it financia-backend bash

# Actualizar código
cd /app
git pull origin main

# Salir
exit

# Reiniciar backend
docker-compose -f infrastructure/docker/docker-compose.hub.yml restart backend
```

---

## Opción 2: Build Local

Construir las imágenes localmente con el código más reciente.

### Pasos

#### 1. Clonar repositorio

```bash
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA.git
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA
```

#### 2. Configurar variables

```bash
cp .env.example .env
# Editar .env con tus valores
```

#### 3. Build de imágenes

```bash
# Build solo backend
docker build -t financia-backend:local backend/

# Build solo frontend (si lo necesitas)
docker build -t financia-frontend:local frontend/

# Build todas las imágenes custom
docker-compose -f infrastructure/docker/docker-compose.yml build
```

#### 4. Modificar docker-compose para usar imágenes locales

Editar `infrastructure/docker/docker-compose.yml`:

```yaml
services:
  backend:
    # Cambiar:
    # image: rjamoriz/financia2030-backend:latest
    # Por:
    image: financia-backend:local
    # O simplemente usar:
    build: ../../backend
```

#### 5. Iniciar servicios

```bash
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

#### 6. Verificar

```bash
docker-compose -f infrastructure/docker/docker-compose.yml ps
docker-compose -f infrastructure/docker/docker-compose.yml logs -f backend
```

---

## Opción 3: Build y Push Actualizado

Para actualizar las imágenes en Docker Hub con el código nuevo.

### Pasos

#### 1. Autenticarse en Docker Hub

```bash
# Cargar variables
source .docker.env

# Login
echo $DOCKER_TOKEN | docker login -u $DOCKER_USERNAME --password-stdin
```

#### 2. Build y Push con script

```bash
# Build y push versión nueva
./docker-build-push.sh v1.1.0-synthetic

# Resultado:
# - rjamoriz/financia2030-backend:v1.1.0-synthetic
# - rjamoriz/financia2030-backend:latest (actualizado)
# - rjamoriz/financia2030-frontend:v1.1.0-synthetic
# - rjamoriz/financia2030-frontend:latest (actualizado)
```

#### 3. Usar las nuevas imágenes

```bash
# Pull las nuevas imágenes
docker pull rjamoriz/financia2030-backend:latest
docker pull rjamoriz/financia2030-frontend:latest

# Reiniciar con nuevas imágenes
docker-compose -f infrastructure/docker/docker-compose.hub.yml down
docker-compose -f infrastructure/docker/docker-compose.hub.yml up -d
```

---

## Configuración de Variables

### Variables Esenciales

```bash
# .env file
OPENAI_API_KEY=sk-your-key                    # REQUERIDO para IA
DATABASE_URL=postgresql+asyncpg://...         # REQUERIDO
OPENSEARCH_HOST=opensearch                    # REQUERIDO para búsqueda
REDIS_URL=redis://redis:6379/0                # REQUERIDO para cache
KAFKA_BOOTSTRAP_SERVERS=kafka:9092            # REQUERIDO para eventos
MINIO_ENDPOINT=minio:9000                     # REQUERIDO para storage
ENVIRONMENT=development                       # development/staging/production
```

### Variables Opcionales

```bash
# Observabilidad
PHOENIX_HOST=http://phoenix
PHOENIX_PORT=6006

# Seguridad
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Storage
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=financia-docs

# Database
POSTGRES_DB=financia_db
POSTGRES_USER=financia
POSTGRES_PASSWORD=financia2030
```

---

## Verificación y Testing

### 1. Health Check

```bash
# Backend
curl http://localhost:8000/health

# Respuesta esperada:
# {"status":"healthy"}
```

### 2. API Docs

Abrir en navegador: http://localhost:8000/docs

### 3. Test de endpoints

```bash
# Listar endpoints synthetic data
curl http://localhost:8000/api/v1/synthetic/templates

# Verificar PostgreSQL
docker exec -it financia-postgresql psql -U financia -d financia_db -c "SELECT version();"

# Verificar OpenSearch
curl http://localhost:9200/_cluster/health

# Verificar Redis
docker exec -it financia-redis redis-cli ping

# Verificar MinIO
curl http://localhost:9001
```

### 4. Logs de servicios

```bash
# Ver logs en tiempo real
docker-compose -f infrastructure/docker/docker-compose.hub.yml logs -f

# Ver últimas 100 líneas de backend
docker-compose -f infrastructure/docker/docker-compose.hub.yml logs --tail=100 backend

# Ver logs de errores
docker-compose -f infrastructure/docker/docker-compose.hub.yml logs | grep ERROR
```

---

## Troubleshooting

### Problema 1: Sin Espacio en Disco

**Error**: `no space left on device`

**Solución**:
```bash
# Limpiar imágenes no usadas
docker system prune -a

# Limpiar volúmenes no usados
docker volume prune

# Ver espacio usado por Docker
docker system df

# Limpiar build cache
docker builder prune
```

### Problema 2: Puerto Ya en Uso

**Error**: `port is already allocated`

**Solución**:
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8000
sudo netstat -tulpn | grep 8000

# Matar proceso
sudo kill -9 <PID>

# O cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar puerto host
```

### Problema 3: Contenedor No Inicia

**Error**: Container exits immediately

**Solución**:
```bash
# Ver logs del contenedor
docker logs financia-backend

# Ver último comando ejecutado
docker inspect financia-backend | grep -A 10 Cmd

# Iniciar en modo interactivo para debug
docker run -it financia-backend:latest bash
```

### Problema 4: Base de Datos No Conecta

**Error**: `could not connect to database`

**Solución**:
```bash
# Verificar que PostgreSQL está corriendo
docker-compose -f infrastructure/docker/docker-compose.hub.yml ps postgres

# Verificar logs de PostgreSQL
docker-compose -f infrastructure/docker/docker-compose.hub.yml logs postgres

# Reiniciar PostgreSQL
docker-compose -f infrastructure/docker/docker-compose.hub.yml restart postgres

# Verificar conectividad desde backend
docker exec -it financia-backend bash
nc -zv postgres 5432
```

### Problema 5: OpenSearch Falla

**Error**: `OpenSearch not responding`

**Solución**:
```bash
# Aumentar memoria virtual (Linux)
sudo sysctl -w vm.max_map_count=262144

# Verificar logs
docker logs financia-opensearch

# Reiniciar con más memoria
docker-compose -f infrastructure/docker/docker-compose.hub.yml down
# Editar docker-compose.yml y aumentar memoria:
# OPENSEARCH_JAVA_OPTS=-Xms4g -Xmx4g
docker-compose -f infrastructure/docker/docker-compose.hub.yml up -d
```

### Problema 6: Variables de Entorno No se Cargan

**Error**: Environment variables not set

**Solución**:
```bash
# Verificar que .env existe
ls -la .env

# Ver variables cargadas en contenedor
docker exec -it financia-backend env | grep OPENAI

# Reiniciar contenedor para recargar
docker-compose -f infrastructure/docker/docker-compose.hub.yml restart backend
```

---

## Comandos Útiles

### Gestión de Contenedores

```bash
# Detener todos los servicios
docker-compose -f infrastructure/docker/docker-compose.hub.yml down

# Detener y eliminar volúmenes (CUIDADO: borra datos)
docker-compose -f infrastructure/docker/docker-compose.hub.yml down -v

# Reiniciar un servicio específico
docker-compose -f infrastructure/docker/docker-compose.hub.yml restart backend

# Escalar un servicio
docker-compose -f infrastructure/docker/docker-compose.hub.yml up -d --scale backend=3

# Ver recursos usados
docker stats
```

### Inspección

```bash
# Ver configuración de un contenedor
docker inspect financia-backend

# Ver redes
docker network ls
docker network inspect financia-network

# Ver volúmenes
docker volume ls
docker volume inspect financia_postgresql_data

# Ejecutar comando en contenedor
docker exec -it financia-backend python --version
```

### Backup y Restore

```bash
# Backup de PostgreSQL
docker exec financia-postgresql pg_dump -U financia financia_db > backup.sql

# Restore
docker exec -i financia-postgresql psql -U financia financia_db < backup.sql

# Backup de volumen
docker run --rm -v financia_postgresql_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/postgres-backup.tar.gz /data
```

---

## Arquitectura de Servicios

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                  (financia-network)                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │ Frontend │    │ Backend  │    │ Phoenix  │         │
│  │ :3000    │◄───┤ :8000    │◄───┤ :6006    │         │
│  └──────────┘    └────┬─────┘    └──────────┘         │
│                       │                                 │
│         ┌─────────────┴─────────────┐                  │
│         ▼                           ▼                   │
│  ┌──────────┐              ┌──────────┐               │
│  │PostgreSQL│              │OpenSearch│               │
│  │ :5432    │              │ :9200    │               │
│  └──────────┘              └──────────┘               │
│         │                           │                  │
│         ▼                           ▼                  │
│  ┌──────────┐              ┌──────────┐              │
│  │  Redis   │              │  Kafka   │              │
│  │  :6379   │              │  :9092   │              │
│  └──────────┘              └──────────┘              │
│         │                           │                 │
│         ▼                           ▼                 │
│  ┌──────────┐              ┌──────────┐             │
│  │  MinIO   │              │ Zookeeper│             │
│  │  :9000   │              │  :2181   │             │
│  └──────────┘              └──────────┘             │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## Orden de Inicio Recomendado

```bash
# 1. Servicios de infraestructura primero
docker-compose -f infrastructure/docker/docker-compose.hub.yml up -d \
  postgres redis zookeeper

# Esperar 10 segundos
sleep 10

# 2. Servicios que dependen de infraestructura
docker-compose -f infrastructure/docker/docker-compose.hub.yml up -d \
  kafka opensearch minio

# Esperar 20 segundos
sleep 20

# 3. Aplicación
docker-compose -f infrastructure/docker/docker-compose.hub.yml up -d \
  backend phoenix

# 4. Frontend (opcional)
# docker-compose -f infrastructure/docker/docker-compose.hub.yml up -d frontend
```

---

## Servicios Mínimos para Desarrollo

Si quieres solo los servicios esenciales:

```bash
# Solo backend + PostgreSQL + Redis
docker-compose -f infrastructure/docker/docker-compose.hub.yml up -d \
  postgres redis backend
```

Editar `.env`:
```bash
# Deshabilitar servicios opcionales
USE_OPENSEARCH=false
USE_KAFKA=false
USE_MINIO=false
```

---

## Monitoreo

### Grafana Dashboards

1. Acceder: http://localhost:3001
2. Usuario: `admin`
3. Password: `admin`
4. Importar dashboards desde `infrastructure/monitoring/dashboards/`

### Prometheus Metrics

- URL: http://localhost:9090
- Métricas de FastAPI: http://localhost:8000/metrics

### Phoenix Observability

- URL: http://localhost:6006
- Ver traces de LLM
- Analizar latencias
- Debug de prompts

---

## Performance Tips

### 1. Limitar Memoria

Editar `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### 2. Usar Bind Mounts en Dev

Para desarrollo rápido sin rebuild:
```yaml
services:
  backend:
    volumes:
      - ../../backend:/app
    # Hot reload automático
```

### 3. Multi-Stage Builds

Ya implementado en `Dockerfile`:
```dockerfile
# Build stage
FROM python:3.11-slim as builder
...

# Runtime stage
FROM python:3.11-slim
COPY --from=builder ...
```

---

## Seguridad en Producción

```bash
# 1. No usar puertos por defecto
ports:
  - "18000:8000"  # Backend en puerto custom

# 2. Usar secrets
echo "my-secret" | docker secret create jwt_secret -
docker service update --secret-add jwt_secret backend

# 3. Escanear vulnerabilidades
docker scan rjamoriz/financia2030-backend:latest

# 4. Actualizar imágenes base
docker pull python:3.11-slim
docker build --pull ...

# 5. No correr como root
USER appuser
```

---

## Enlaces Útiles

- **Documentación Principal**: `/docs/DEPLOYMENT.md`
- **Guía de Datos Sintéticos**: `/docs/SYNTHETIC_GENERATOR_USAGE.md`
- **Docker Hub**: https://hub.docker.com/u/rjamoriz
- **Repo GitHub**: https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

---

**Última actualización**: 9 de Octubre 2025  
**Mantenedor**: Equipo FinancIA 2030
