# Backend - FinancIA 2030

Backend API construido con FastAPI para el Sistema Corporativo Documental con Capacidades de IA.

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- PostgreSQL 15+ con extensión pgvector
- OpenSearch 2.11+
- Redis 7.2+
- Apache Kafka 3.6+
- MinIO
- Tesseract OCR

### Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelos spaCy
python -m spacy download es_core_news_lg

# Copiar variables de entorno
cp ../.env.example ../.env
# Editar .env con tus configuraciones

# Crear base de datos y tablas
# (Se crean automáticamente al iniciar la aplicación)
```

### Ejecución

```bash
# Desarrollo (con hot reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Acceso

- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Estructura

```
backend/
├── api/                    # API endpoints
│   └── v1/                # API versión 1
│       ├── auth.py        # Autenticación
│       ├── documents.py   # Gestión de documentos
│       ├── search.py      # Búsqueda
│       ├── rag.py         # RAG/Chat
│       ├── risk.py        # Análisis de riesgo
│       └── compliance.py  # Compliance y auditoría
├── core/                  # Configuración core
│   ├── config.py         # Settings
│   ├── database.py       # SQLAlchemy setup
│   └── logging_config.py # Logging
├── models/                # Modelos de datos
│   ├── database_models.py # SQLAlchemy models
│   └── schemas.py        # Pydantic models
├── services/              # Lógica de negocio
│   ├── ingest_service.py
│   ├── transform_service.py
│   ├── extract_service.py
│   ├── nlp_service.py
│   ├── classification_service.py
│   ├── search_service.py
│   ├── rag_service.py
│   ├── risk_service.py
│   └── compliance_service.py
├── workers/               # Kafka workers
│   ├── ingest_worker.py
│   ├── process_worker.py
│   └── index_worker.py
├── ml/                    # Modelos ML/IA
│   ├── ner_model.py
│   ├── classifier.py
│   ├── embeddings.py
│   └── llm_client.py
├── utils/                 # Utilidades
│   ├── security.py
│   ├── validators.py
│   └── helpers.py
├── tests/                 # Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── logs/                  # Logs (generado)
├── main.py               # Entry point
└── requirements.txt      # Dependencias
```

## 🔌 API Endpoints

### Authentication (`/api/v1/auth`)

- `POST /register` - Registrar usuario
- `POST /login` - Login
- `POST /logout` - Logout
- `POST /refresh` - Refresh token
- `GET /me` - Usuario actual
- `PUT /me` - Actualizar perfil
- `POST /mfa/enable` - Habilitar MFA
- `POST /mfa/verify` - Verificar código MFA

### Documents (`/api/v1/documents`)

- `POST /upload` - Subir documento
- `GET /{id}` - Obtener documento
- `GET /` - Listar documentos (con filtros)
- `PUT /{id}` - Actualizar metadatos
- `DELETE /{id}` - Eliminar documento
- `GET /{id}/download` - Descargar archivo
- `GET /{id}/entities` - Obtener entidades (NER)
- `GET /{id}/chunks` - Obtener chunks
- `POST /{id}/reprocess` - Reprocesar documento

### Search (`/api/v1/search`)

- `POST /` - Búsqueda híbrida
- `GET /suggest` - Sugerencias de búsqueda
- `GET /facets` - Obtener facetas para filtros

### RAG (`/api/v1/rag`)

- `POST /query` - Preguntar al asistente
- `GET /conversations/{id}` - Obtener conversación
- `DELETE /conversations/{id}` - Eliminar conversación

### Risk (`/api/v1/risk`)

- `POST /{document_id}/assess` - Evaluar riesgo
- `GET /{document_id}/risk` - Obtener evaluación existente
- `GET /dashboard` - Dashboard de riesgos

### Compliance (`/api/v1/compliance`)

- `POST /check` - Ejecutar checks de compliance
- `GET /{document_id}/compliance` - Obtener resultados
- `POST /dsr` - Crear Data Subject Request (GDPR)
- `GET /dsr` - Listar DSRs
- `POST /audit/query` - Consultar logs de auditoría
- `GET /audit/export` - Exportar logs

## 🔒 Seguridad

- **Autenticación**: JWT tokens con refresh
- **MFA**: TOTP (opcional, configurable)
- **Autorización**: RBAC + ABAC
- **Cifrado**: TLS 1.3 en tránsito, AES-256 en reposo
- **Rate Limiting**: Configurable por endpoint
- **Input Validation**: Pydantic schemas
- **SQL Injection**: Protección con SQLAlchemy ORM
- **XSS**: Sanitización automática
- **CSRF**: Tokens CSRF en formularios

## 🧪 Testing

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Solo unit tests
pytest tests/unit/

# Solo integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/
```

## 📊 Observabilidad

### Logging

- **Formato**: JSON estructurado
- **Niveles**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Destinos**: 
  - Console (stdout)
  - Archivo `logs/app.log`
  - Archivo `logs/error.log` (solo errores)
  - Archivo `logs/audit.log` (append-only, inmutable)

### Métricas (Prometheus)

- `http_requests_total` - Total de requests
- `http_request_duration_seconds` - Latencia de requests
- `documents_processed_total` - Documentos procesados
- `documents_ingested_total` - Documentos ingestados
- `search_latency_seconds` - Latencia de búsquedas
- `rag_response_time_seconds` - Tiempo de respuesta RAG

### Tracing (OpenTelemetry)

- Trazas end-to-end de requests
- Spans por servicio
- Integración con Jaeger/Zipkin

## 🚀 Despliegue

### Docker

```bash
# Build
docker build -t financia-backend:latest .

# Run
docker run -p 8000:8000 \
  --env-file .env \
  financia-backend:latest
```

### Docker Compose

Ver `../infrastructure/docker/docker-compose.yml`

### Kubernetes

Ver `../infrastructure/kubernetes/`

## 📝 Estado Actual

### ✅ Completado

- [x] Estructura base del proyecto
- [x] Configuración (Settings)
- [x] Modelos de base de datos (SQLAlchemy)
- [x] Modelos de API (Pydantic)
- [x] Routers principales (esqueleto)
- [x] Logging configurado
- [x] Health checks

### 🚧 En Desarrollo

- [ ] Servicios de negocio (services/)
- [ ] Workers de Kafka (workers/)
- [ ] Modelos ML/IA (ml/)
- [ ] Tests completos
- [ ] Documentación de API detallada

### 📅 Pendiente

- [ ] Implementación completa de endpoints
- [ ] Autenticación JWT + MFA
- [ ] Integración con OpenSearch
- [ ] Integración con MinIO
- [ ] Pipeline de procesamiento documental
- [ ] Modelos NER y clasificación
- [ ] RAG con LLM
- [ ] Scoring de riesgo
- [ ] Motor de compliance
- [ ] Observabilidad completa (Prometheus, OTel)

## 🤝 Contribución

Ver [`../README.md`](../README.md) para guías de contribución.

## 📜 Licencia

Copyright © 2025 TeFinancia S.A. Todos los derechos reservados.
