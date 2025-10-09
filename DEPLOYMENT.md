# 🚀 Guía de Deployment - FinancIA 2030

## 📦 Imágenes Docker Disponibles

Todas las imágenes del sistema están disponibles públicamente en Docker Hub:

| Imagen | URL | Tamaño | Descripción |
|--------|-----|--------|-------------|
| **Backend** | `rjamoriz/financia2030-backend:latest` | ~7 GB | API Flask con ML/AI stack completo |
| **Frontend** | `rjamoriz/financia2030-frontend:latest` | ~54 MB | Aplicación React + nginx |
| **Worker Ingest** | `rjamoriz/financia2030-worker-ingest:latest` | ~7 GB | Worker de ingesta desde Kafka |
| **Worker Process** | `rjamoriz/financia2030-worker-process:latest` | ~7 GB | Worker de procesamiento (OCR, NER, embeddings) |
| **Worker Index** | `rjamoriz/financia2030-worker-index:latest` | ~7 GB | Worker de indexación vectorial (Qdrant) |

## 🎯 Deployment Rápido con Docker Hub

### Opción 1: Usar Docker Compose con imágenes pre-construidas

El método más rápido para desplegar el sistema completo:

```bash
# Navegar al directorio de infraestructura
cd infrastructure/docker

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de OpenAI, Qdrant, etc.

# Desplegar usando las imágenes de Docker Hub
docker-compose -f docker-compose.hub.yml up -d

# Ver el estado de los servicios
docker-compose -f docker-compose.hub.yml ps

# Ver logs
docker-compose -f docker-compose.hub.yml logs -f
```

### Opción 2: Pull individual de imágenes

Para descargar y ejecutar imágenes individuales:

```bash
# Descargar una imagen específica
docker pull rjamoriz/financia2030-backend:latest

# Ejecutar el backend (ejemplo básico)
docker run -d \
  --name financia-backend \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  rjamoriz/financia2030-backend:latest
```

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (React)                       │
│              rjamoriz/financia2030-frontend                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (Flask)                       │
│              rjamoriz/financia2030-backend                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │  Worker  │     │  Worker  │     │  Worker  │
    │  Ingest  │     │ Process  │     │  Index   │
    └──────────┘     └──────────┘     └──────────┘
         │                │                │
         │                │                │
         ▼                ▼                ▼
    ┌────────────────────────────────────────────┐
    │  PostgreSQL │ Redis │ Kafka │ Qdrant │... │
    └────────────────────────────────────────────┘
```

## 🔧 Configuración Requerida

### Variables de Entorno Esenciales

```bash
# OpenAI API
OPENAI_API_KEY=sk-...

# Base de datos
DATABASE_URL=postgresql://financia:financia2030@postgres:5432/financia_db

# Qdrant (Vector Database)
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_API_KEY=your_qdrant_key

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# MinIO (Object Storage)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Observabilidad
PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:6006
```

## 📋 Requisitos del Sistema

### Hardware Mínimo Recomendado

- **CPU**: 8 cores
- **RAM**: 32 GB (los workers con ML necesitan bastante memoria)
- **Disco**: 100 GB (50 GB para imágenes + 50 GB para datos)
- **Red**: Conexión estable para descargar ~28 GB de imágenes

### Software Requerido

- Docker Engine 20.10+
- Docker Compose 2.0+
- Sistema operativo: Linux (recomendado), macOS, Windows con WSL2

## 🚦 Verificación del Deployment

### 1. Verificar que todos los servicios están corriendo

```bash
docker-compose -f docker-compose.hub.yml ps
```

Todos los servicios deben mostrar estado `Up` o `healthy`.

### 2. Verificar salud de los servicios

```bash
# Backend API
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Prometheus metrics
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3001/api/health
```

### 3. Verificar logs

```bash
# Ver logs del backend
docker-compose -f docker-compose.hub.yml logs backend

# Ver logs de todos los workers
docker-compose -f docker-compose.hub.yml logs worker-ingest worker-process worker-index

# Seguir logs en tiempo real
docker-compose -f docker-compose.hub.yml logs -f --tail=100
```

## 🎨 Stack Tecnológico Incluido

### Backend & Workers (Python 3.11)
- **Framework**: Flask + Gunicorn
- **ML/AI**: PyTorch, LangChain, OpenAI, Anthropic
- **NLP**: spaCy (modelo español), sentence-transformers
- **OCR**: Tesseract, PyMuPDF, pdf2image
- **Observabilidad**: OpenTelemetry, Arize Phoenix
- **Total**: 314 paquetes Python

### Frontend (Node 20)
- **Framework**: React
- **Servidor web**: nginx (alpine)
- **Optimizado**: Build de producción minificado

### Infraestructura
- **Base de datos**: PostgreSQL 15 + pgvector
- **Cache**: Redis 7.2
- **Message Broker**: Kafka + Zookeeper
- **Object Storage**: MinIO
- **Metrics**: Prometheus + Grafana
- **Observabilidad**: Arize Phoenix

## 🔄 Actualizaciones

Para actualizar a la última versión de las imágenes:

```bash
# Detener servicios
docker-compose -f docker-compose.hub.yml down

# Descargar últimas imágenes
docker-compose -f docker-compose.hub.yml pull

# Reiniciar servicios
docker-compose -f docker-compose.hub.yml up -d
```

## 🛠️ Build Local (Desarrollo)

Si prefieres construir las imágenes localmente en lugar de usar Docker Hub:

```bash
# Usar el docker-compose.yml estándar que hace build local
docker-compose up -d --build
```

O usar el script optimizado de build:

```bash
# Configurar credenciales de Docker Hub (opcional, solo para push)
cp .docker.env.example .docker.env
# Editar .docker.env con tus credenciales

# Build y push automático
./docker-build-push-optimized.sh
```

## 🐛 Troubleshooting

### Problema: Out of memory

**Solución**: Los workers necesitan bastante RAM. Aumenta la memoria de Docker:
```bash
# Docker Desktop: Settings > Resources > Memory > 16+ GB
```

### Problema: Imágenes muy grandes

**Solución**: Las imágenes incluyen todo el stack de ML/AI. Son grandes pero completas:
- Backend/Workers: ~7 GB cada uno (PyTorch, spaCy, etc.)
- Total: ~28 GB

Para deployment en producción, considera:
- Usar un registry privado más cercano
- Implementar layer caching
- Separar imágenes base compartidas

### Problema: Timeout al descargar imágenes

**Solución**: 
```bash
# Aumentar el timeout de Docker
export COMPOSE_HTTP_TIMEOUT=600

# O descargar imágenes individualmente primero
docker pull rjamoriz/financia2030-backend:latest
docker pull rjamoriz/financia2030-frontend:latest
# ... etc
```

### Problema: Worker-process falla al iniciar

**Verificar**: El modelo de spaCy debe descargarse correctamente. Ver logs:
```bash
docker-compose -f docker-compose.hub.yml logs worker-process | grep spacy
```

La imagen ya incluye el modelo `es_core_news_lg` pre-instalado.

## 📊 Monitorización

### Dashboards Disponibles

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Arize Phoenix**: http://localhost:6006
- **Backend API Docs**: http://localhost:8000/docs

### Métricas Clave

- Tiempo de respuesta de la API
- Throughput de procesamiento de documentos
- Uso de memoria de workers
- Latencia de embeddings
- Rate de errores

## 🔐 Seguridad

### Para Producción

1. **Cambiar todas las contraseñas por defecto**
2. **Configurar secretos con Docker Secrets o variables de entorno seguras**
3. **Usar HTTPS con certificados SSL**
4. **Configurar firewall para exponer solo puertos necesarios**
5. **Habilitar autenticación en servicios (Redis, Kafka, etc.)**
6. **Mantener imágenes actualizadas**

```bash
# Escanear vulnerabilidades
docker scout cves rjamoriz/financia2030-backend:latest
```

## 📚 Documentación Adicional

- [Arquitectura del Sistema](./docs/architecture.md)
- [API Reference](http://localhost:8000/docs)
- [Configuración de Workers](./docs/workers.md)
- [Guía de Desarrollo](./docs/development.md)

## 🤝 Soporte

Para problemas o preguntas:
- Issues: GitHub Issues del repositorio
- Docker Hub: https://hub.docker.com/u/rjamoriz

## 📝 Changelog

### v1.0.0 (Octubre 2025)
- ✅ Primera versión estable en Docker Hub
- ✅ 5 imágenes disponibles públicamente
- ✅ Fix spaCy model download (pip wheel)
- ✅ Resolución de 7 conflictos de dependencias Python
- ✅ Script de deployment optimizado
- ✅ Stack completo de ML/AI (314 paquetes)

---

**Última actualización**: Octubre 9, 2025  
**Versión**: 1.0.0  
**Mantenedor**: rjamoriz
