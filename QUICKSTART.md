# 🚀 Guía de Inicio Rápido - Sistema Corporativo Documental con IA

Esta guía te ayudará a levantar el sistema completo en menos de 10 minutos.

---

## 📋 Requisitos Previos

### Sistema Operativo
- Ubuntu 22.04 LTS o superior (recomendado)
- macOS 12+ o Windows 11 con WSL2

### Software Necesario
```bash
# Verificar versiones instaladas
docker --version          # Docker 24.0+
docker-compose --version  # Docker Compose 2.20+
python3 --version         # Python 3.11+
node --version            # Node.js 20+
npm --version             # npm 10+
git --version             # Git 2.40+
```

### Instalación de Requisitos (Ubuntu)
```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Docker Compose
sudo apt install docker-compose-plugin

# Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs

# Tesseract OCR
sudo apt install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

---

## 🎬 Inicio Rápido (3 pasos)

### 1️⃣ Clonar y Configurar

```bash
# Clonar repositorio
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA

# Ejecutar setup automático (instala dependencias, configura .env)
./scripts/setup.sh
```

**¿Qué hace `setup.sh`?**
- ✅ Verifica requisitos del sistema
- ✅ Crea entornos virtuales Python
- ✅ Instala dependencias backend (80+ paquetes)
- ✅ Instala dependencias frontend (40+ paquetes npm)
- ✅ Configura archivos .env con valores por defecto
- ✅ Verifica conectividad a servicios Docker

### 2️⃣ Iniciar Infraestructura

```bash
# Iniciar todos los servicios Docker (12 contenedores)
./scripts/start.sh
```

**Servicios iniciados:**
- PostgreSQL 15 + pgvector (puerto 5432)
- OpenSearch 2.11 (puerto 9200)
- Redis 7.2 (puerto 6379)
- Kafka 3.6 + Zookeeper (puertos 9092, 2181)
- MinIO (puertos 9000, 9001)
- Prometheus (puerto 9090)
- Grafana (puerto 3001)
- MLflow (puerto 5000)

**Tiempo de inicio:** ~2-3 minutos

### 3️⃣ Iniciar Aplicación

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # o venv\Scripts\activate en Windows
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Workers (opcional para procesamiento):**
```bash
cd backend
source venv/bin/activate
python -m workers.ingest_worker &
python -m workers.process_worker &
python -m workers.index_worker &
```

---

## 🌐 Acceso a la Aplicación

### Frontend (Interfaz Principal)
**URL:** http://localhost:3000

**Páginas disponibles:**
- `/dashboard` - Estadísticas y gráficos
- `/upload` - Subir documentos
- `/search` - Buscar documentos
- `/chat` - Chat RAG con IA

### Backend API
**URL:** http://localhost:8000

**Documentación:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### Servicios de Infraestructura

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Grafana** | http://localhost:3001 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **OpenSearch** | http://localhost:9200 | admin / admin |
| **MLflow** | http://localhost:5000 | - |

---

## 🧪 Verificar Instalación

### Test Automático
```bash
# Ejecutar suite completa de tests
./scripts/test.sh
```

**Tests incluidos:**
- ✅ Health checks de 12 servicios Docker
- ✅ Conectividad PostgreSQL, Redis, Kafka, OpenSearch
- ✅ Upload de documento de prueba
- ✅ Procesamiento completo (OCR → NER → Index)
- ✅ Búsqueda híbrida
- ✅ Query RAG
- ✅ Scoring de riesgo
- ✅ Verificación compliance

### Test Manual

1. **Verificar servicios Docker:**
```bash
docker-compose ps
# Todos los servicios deben estar "Up" y "healthy"
```

2. **Verificar backend:**
```bash
curl http://localhost:8000/health
# Respuesta: {"status": "healthy"}
```

3. **Verificar frontend:**
- Abrir http://localhost:3000
- Debe cargar el Dashboard

---

## 📊 Generar Datos de Prueba

```bash
# Generar 200 documentos sintéticos en 8 categorías
python scripts/generate_synthetic_data.py

# Documentos generados en: data/synthetic_documents/
# Manifest con estadísticas: data/synthetic_documents/manifest.json
```

**Categorías generadas:**
- 30 Contratos (PDF)
- 35 Facturas (PDF)
- 25 Nóminas (PDF)
- 25 Especificaciones técnicas (DOCX)
- 20 Informes de marketing (PDF)
- 20 Procedimientos operacionales (DOCX)
- 25 Políticas de compliance (PDF)
- 20 Documentos multimedia (PNG)

**Subir documentos:**
1. Ir a http://localhost:3000/upload
2. Arrastrar archivos desde `data/synthetic_documents/`
3. Esperar procesamiento (status: INDEXED)
4. Buscar en http://localhost:3000/search

---

## 🔧 Troubleshooting

### Error: "Cannot connect to Docker daemon"
```bash
# Iniciar Docker
sudo systemctl start docker

# Agregar usuario a grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### Error: "Port already in use"
```bash
# Ver qué está usando el puerto (ejemplo: 8000)
sudo lsof -i :8000

# Detener proceso
kill -9 <PID>

# O cambiar puerto en .env
```

### Error: "ModuleNotFoundError" en Python
```bash
# Reinstalar dependencias
cd backend
pip install -r requirements.txt
```

### Error: "npm ERR!" en Frontend
```bash
# Limpiar cache y reinstalar
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Servicios Docker no inician
```bash
# Ver logs de servicios
docker-compose logs -f <servicio>

# Reiniciar servicios
./scripts/stop.sh
./scripts/start.sh

# Reiniciar Docker completo
sudo systemctl restart docker
```

### Backend responde lento
```bash
# Verificar uso de recursos
docker stats

# Aumentar RAM asignada a Docker:
# Docker Desktop > Settings > Resources > Memory: 8GB+
```

---

## 🛑 Detener el Sistema

### Opción 1: Detener todo (recomendado)
```bash
./scripts/stop.sh
```

### Opción 2: Solo aplicación (mantener infraestructura)
```bash
# Detener backend (Ctrl+C en terminal)
# Detener frontend (Ctrl+C en terminal)
# Detener workers (Ctrl+C en terminal)
```

### Opción 3: Limpiar todo (incluye volúmenes)
```bash
cd infrastructure/docker
docker-compose down -v
# ⚠️ ADVERTENCIA: Elimina todos los datos
```

---

## 💾 Backup y Restore

### Crear Backup
```bash
./scripts/backup.sh

# Backup guardado en: backups/backup_YYYYMMDD_HHMMSS/
# Incluye:
# - PostgreSQL dump
# - MinIO data (documentos)
# - Logs de aplicación
```

### Restaurar desde Backup
```bash
./scripts/restore.sh backups/backup_YYYYMMDD_HHMMSS

# Restaura:
# - Base de datos
# - Archivos en MinIO
# - Configuraciones
```

---

## 📚 Recursos Adicionales

### Documentación
- [Arquitectura Técnica](docs/ARCHITECTURE.md)
- [Gobernanza de IA](docs/GOVERNANCE.md)
- [DPIA](docs/DPIA.md)
- [Scripts Operacionales](scripts/README.md)
- [Frontend README](frontend/README.md)

### API Endpoints (Swagger)
- http://localhost:8000/docs

### Ejemplos de Uso

**1. Upload de documento vía API:**
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@contrato.pdf" \
  -F "user_id=user-123"
```

**2. Búsqueda híbrida:**
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contrato de confidencialidad",
    "search_mode": "hybrid",
    "page_size": 10
  }'
```

**3. Query RAG:**
```bash
curl -X POST http://localhost:8000/api/v1/rag/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es el plazo del contrato?",
    "max_chunks": 5
  }'
```

---

## 🎯 Siguientes Pasos

1. ✅ **Explorar Dashboard** - http://localhost:3000/dashboard
2. ✅ **Subir documentos** - http://localhost:3000/upload
3. ✅ **Probar búsqueda** - http://localhost:3000/search
4. ✅ **Chatear con RAG** - http://localhost:3000/chat
5. ✅ **Ver métricas** - http://localhost:3001 (Grafana)
6. ✅ **Revisar logs** - `docker-compose logs -f backend`

---

## 📞 Soporte

**Issues:** https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA/issues

**Documentación completa:** [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)

---

**¡Listo para comenzar! 🚀**

Si tienes problemas, consulta la sección de Troubleshooting o revisa los logs con:
```bash
docker-compose logs -f
```
