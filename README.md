# 🚀 Sistema Corporativo Documental con Capacidades de IA# 🚀 Sistema Corporativo Documental con Capacidades de IA



<div align="center"><div align="center">



![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)

![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)

![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25-gold)![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25-gold)

![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)

![Coverage](https://img.shields.io/badge/Coverage-90%25-green)![Coverage](https://img.shields.io/badge/Coverage-90%25-green)

![Python](https://img.shields.io/badge/Python-3.11+-green)![Python](https://img.shields.io/badge/Python-3.11+-green)

![React](https://img.shields.io/badge/React-18.3-blue)![React](https://img.shields.io/badge/React-18.3-blue)

![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)

![Docker](https://img.shields.io/badge/Docker-Ready-blue)![Docker](https://img.shields.io/badge/Docker-Ready-blue)

![GPU](https://img.shields.io/badge/GPU-NVIDIA%20RTX%204070-76B900)![GPU](https://img.shields.io/badge/GPU-NVIDIA%20RTX%204070-76B900)



**Sistema enterprise de gestión documental con IA responsable**Sistema enterprise de gestión documental con IA responsable.  

Procesamiento inteligente | Cumplimiento normativo | Aceleración GPU

Procesamiento inteligente | Cumplimiento normativo | Aceleración GPU

[Inicio rápido](#-inicio-rápido) • [Arquitectura](#-arquitectura-del-sistema) • [Características](#-características-principales) • [Documentación](#-documentación-completa)

[Inicio rápido](#-inicio-rápido) • [Arquitectura](#-arquitectura-del-sistema) • [Características](#-características-principales) • [Documentación](#-documentación-completa)

</div>

</div>

### 📌 Diagrama estático (backup SVG) e interactivo

### 📌 Diagramas de arquitectura

- SVGs generados por CI: [C4 Context](docs/generated-diagrams/c4-context.svg) • [C4 Container](docs/generated-diagrams/c4-container.svg) • [Índice](docs/generated-diagrams/README.md)

- **SVGs generados por CI:** [C4 Context](docs/generated-diagrams/c4-context.svg) • [C4 Container](docs/generated-diagrams/c4-container.svg) • [Índice](docs/generated-diagrams/README.md)- Versión interactiva (GitHub Pages): https://rjamoriz.github.io/Sistema-Corporativo-Documental-con-Capacidades-de-IA/  

- **Versión interactiva:** https://rjamoriz.github.io/Sistema-Corporativo-Documental-con-Capacidades-de-IA/ (o ver [docs/index.html](docs/index.html))    (si aún no está activo, ver archivo estático: [docs/index.html](docs/index.html))



------



## 📋 Descripción## 📋 Descripción



Plataforma corporativa para gestionar, buscar y analizar documentos a escala con IA: clasificación, extracción de entidades, RAG con citación, scoring de riesgo y compliance automatizado (EU AI Act, GDPR). Optimizada para GPU (RTX 4070).Plataforma corporativa para gestionar, buscar y analizar documentos a escala con IA: clasificación, extracción de entidades, RAG con citación, scoring de riesgo y compliance automatizado (EU AI Act, GDPR). Optimizada para GPU (RTX 4070).



**Cliente:** TeFinancia S.A. | **Proyecto:** FinancIA 2030 | **Estado:** Production Ready---



---## 🎯 Características Principales



## 🎯 Características Principales- IA Documental: clasificación, OCR, NER, resúmenes, anomalías

- Búsqueda híbrida y RAG con citación obligatoria de fuentes

- **IA Documental:** clasificación, OCR, NER, resúmenes, detección de anomalías- Compliance automatizado (EU AI Act, GDPR) con trazabilidad

- **Búsqueda híbrida:** léxica (BM25) + semántica (embeddings) con RAG y citación obligatoria- Observabilidad de LLMs (Phoenix) y explicabilidad (LIME/SHAP)

- **Compliance automatizado:** EU AI Act, GDPR, NIS2 con trazabilidad completa- Alto rendimiento: p95 < 2s en 1M+ documentos, SLA 99.9%

- **Observabilidad de LLMs:** Arize Phoenix (OTLP) con explicabilidad (LIME/SHAP)

- **Alto rendimiento:** p95 < 2s en 1M+ documentos, SLA 99.9%---



---## 🏗️ Arquitectura del Sistema (vista microservicios)



## 🏗️ Arquitectura del Sistema```mermaid

flowchart TB

### Vista de microservicios        subgraph Client

            UI[React SPA\nTypeScript + Vite]

```mermaid        end

flowchart TB

    subgraph Client        subgraph Gateway

        UI[React SPA<br/>TypeScript + Vite]            NGINX[NGINX\nTLS/Reverse Proxy]

    end        end



    subgraph Gateway        subgraph Backend[Backend Services]

        NGINX[NGINX<br/>TLS/Reverse Proxy]            API[FastAPI API]

    end            DOC[Document Service]

            SRCH[Search Service]

    subgraph Backend[Backend Services]            COMP[Compliance Service]

        API[FastAPI API]            RISK[Risk Scoring]

        DOC[Document Service]        end

        SRCH[Search Service]

        COMP[Compliance Service]        subgraph Workers[Async Workers]

        RISK[Risk Scoring]            CELERY[Celery Workers]

    end            JOBS[Schedulers]

        end

    subgraph Workers[Async Workers]

        CELERY[Celery Workers]        subgraph ML[ML/AI Pipeline]

        JOBS[Schedulers]            OCR[OCR Engine]

    end            NER[NER Model]

            EMB[Embeddings]

    subgraph ML[ML/AI Pipeline]            CLF[Classifier]

        OCR[OCR Engine]        end

        NER[NER Model]

        EMB[Embeddings]        subgraph Data[Data Stores]

        CLF[Classifier]            PG[(PostgreSQL)]

    end            QD[(Qdrant Vectors)]

            RD[(Redis Cache)]

    subgraph Data[Data Stores]            S3[(MinIO S3)]

        PG[(PostgreSQL)]        end

        QD[(Qdrant Vectors)]

        RD[(Redis Cache)]        subgraph External[External APIs]

        S3[(MinIO S3)]            OFAC[OFAC]

    end            OPENAI[OpenAI GPT-4]

            PHX[Arize Phoenix]

    subgraph External[External APIs]        end

        OFAC[OFAC]

        OPENAI[OpenAI GPT-4]        UI --> NGINX --> API

        PHX[Arize Phoenix]        API --> DOC

    end        API --> SRCH

        API --> COMP

    UI --> NGINX --> API        API --> RISK

    API --> DOC

    API --> SRCH        DOC --> CELERY --> OCR --> NER --> CLF

    API --> COMP        SRCH --> EMB --> OPENAI

    API --> RISK

        API --> PG

    DOC --> CELERY --> OCR --> NER --> CLF        SRCH --> QD

    SRCH --> EMB --> OPENAI        API --> RD

        DOC --> S3

    API --> PG

    SRCH --> QD        COMP --> OFAC

    API --> RD        API --> PHX

    DOC --> S3```



    COMP --> OFAC### Flujo de procesamiento de documentos

    API --> PHX

``````mermaid

sequenceDiagram

### Flujo de procesamiento de documentos        autonumber

        actor Usuario

```mermaid        participant UI as Frontend (React)

sequenceDiagram        participant API as Backend (FastAPI)

    autonumber        participant S3 as MinIO (S3)

    actor Usuario        participant DB as PostgreSQL

    participant UI as Frontend        participant ML as ML Pipeline

    participant API as Backend        participant VDB as Qdrant

    participant S3 as MinIO

    participant DB as PostgreSQL        Usuario->>UI: Subir documento

    participant ML as ML Pipeline        UI->>API: POST /documents/upload

    participant VDB as Qdrant        API->>S3: Guardar archivo

        S3-->>API: file_id

    Usuario->>UI: Subir documento        API->>DB: Crear metadata (document_id)

    UI->>API: POST /documents/upload        API->>ML: Encolar procesamiento

    API->>S3: Guardar archivo        activate ML

    S3-->>API: file_id        ML->>ML: OCR + NER + Clasificación

    API->>DB: Crear metadata        ML->>VDB: Generar embeddings

    API->>ML: Encolar procesamiento        ML->>DB: Actualizar estado y resultados

    activate ML        deactivate ML

    ML->>ML: OCR + NER + Clasificacion        API-->>UI: Notificar documento procesado

    ML->>VDB: Generar embeddings```

    ML->>DB: Actualizar estado

    deactivate ML---

    API-->>UI: Notificar documento procesado

```## 🧠 Stack Tecnológico



---- Frontend: React 18.3, TypeScript 5.5, Vite, TanStack Query, Tailwind

- Backend: FastAPI (Python 3.11), SQLAlchemy 2.0, Pydantic v2, Celery

## 🧠 Stack Tecnológico- ML/AI: SpaCy, Sentence-BERT, Scikit-learn, PyTorch, LIME/SHAP, Tesseract

- Datos: PostgreSQL, Qdrant, Redis, MinIO (S3)

- **Frontend:** React 18.3, TypeScript 5.5, Vite, TanStack Query, Tailwind- DevOps: Docker Compose, GitHub Actions, NGINX, Prometheus/Grafana

- **Backend:** FastAPI (Python 3.11), SQLAlchemy 2.0, Pydantic v2, Celery- Observabilidad IA: Arize Phoenix (OTLP)

- **ML/AI:** SpaCy, Sentence-BERT, Scikit-learn, PyTorch, LIME/SHAP, Tesseract

- **Datos:** PostgreSQL, Qdrant, Redis, MinIO (S3)---

- **DevOps:** Docker Compose, GitHub Actions, NGINX, Prometheus/Grafana

- **Observabilidad:** Arize Phoenix (OTLP)## 🚀 Inicio Rápido



---```bash

# 1) Clonar

## 🚀 Inicio Rápidogit clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA.git

cd Sistema-Corporativo-Documental-con-Capacidades-de-IA

```bash

# 1) Clonar# 2) Variables de entorno

git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA.gitcp .env.example .env

cd Sistema-Corporativo-Documental-con-Capacidades-de-IA# Edita .env (OPENAI_API_KEY y demás)



# 2) Variables de entorno# 3) Levantar servicios

cp .env.example .envdocker-compose up -d

# Edita .env (OPENAI_API_KEY y demas)

# 4) Acceso

# 3) Levantar servicios# Frontend:  http://localhost:3000

docker-compose up -d# Backend:   http://localhost:8000/docs

# Phoenix:   http://localhost:6006

# 4) Acceso```

# Frontend:  http://localhost:3000

# Backend:   http://localhost:8000/docsModo desarrollo (opcional):

# Phoenix:   http://localhost:6006

``````bash

# Backend

**Modo desarrollo (opcional):**cd backend

python -m venv venv

```bashvenv\Scripts\activate  # Windows

# Backendpip install -r requirements.txt

cd backenduvicorn main:app --reload

python -m venv venv

venv\Scripts\activate  # Windows# Frontend (otra terminal)

pip install -r requirements.txtcd frontend

uvicorn main:app --reloadnpm install

npm run dev

# Frontend (otra terminal)```

cd frontend

npm installCredenciales demo: usuario admin.demo / password Demo2025!

npm run dev

```---



**Credenciales demo:** `admin.demo` / `Demo2025!`## 🔒 Seguridad y Compliance



---- OAuth2 + JWT + MFA, RBAC granular, TLS 1.3

- Auditoría completa y DLP (detección de datos sensibles)

## 🔒 Seguridad y Compliance- DPIA completo y alineamiento con EU AI Act y GDPR



- **Autenticación:** OAuth2 + JWT + MFA---

- **Autorización:** RBAC granular

- **Encriptación:** TLS 1.3, AES-256## � Documentación completa

- **Auditoría:** Logs inmutables con retención 2+ años

- **DLP:** Detección automática de datos sensibles- docs/ARCHITECTURE.md – Arquitectura técnica

- **Compliance:** EU AI Act, GDPR, NIS2- docs/ADMIN_GUIDE.md – Guía de administración

- docs/USER_GUIDE.md – Manual de usuario

---- docs/API_REFERENCE.md – Referencia API



## 📚 Documentación completa---



| Documento | Descripción |## 🧪 Calidad y CI/CD

|-----------|-------------|

| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitectura técnica detallada |- Tests unitarios e integración (coverage 90%)

| [docs/ADMIN_GUIDE.md](docs/ADMIN_GUIDE.md) | Guía para administradores |- GitHub Actions: build, tests, análisis seguridad y despliegue

| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | Manual de usuario |

| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | Referencia API |---

| [docs/GOVERNANCE.md](docs/GOVERNANCE.md) | Gobernanza de IA |

| [docs/DPIA.md](docs/DPIA.md) | Data Protection Impact Assessment |## 👥 Equipo



---- Lead Developer: @rjamoriz

- Arquitectura y ML: Equipo IA / Seguridad

## 🧪 Calidad y CI/CD

---

- **Tests:** 78 tests unitarios + integración (coverage 90%)

- **CI/CD:** GitHub Actions (build, tests, security scan, deploy)© 2024-2025 TeFinancia S.A. – Uso propietario

- **Análisis de seguridad:** Dependabot, Trivy

git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA.git    Rel(admin, dms, "Administra", "HTTPS")docker-compose -f docker-compose.hub.yml up -d

---

cd Sistema-Corporativo-Documental-con-Capacidades-de-IA

## 👥 Equipo

    Rel(dms, sharepoint, "Sincroniza", "Microsoft Graph")

- **Lead Developer:** [@rjamoriz](https://github.com/rjamoriz)

- **Arquitectura y ML:** Equipo IA / Seguridad# 2. Configurar variables de entorno



---cp .env.example .env    Rel(dms, sap, "Importa", "GraphQL")# 4. Acceder a la aplicación



© 2024-2025 TeFinancia S.A. – Uso propietarionano .env  # Añadir OPENAI_API_KEY


    Rel(dms, ofac, "Valida", "REST API")# Frontend: http://localhost:3000

# 3. Desplegar con Docker Compose

docker-compose up -d    Rel(dms, openai, "Procesa", "REST API")# Backend API: http://localhost:8000/docs



# 4. Acceder a la aplicación    Rel(dms, phoenix, "Monitoriza", "OpenTelemetry")# Phoenix (Observability): http://localhost:6006

# Frontend:     http://localhost:3000

# Backend API:  http://localhost:8000/docs    ```

# Phoenix:      http://localhost:6006

```    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")



### Opción B: Desarrollo Local```📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)



```bash

# Backend

cd backend### 🔍 Vista de Contenedores C4 (Level 2 - Container Diagram)### Opción B: Build Local (Desarrollo)

python -m venv venv

source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload```mermaid```bash



# Frontend (terminal separado)C4Container# 1. Clonar repositorio

cd frontend

npm install    title Sistema Documental IA - Arquitectura de Contenedoresgit clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

npm run dev

```    cd Sistema-Corporativo-Documental-con-Capacidades-de-IA



**Credenciales Demo:**    Person(user, "Usuario", "Interactúa con el sistema")

- Usuario: `admin.demo`

- Password: `Demo2025!`    # 2. Setup automático (instala todo)



---    Container_Boundary(frontend, "Frontend Layer") {./scripts/setup.sh



## 📊 Dashboard y Métricas        Container(web, "React SPA", "TypeScript, Vite", "UI interactiva con dashboards")



### Métricas Clave    }# 3. Iniciar sistema completo



```mermaid    ./scripts/start.sh

graph LR

    A[📈 Documentos<br/>Procesados] -->|Real-time| D[Dashboard<br/>Central]    Container_Boundary(backend, "Backend Layer") {

    B[⚠️ Alertas<br/>de Riesgo] --> D

    C[✅ Compliance<br/>Score] --> D        Container(api, "FastAPI Backend", "Python 3.11", "API REST + GraphQL")# 4. Iniciar aplicación

    D --> E[📊 Visualizaciones]

    D --> F[📧 Notificaciones]        Container(ml, "ML Pipeline", "Scikit-learn, PyTorch", "Modelos de IA")# Terminal 1 - Backend:

    D --> G[📄 Reportes PDF]

            Container(workers, "Celery Workers", "Python", "Procesamiento asíncrono")cd backend && source venv/bin/activate && uvicorn main:app --reload

    style D fill:#4CAF50,color:#fff

```    }



**Disponibles:**    # Terminal 2 - Frontend:

- 📊 Tasa de procesamiento: docs/hora

- ⚡ Tiempo medio respuesta API    Container_Boundary(data, "Data Layer") {cd frontend && npm run dev

- 🎯 Precisión clasificación ML

- 🛡️ Incidencias compliance        ContainerDb(postgres, "PostgreSQL", "Base de datos relacional")

- 🚀 Aceleración GPU vs CPU

        ContainerDb(vector, "Qdrant", "Vector DB para embeddings")# 5. Acceder a la aplicación

---

        ContainerDb(redis, "Redis", "Cache y message broker")# Frontend: http://localhost:3000

## 🔐 Seguridad y Cumplimiento

        ContainerDb(minio, "MinIO", "Object storage (S3-compatible)")# Backend API: http://localhost:8000/docs

### Medidas de Seguridad

    }```

| Categoría | Implementación | Estado |

|-----------|---------------|--------|    

| **Autenticación** | OAuth2 + JWT + MFA | ✅ |

| **Autorización** | RBAC granular | ✅ |    Rel(user, web, "Usa", "HTTPS")📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

| **Encriptación** | TLS 1.3 + AES-256 | ✅ |

| **Auditoría** | Logs inmutables | ✅ |    Rel(web, api, "Llama", "REST/GraphQL")

| **Backup** | Incremental + Geo-redundancia | ✅ |

| **DLP** | Detección datos sensibles | ✅ |    Rel(api, ml, "Procesa", "Internal")---

| **Vulnerability Scan** | Dependabot + Trivy | ✅ |

    Rel(api, workers, "Encola", "Celery")

### Niveles de Riesgo EU AI Act

    Rel(api, postgres, "Lee/Escribe", "SQLAlchemy")## 📁 Documentación Principal

```mermaid

pie title Distribución Casos de Uso por Nivel de Riesgo    Rel(ml, vector, "Almacena embeddings", "gRPC")

    "Mínimo" : 45

    "Limitado" : 30    Rel(workers, redis, "Pub/Sub", "Redis Protocol")- 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU

    "Alto" : 20

    "Inaceptable" : 5    Rel(api, minio, "Almacena archivos", "S3 API")- 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)

```

```- 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)

---

- 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub

## 🧪 Testing y Calidad

### ⚙️ Arquitectura de Microservicios y Flujos- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)

### Pipeline CI/CD

- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)

```mermaid

graph TD```mermaid- 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)

    A[Code Push] --> B{GitHub Actions}

    B --> C[Unit Tests]graph TB- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix

    B --> D[Integration Tests]

    B --> E[E2E Tests]    subgraph "Frontend - React SPA"- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada

    

    C --> F{Coverage > 90%?}        UI[React UI Layer]- 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales

    D --> F

    E --> F        RT[React Router]- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema

    

    F -->|Sí| G[Security Scan]        TQ[TanStack Query]- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders

    F -->|No| H[❌ Build Failed]

            Z[Zustand State]- ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

    G --> I{Vulnerabilities?}

    I -->|No| J[Docker Build]    end

    I -->|Sí| H

        ![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)

    J --> K[🚀 Deploy Production]

        subgraph "API Gateway"![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)

    style K fill:#4CAF50,color:#fff

    style H fill:#f44336,color:#fff        NGINX[NGINX + SSL]![Completado](https://img.shields.io/badge/Completado-100%25-success)

```

        AUTH[Auth Middleware]![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)

**Cobertura:**

- ✅ Backend: 92% (78 tests)        RATE[Rate Limiter]![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)

- ✅ Frontend: 87% (45 tests)

- ✅ E2E: 15 escenarios críticos    end![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)



---    ![Coverage](https://img.shields.io/badge/Coverage-90%25-green)



## 📚 Documentación Completa    subgraph "Backend Services"![Python](https://img.shields.io/badge/Python-3.11+-green)



| Documento | Descripción | Palabras |        API[FastAPI Main]![React](https://img.shields.io/badge/React-18.3-blue)

|-----------|-------------|----------|

| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arquitectura técnica detallada | 6,000 |        DOC[Document Service]![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)

| [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) | Gobernanza de IA y compliance | 8,500 |

| [`docs/DPIA.md`](docs/DPIA.md) | Data Protection Impact Assessment | 7,000 |        CLS[Classification Service]![License](https://img.shields.io/badge/License-Proprietary-red)

| [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) | Guía para administradores | 4,500 |

| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | Manual de usuario final | 5,000 |        RAG[RAG Service]

| [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) | Referencia completa API | 3,000 |

        VAL[Validation Service]---

---

        RISK[Risk Scoring]

## 🐳 Despliegue con Docker

    end## 📋 Descripción del Proyecto

### Stack de Servicios

    

| Servicio | Puerto | Descripción |

|----------|--------|-------------|    subgraph "ML/AI Pipeline"Sistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.

| `frontend` | 3000 | React SPA con Vite |

| `backend` | 8000 | FastAPI + Uvicorn |        OCR[OCR Engine<br/>Tesseract/PaddleOCR]

| `postgres` | 5432 | Base de datos principal |

| `qdrant` | 6333 | Vector database |        NER[NER Model<br/>SpaCy]**Cliente:** TeFinancia S.A.  

| `redis` | 6379 | Cache y message broker |

| `minio` | 9000 | Object storage (S3) |        EMB[Embeddings<br/>OpenAI/SentenceBERT]**Proyecto:** FinancIA 2030  

| `phoenix` | 6006 | LLM observability |

| `nginx` | 80/443 | Reverse proxy + SSL |        CLF[Classifier<br/>Random Forest]**Estado:** ✅ **100% RFP COVERAGE ACHIEVED** 🎉 - Production Ready



### Comandos Útiles        XAI[Explainability<br/>LIME/SHAP]



```bash    end### 🎯 Sprint 6 - Completado

# Ver logs en tiempo real

docker-compose logs -f backend    



# Reiniciar servicio    subgraph "Async Workers"✅ **Enhanced Document Viewer** - Visor PDF avanzado con zoom, rotación, thumbnails  

docker-compose restart backend

        CEL[Celery]✅ **Annotation System** - Sistema colaborativo de anotaciones con Canvas overlay  

# Escalar workers

docker-compose up -d --scale celery-worker=4        W1[Document Processor]✅ **Document Comparison** - Comparación lado a lado de versiones con sync scroll  



# Backup de base de datos        W2[ML Inference]✅ **GraphQL API** - API completa con SharePoint y SAP DMS connectors  

docker-compose exec postgres pg_dump -U dms > backup.sql

```        W3[Batch Jobs]✅ **100% RFP Coverage** - Todos los requisitos implementados



---    end



## 🎯 Casos de Uso    ### 🎯 Objetivos Clave Alcanzados



### 1. 📄 Procesamiento Automático de Contratos    subgraph "Data Stores"



```python        PG[(PostgreSQL<br/>Metadata)]- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato

import requests

        QD[(Qdrant<br/>Vectors)]- ✅ **Validación automatizada** contra listas de sanciones (OFAC, EU, World Bank)

response = requests.post(

    "http://localhost:8000/api/v1/documents/upload",        RD[(Redis<br/>Cache)]- ✅ **IA Responsable** con explicabilidad y supervisión humana

    files={"file": open("contrato.pdf", "rb")},

    headers={"Authorization": f"Bearer {token}"}        MN[(MinIO<br/>Files)]- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)

)

    end- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)

document_id = response.json()["document_id"]

# → { "status": "completed", "risk_score": 0.23, "entities": [...] }    - ✅ **Seguridad por diseño** con auditoría completa

```

    subgraph "External APIs"

### 2. 🔍 Búsqueda Semántica con RAG

        OFAC[OFAC API]---

```python

results = requests.post(        OPENAI[OpenAI GPT-4]

    "/api/v1/search/hybrid",

    json={        PHX[Arize Phoenix]## 🚀 Inicio Rápido

        "query": "clausulas de confidencialidad en contratos 2024",

        "filters": {"document_type": "contract", "year": 2024},    end

        "limit": 10

    }    ¿Quieres probar el sistema? Tienes **dos opciones**:

).json()

    UI --> NGINX

for result in results:

    print(f"📄 {result['title']}")    NGINX --> AUTH --> RATE --> API### Opción A: Docker Hub (Recomendado - Más Rápido) 🐳

    print(f"📍 Fuente: {result['citation']}")

    print(f"🎯 Relevancia: {result['score']}")    

```

    API --> DOC --> W1```bash

---

    API --> CLS --> CLF# 1. Clonar repositorio

## 🚦 Roadmap 2025-2026

    API --> RAG --> EMBgit clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

```mermaid

timeline    API --> VAL --> OFACcd Sistema-Corporativo-Documental-con-Capacidades-de-IA/infrastructure/docker

    title Roadmap Sistema DMS IA

        API --> RISK --> XAI

    Q1 2025 : MVP Production Ready

            : 100% RFP Coverage    # 2. Configurar variables de entorno

            : GPU Acceleration

                DOC --> OCR --> NERcp .env.example .env

    Q2 2025 : Multi-idioma (ES/EN/FR)

            : Fine-tuning modelos propios    EMB --> OPENAI# Editar .env con tu OPENAI_API_KEY y otras credenciales

            

    Q3 2025 : Integración Azure/AWS    EMB --> QD

            : Mobile app React Native

                # 3. Desplegar con imágenes pre-construidas desde Docker Hub

    Q4 2025 : IA Generativa avanzada

            : Predicción riesgos ML    W1 --> CEL --> RDdocker-compose -f docker-compose.hub.yml up -d

            

    Q1 2026 : Expansión internacional    W2 --> CEL

            : ISO 27001

```    W3 --> CEL# 4. Acceder a la aplicación



---    # Frontend: http://localhost:3000



## 🎨 Visualizaciones Avanzadas    DOC --> PG# Backend API: http://localhost:8000/docs



### 📊 Diagramas Auto-generados con Kroki    DOC --> MN# Phoenix (Observability): http://localhost:6006



Este proyecto usa **GitHub Actions** para auto-generar diagramas arquitectónicos:    RAG --> QD```



- 🏛️ **PlantUML C4 Model** → Ver [`docs/diagrams/c4-context.puml`](docs/diagrams/c4-context.puml)    API --> RD

- 📐 **Structurizr DSL** → Ver [`docs/diagrams/workspace.dsl`](docs/diagrams/workspace.dsl)

- 🔄 **Auto-generación CI/CD** → Ver [`.github/workflows/diagrams.yml`](.github/workflows/diagrams.yml)    📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)



**Herramientas utilizadas:**    API -.Observability.-> PHX

- [Mermaid](https://mermaid.js.org/) - Diagramas en Markdown

- [Structurizr](https://structurizr.com/) - C4 Model DSL    ### Opción B: Build Local (Desarrollo)

- [Kroki](https://kroki.io/) - Generación automática

- [PlantUML](https://plantuml.com/) - Diagramas UML    style UI fill:#61DAFB,stroke:#333,stroke-width:2px



---    style API fill:#009688,stroke:#333,stroke-width:2px```bash



## 🤝 Contribución y Soporte    style OCR fill:#FF6B6B,stroke:#333,stroke-width:2px# 1. Clonar repositorio



### Equipo de Desarrollo    style EMB fill:#FFD93D,stroke:#333,stroke-width:2pxgit clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA



- 👨‍💻 **Lead Developer**: [@rjamoriz](https://github.com/rjamoriz)    style PG fill:#336791,stroke:#333,stroke-width:2px,color:#fffcd Sistema-Corporativo-Documental-con-Capacidades-de-IA

- 🏛️ **Arquitecto**: Roberto Amoriz

- 🤖 **ML Engineer**: Equipo IA    style QD fill:#DC477D,stroke:#333,stroke-width:2px,color:#fff



### Reportar Issues```# 2. Setup automático (instala todo)



```markdown./scripts/setup.sh

**Descripción**: Breve descripción del error

**Pasos para reproducir**: ### 🌊 Flujo de Procesamiento de Documentos

1. Ir a...

2. Hacer clic en...# 3. Iniciar sistema completo

3. Ver error

```mermaid./scripts/start.sh

**Entorno**: 

- OS: Windows 11 / Ubuntu 22.04sequenceDiagram

- Docker: 24.0.5

- Navegador: Chrome 120    autonumber# 4. Iniciar aplicación

```

    actor Usuario# Terminal 1 - Backend:

---

    participant UI as React Frontendcd backend && source venv/bin/activate && uvicorn main:app --reload

## 📜 Licencia

    participant API as FastAPI Backend

```

Copyright © 2024-2025 TeFinancia S.A. - Proyecto FinancIA 2030    participant Val as Validation Service# Terminal 2 - Frontend:

Licencia: Propietaria - Uso exclusivo cliente

```    participant ML as ML Pipelinecd frontend && npm run dev



---    participant VDB as Qdrant (Vectors)



## 🎓 Referencias    participant DB as PostgreSQL# 5. Acceder a la aplicación



### Frameworks Principales    participant S3 as MinIO (S3)# Frontend: http://localhost:3000



- **Frontend**: [React](https://react.dev/) | [TypeScript](https://www.typescriptlang.org/) | [Vite](https://vitejs.dev/)    participant OFAC as OFAC API# Backend API: http://localhost:8000/docs

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) | [SQLAlchemy](https://www.sqlalchemy.org/)

- **ML/AI**: [OpenAI](https://openai.com/) | [Sentence-Transformers](https://www.sbert.net/) | [SpaCy](https://spacy.io/)    ```

- **Databases**: [PostgreSQL](https://www.postgresql.org/) | [Qdrant](https://qdrant.tech/) | [Redis](https://redis.io/)

    Usuario->>UI: Sube documento PDF

### Normativas Compliance

    UI->>API: POST /documents/upload📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

- [EU AI Act](https://artificialintelligenceact.eu/) - Regulación IA Europea

- [GDPR](https://gdpr.eu/) - Protección de Datos (EU)    API->>Val: Valida archivo (tamaño, tipo, malware)

- [NIS2](https://www.enisa.europa.eu/topics/nis-directive) - Ciberseguridad

- [OFAC](https://ofac.treasury.gov/) - Sanciones USA    Val-->>API: ✅ Válido---



---    



<div align="center">    API->>S3: Almacena archivo original## 📁 Documentación Principal



**🚀 Sistema Corporativo Documental con IA - FinancIA 2030**    S3-->>API: file_id, url



Made with ❤️ by [Roberto Amoriz](https://github.com/rjamoriz)    - 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU



[![GitHub](https://img.shields.io/badge/GitHub-rjamoriz-181717?logo=github)](https://github.com/rjamoriz)    API->>DB: Crea registro metadata- 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin)](https://linkedin.com/in/rjamoriz)

    DB-->>API: document_id- 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)

[⬆️ Volver arriba](#-sistema-corporativo-documental-con-capacidades-de-ia)

    - 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub

</div>

    API->>ML: Encola procesamiento asíncrono- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)

    activate ML- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)

    - 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)

    ML->>ML: OCR extracción texto- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix

    ML->>ML: NER extrae entidades- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada

    ML->>ML: Clasificación automática- 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales

    ML->>VDB: Genera y almacena embeddings- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema

    VDB-->>ML: vector_id- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders

    - ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

    ML->>OFAC: Valida entidades contra sanciones

    OFAC-->>ML: validation_result![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)

    ![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)

    ML->>ML: Score de riesgo + explicabilidad![Completado](https://img.shields.io/badge/Completado-100%25-success)

    ML->>DB: Actualiza documento procesado![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)

    ![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)

    deactivate ML![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)

    ![Coverage](https://img.shields.io/badge/Coverage-90%25-green)

    DB-->>API: Documento listo![Python](https://img.shields.io/badge/Python-3.11+-green)

    API-->>UI: Notificación WebSocket![React](https://img.shields.io/badge/React-18.3-blue)

    UI-->>Usuario: 🎉 Documento procesado!![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)

```![License](https://img.shields.io/badge/License-Proprietary-red)



### 🎯 Stack Tecnológico Detallado---



```mermaid## 📋 Descripción del Proyecto

mindmap

  root((Sistema DMS IA))Sistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.

    Frontend

      React 18.3**Cliente:** TeFinancia S.A.  

      TypeScript 5.5**Proyecto:** FinancIA 2030  

      Vite**Estado:** ✅ **100% RFP COVERAGE ACHIEVED** 🎉 - Production Ready

      TanStack Query

      Zustand### 🎯 Sprint 6 - Completado

      Tailwind CSS

      Recharts✅ **Enhanced Document Viewer** - Visor PDF avanzado con zoom, rotación, thumbnails  

    Backend✅ **Annotation System** - Sistema colaborativo de anotaciones con Canvas overlay  

      FastAPI✅ **Document Comparison** - Comparación lado a lado de versiones con sync scroll  

      Python 3.11✅ **GraphQL API** - API completa con SharePoint y SAP DMS connectors  

      SQLAlchemy 2.0✅ **100% RFP Coverage** - Todos los requisitos implementados

      Pydantic V2

      Celery### 🎯 Objetivos Clave Alcanzados

      GraphQL Strawberry

    ML/AI- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato

      OpenAI GPT-4- ✅ **Validación automatizada** contra listas de sanciones (OFAC, EU, World Bank)

      Sentence-BERT- ✅ **IA Responsable** con explicabilidad y supervisión humana

      SpaCy NER- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)

      Scikit-learn- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)

      PyTorch- ✅ **Seguridad por diseño** con auditoría completa

      LIME/SHAP

      Tesseract OCR---

    Databases

      PostgreSQL 15## 🚀 Inicio Rápido

      Qdrant Vector DB

      Redis 7¿Quieres probar el sistema? Tienes **dos opciones**:

      MinIO S3

    DevOps### Opción A: Docker Hub (Recomendado - Más Rápido) 🐳

      Docker Compose

      GitHub Actions```bash

      NGINX# 1. Clonar repositorio

      Let's Encryptgit clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

      Prometheuscd Sistema-Corporativo-Documental-con-Capacidades-de-IA/infrastructure/docker

      Grafana

    GPU Acceleration# 2. Configurar variables de entorno

      CUDA 12.1cp .env.example .env

      cuDNN 8.9# Editar .env con tu OPENAI_API_KEY y otras credenciales

      NVIDIA Driver 537+

      PyTorch GPU# 3. Desplegar con imágenes pre-construidas desde Docker Hub

    Compliancedocker-compose -f docker-compose.hub.yml up -d

      EU AI Act

      GDPR# 4. Acceder a la aplicación

      NIS2# Frontend: http://localhost:3000

      OFAC/AML# Backend API: http://localhost:8000/docs

```# Phoenix (Observability): http://localhost:6006

```

### 🚀 Flujo CI/CD y Deployment

📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)

```mermaid

gitGraph### Opción B: Build Local (Desarrollo)

    commit id: "Initial commit"

    branch develop```bash

    checkout develop# 1. Clonar repositorio

    commit id: "Feature: RAG system"git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

    commit id: "Feature: Risk scoring"cd Sistema-Corporativo-Documental-con-Capacidades-de-IA

    branch feature/gpu-acceleration

    checkout feature/gpu-acceleration# 2. Setup automático (instala todo)

    commit id: "Add GPU support"./scripts/setup.sh

    commit id: "Optimize embeddings"

    checkout develop# 3. Iniciar sistema completo

    merge feature/gpu-acceleration tag: "v0.9"./scripts/start.sh

    commit id: "Tests passed ✅"

    checkout main# 4. Iniciar aplicación

    merge develop tag: "v1.0.0 🚀"# Terminal 1 - Backend:

    commit id: "Production deploy"cd backend && source venv/bin/activate && uvicorn main:app --reload

```

# Terminal 2 - Frontend:

---cd frontend && npm run dev



## 🚀 Inicio Rápido# 5. Acceder a la aplicación

# Frontend: http://localhost:3000

### Opción A: Docker Compose (Recomendado) 🐳# Backend API: http://localhost:8000/docs

```

```bash

# 1. Clonar repositorio📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA.git

cd Sistema-Corporativo-Documental-con-Capacidades-de-IA---



# 2. Configurar variables de entorno## 📁 Documentación Principal

cp .env.example .env

nano .env  # Añadir OPENAI_API_KEY y otros secretos- 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU

- 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)

# 3. Desplegar con Docker Compose- 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)

docker-compose up -d- 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub

- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)

# 4. Verificar servicios- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)

docker-compose ps- 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)

- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix

# 5. Acceder a la aplicación- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada

# Frontend:     http://localhost:3000- 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales

# Backend API:  http://localhost:8000/docs- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema

# Phoenix:      http://localhost:6006- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders

# Qdrant:       http://localhost:6333/dashboard- ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

```

![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)

### Opción B: Docker Hub (Imágenes Pre-construidas) 🎯![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)

![Completado](https://img.shields.io/badge/Completado-100%25-success)

```bash![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)

# Usar imágenes desde Docker Hub![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)

docker-compose -f docker-compose.hub.yml up -d![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)

![Coverage](https://img.shields.io/badge/Coverage-90%25-green)

# Login demo![Python](https://img.shields.io/badge/Python-3.11+-green)

Usuario: admin.demo![React](https://img.shields.io/badge/React-18.3-blue)

Password: Demo2025!![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)

```![License](https://img.shields.io/badge/License-Proprietary-red)



### Opción C: Desarrollo Local---



```bash## 📋 Descripción del Proyecto

# Backend

cd backendSistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.

python -m venv venv

source venv/bin/activate  # En Windows: venv\Scripts\activate**Cliente:** TeFinancia S.A.  

pip install -r requirements.txt**Proyecto:** FinancIA 2030  

uvicorn main:app --reload**Estado:** ✅ **100% RFP COVERAGE ACHIEVED** 🎉 - Production Ready



# Frontend (terminal separado)### 🎯 Sprint 6 - Completado

cd frontend

npm install✅ **Enhanced Document Viewer** - Visor PDF avanzado con zoom, rotación, thumbnails  

npm run dev✅ **Annotation System** - Sistema colaborativo de anotaciones con Canvas overlay  

```✅ **Document Comparison** - Comparación lado a lado de versiones con sync scroll  

✅ **GraphQL API** - API completa con SharePoint y SAP DMS connectors  

---✅ **100% RFP Coverage** - Todos los requisitos implementados



## 📊 Dashboard y Métricas### 🎯 Objetivos Clave Alcanzados



### Panel de Control Principal- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato

- ✅ **Validación automatizada** contra listas de sanciones (OFAC, EU, World Bank)

```mermaid- ✅ **IA Responsable** con explicabilidad y supervisión humana

graph LR- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)

    subgraph "Dashboard Analytics"- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)

        A[📈 Documentos Procesados] -->|Real-time| D[Dashboard]- ✅ **Seguridad por diseño** con auditoría completa

        B[⚠️ Alertas de Riesgo] --> D

        C[✅ Compliance Score] --> D---

        D --> E[📊 Visualizaciones]

        D --> F[📧 Notificaciones]## 🚀 Inicio Rápido

        D --> G[📄 Reportes PDF]

    end¿Quieres probar el sistema? Tienes **dos opciones**:

    

    style D fill:#4CAF50,stroke:#333,stroke-width:3px,color:#fff### Opción A: Docker Hub (Recomendado - Más Rápido) 🐳

```

```bash

**Métricas Clave Disponibles:**# 1. Clonar repositorio

- 📊 Tasa de procesamiento: docs/horagit clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

- ⚡ Tiempo medio de respuesta APIcd Sistema-Corporativo-Documental-con-Capacidades-de-IA/infrastructure/docker

- 🎯 Precisión de clasificación ML

- 🛡️ Incidencias de cumplimiento detectadas# 2. Configurar variables de entorno

- 💾 Uso de almacenamiento y crecimientocp .env.example .env

- 🚀 Aceleración GPU vs CPU# Editar .env con tu OPENAI_API_KEY y otras credenciales



---# 3. Desplegar con imágenes pre-construidas desde Docker Hub

docker-compose -f docker-compose.hub.yml up -d

## 🔐 Seguridad y Cumplimiento

# 4. Acceder a la aplicación

### Niveles de Riesgo EU AI Act# Frontend: http://localhost:3000

# Backend API: http://localhost:8000/docs

```mermaid# Phoenix (Observability): http://localhost:6006

pie title Distribución Casos de Uso por Nivel de Riesgo```

    "Mínimo" : 45

    "Limitado" : 30📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)

    "Alto" : 20

    "Inaceptable" : 5### Opción B: Build Local (Desarrollo)

```

```bash

### Medidas de Seguridad Implementadas# 1. Clonar repositorio

git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

| Categoría | Implementación | Estado |cd Sistema-Corporativo-Documental-con-Capacidades-de-IA

|-----------|---------------|--------|

| **Autenticación** | OAuth2 + JWT + MFA | ✅ |# 2. Setup automático (instala todo)

| **Autorización** | RBAC granular | ✅ |./scripts/setup.sh

| **Encriptación** | TLS 1.3 + AES-256 | ✅ |

| **Auditoría** | Logs inmutables + Blockchain ready | ✅ |# 3. Iniciar sistema completo

| **Backup** | Incremental diario + Geo-redundancia | ✅ |./scripts/start.sh

| **DLP** | Detección de datos sensibles | ✅ |

| **Vulnerability Scan** | Dependabot + Trivy | ✅ |# 4. Iniciar aplicación

| **SIEM** | Integración con Splunk/ELK | ✅ |# Terminal 1 - Backend:

cd backend && source venv/bin/activate && uvicorn main:app --reload

---

# Terminal 2 - Frontend:

## 🧪 Testing y Calidadcd frontend && npm run dev



```mermaid# 5. Acceder a la aplicación

graph TD# Frontend: http://localhost:3000

    A[Code Push] --> B{GitHub Actions}# Backend API: http://localhost:8000/docs

    B --> C[Unit Tests]```

    B --> D[Integration Tests]

    B --> E[E2E Tests]📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

    

    C --> F{Coverage > 90%?}---

    D --> F

    E --> F## 📁 Documentación Principal

    

    F -->|Sí| G[Security Scan]- 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU

    F -->|No| H[❌ Build Failed]- 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)

    - 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)

    G --> I{Vulnerabilities?}- 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub

    I -->|No| J[Docker Build]- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)

    I -->|Sí| H- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)

    - 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)

    J --> K[Push to Registry]- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix

    K --> L[Deploy Staging]- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada

    L --> M{QA Approval?}- 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales

    M -->|Sí| N[🚀 Deploy Production]- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema

    M -->|No| H- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders

    - ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

    style N fill:#4CAF50,color:#fff

    style H fill:#f44336,color:#fff![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)

```![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)

![Completado](https://img.shields.io/badge/Completado-100%25-success)

**Cobertura de Tests:**![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)

- ✅ Backend: 92% (78 tests)![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)

- ✅ Frontend: 87% (45 tests)![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)

- ✅ E2E: 15 escenarios críticos![Coverage](https://img.shields.io/badge/Coverage-90%25-green)

- ✅ Load Testing: 1000 req/s sostenidos![Python](https://img.shields.io/badge/Python-3.11+-green)

![React](https://img.shields.io/badge/React-18.3-blue)

---![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)

![License](https://img.shields.io/badge/License-Proprietary-red)

## 📚 Documentación Completa

---

| Documento | Descripción | Palabras |

|-----------|-------------|----------|## 📋 Descripción del Proyecto

| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arquitectura técnica detallada | 6,000 |

| [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) | Gobernanza de IA y compliance | 8,500 |Sistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.

| [`docs/DPIA.md`](docs/DPIA.md) | Data Protection Impact Assessment | 7,000 |

| [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) | Guía para administradores | 4,500 |**Cliente:** TeFinancia S.A.  

| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | Manual de usuario final | 5,000 |**Proyecto:** FinancIA 2030  

| [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) | Referencia completa API | 3,000 |**Estado:** ✅ **100% RFP COVERAGE ACHIEVED** 🎉 - Production Ready

| [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md) | Guía de despliegue producción | 4,000 |

| [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) | Script para demos a clientes | 2,500 |### 🎯 Sprint 6 - Completado



---✅ **Enhanced Document Viewer** - Visor PDF avanzado con zoom, rotación, thumbnails  

✅ **Annotation System** - Sistema colaborativo de anotaciones con Canvas overlay  

## 🎨 Visualizaciones Avanzadas e Interactivas✅ **Document Comparison** - Comparación lado a lado de versiones con sync scroll  

✅ **GraphQL API** - API completa con SharePoint y SAP DMS connectors  

### 🌐 Dashboard Interactivo con D3.js✅ **100% RFP Coverage** - Todos los requisitos implementados



> **🔗 [Ver Dashboard Interactivo en Vivo](https://rjamoriz.github.io/sistema-dms-dashboard)**  ### 🎯 Objetivos Clave Alcanzados

> Visualización dinámica de arquitectura de microservicios con D3.js + React Flow

- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato

<details>- ✅ **Validación automatizada** contra listas de sanciones (OFAC, EU, World Bank)

<summary>📸 Preview del Dashboard Interactivo</summary>- ✅ **IA Responsable** con explicabilidad y supervisión humana

- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)

```- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)

┌─────────────────────────────────────────────────────────────┐- ✅ **Seguridad por diseño** con auditoría completa

│  🎯 Sistema DMS - Vista Interactiva de Servicios            │

├─────────────────────────────────────────────────────────────┤---

│                                                              │

│   [Frontend]  ━━━>  [API Gateway]  ━━━>  [Backend]         │## 🚀 Inicio Rápido

│       │                   │                    │             │

│       └───> Cache <───────┘                    │             │¿Quieres probar el sistema? Tienes **dos opciones**:

│                                                 ↓             │

│                                          [ML Pipeline]       │### Opción A: Docker Hub (Recomendado - Más Rápido) 🐳

│                                                 │             │

│                                                 ↓             │```bash

│                                    [PostgreSQL] [Qdrant]    │# 1. Clonar repositorio

│                                                              │git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

│  Nodos clickables | Métricas real-time | Rutas animadas    │cd Sistema-Corporativo-Documental-con-Capacidades-de-IA/infrastructure/docker

└─────────────────────────────────────────────────────────────┘

```# 2. Configurar variables de entorno

</details>cp .env.example .env

# Editar .env con tu OPENAI_API_KEY y otras credenciales

### 📊 Diagramas Generados Automáticamente

# 3. Desplegar con imágenes pre-construidas desde Docker Hub

Este proyecto usa **Kroki** para auto-generar diagramas desde código en cada commit:docker-compose -f docker-compose.hub.yml up -d



```yaml# 4. Acceder a la aplicación

# .github/workflows/diagrams.yml# Frontend: http://localhost:3000

name: Auto-generate Diagrams# Backend API: http://localhost:8000/docs

on: [push]# Phoenix (Observability): http://localhost:6006

jobs:```

  diagrams:

    runs-on: ubuntu-latest📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)

    steps:

      - uses: actions/checkout@v3### Opción B: Build Local (Desarrollo)

      - name: Generate with Kroki

        run: |```bash

          curl -X POST -H "Content-Type: text/plain" \# 1. Clonar repositorio

            --data-binary @architecture.puml \git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

            https://kroki.io/plantuml/svg > docs/architecture.svgcd Sistema-Corporativo-Documental-con-Capacidades-de-IA

```

# 2. Setup automático (instala todo)

### 🏛️ Structurizr C4 Model (DSL)./scripts/setup.sh



El modelo C4 completo está definido en código con **Structurizr DSL**:# 3. Iniciar sistema completo

./scripts/start.sh

```

workspace "Sistema DMS Corporativo" {# 4. Iniciar aplicación

    model {# Terminal 1 - Backend:

        user = person "Usuario Financiero"cd backend && source venv/bin/activate && uvicorn main:app --reload

        dmsSystem = softwareSystem "Sistema Documental IA" {

            webApp = container "React SPA"# Terminal 2 - Frontend:

            api = container "FastAPI Backend"cd frontend && npm run dev

            mlPipeline = container "ML Pipeline"

            database = container "PostgreSQL"# 5. Acceder a la aplicación

            vectorDB = container "Qdrant"# Frontend: http://localhost:3000

        }# Backend API: http://localhost:8000/docs

    }```

    views {

        systemContext dmsSystem {📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

            include *

            autolayout lr---

        }

    }## 📁 Documentación Principal

}

```- 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU

- 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)

> **🔗 [Ver Modelo C4 Completo](https://structurizr.com/share/YOUR_WORKSPACE_ID)**- 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)

- 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub

---- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)

- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)

## 🐳 Despliegue con Docker- 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)

- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix

### Stack de Servicios- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada

- 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales

| Servicio | Puerto | Descripción |- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema

|----------|--------|-------------|- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders

| `frontend` | 3000 | React SPA con Vite |- ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

| `backend` | 8000 | FastAPI + Uvicorn |

| `postgres` | 5432 | Base de datos principal |![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)

| `qdrant` | 6333 | Vector database |![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)

| `redis` | 6379 | Cache y message broker |![Completado](https://img.shields.io/badge/Completado-100%25-success)

| `minio` | 9000 | Object storage (S3) |![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)

| `phoenix` | 6006 | LLM observability |![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)

| `celery-worker` | - | Procesamiento asíncrono |![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)

| `celery-beat` | - | Scheduler de tareas |![Coverage](https://img.shields.io/badge/Coverage-90%25-green)

| `nginx` | 80/443 | Reverse proxy + SSL |![Python](https://img.shields.io/badge/Python-3.11+-green)

![React](https://img.shields.io/badge/React-18.3-blue)

### Comandos Útiles Docker![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)

![License](https://img.shields.io/badge/License-Proprietary-red)

```bash

# Ver logs en tiempo real---

docker-compose logs -f backend

## 📋 Descripción del Proyecto

# Reiniciar un servicio específico

docker-compose restart backendSistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.



# Escalar workers**Cliente:** TeFinancia S.A.  

docker-compose up -d --scale celery-worker=4**Proyecto:** FinancIA 2030  

**Estado:** ✅ **100% RFP COVERAGE ACHIEVED** 🎉 - Production Ready

# Backup de base de datos

docker-compose exec postgres pg_dump -U dms > backup.sql### 🎯 Sprint 6 - Completado



# Restaurar backup✅ **Enhanced Document Viewer** - Visor PDF avanzado con zoom, rotación, thumbnails  

docker-compose exec -T postgres psql -U dms < backup.sql✅ **Annotation System** - Sistema colaborativo de anotaciones con Canvas overlay  

✅ **Document Comparison** - Comparación lado a lado de versiones con sync scroll  

# Limpiar todo (¡CUIDADO!)✅ **GraphQL API** - API completa con SharePoint y SAP DMS connectors  

docker-compose down -v --remove-orphans✅ **100% RFP Coverage** - Todos los requisitos implementados

```

### 🎯 Objetivos Clave Alcanzados

---

- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato

## 🎯 Casos de Uso Implementados- ✅ **Validación automatizada** contra listas de sanciones (OFAC, EU, World Bank)

- ✅ **IA Responsable** con explicabilidad y supervisión humana

### 1. 📄 Procesamiento Automático de Contratos- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)

- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)

```python- ✅ **Seguridad por diseño** con auditoría completa

# Ejemplo de uso de la API

import requests---



response = requests.post(## 🚀 Inicio Rápido

    "http://localhost:8000/api/v1/documents/upload",

    files={"file": open("contrato.pdf", "rb")},¿Quieres probar el sistema? Tienes **dos opciones**:

    headers={"Authorization": f"Bearer {token}"}

)### Opción A: Docker Hub (Recomendado - Más Rápido) 🐳



document_id = response.json()["document_id"]```bash

# 1. Clonar repositorio

# Esperar procesamientogit clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

status = requests.get(f"/api/v1/documents/{document_id}/status")cd Sistema-Corporativo-Documental-con-Capacidades-de-IA/infrastructure/docker

# → { "status": "completed", "risk_score": 0.23, "entities": [...] }

```# 2. Configurar variables de entorno

cp .env.example .env

### 2. 🔍 Búsqueda Semántica con RAG# Editar .env con tu OPENAI_API_KEY y otras credenciales



```python# 3. Desplegar con imágenes pre-construidas desde Docker Hub

# Búsqueda híbrida (keyword + semantic)docker-compose -f docker-compose.hub.yml up -d

results = requests.post(

    "/api/v1/search/hybrid",# 4. Acceder a la aplicación

    json={# Frontend: http://localhost:3000

        "query": "clausulas de confidencialidad en contratos 2024",# Backend API: http://localhost:8000/docs

        "filters": {"document_type": "contract", "year": 2024},# Phoenix (Observability): http://localhost:6006

        "limit": 10```

    }

).json()📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)



# Resultado incluye citaciones exactas### Opción B: Build Local (Desarrollo)

for result in results:

    print(f"📄 {result['title']}")```bash

    print(f"📍 Fuente: {result['citation']}")  # Párrafo exacto citado# 1. Clonar repositorio

    print(f"🎯 Relevancia: {result['score']}")git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

```cd Sistema-Corporativo-Documental-con-Capacidades-de-IA



### 3. ⚖️ Análisis de Riesgo y Compliance# 2. Setup automático (instala todo)

./scripts/setup.sh

```python

# Verificar cumplimiento GDPR automáticamente# 3. Iniciar sistema completo

compliance = requests.post(./scripts/start.sh

    "/api/v1/compliance/check-gdpr",

    json={"document_id": document_id}# 4. Iniciar aplicación

).json()# Terminal 1 - Backend:

cd backend && source venv/bin/activate && uvicorn main:app --reload

print(f"Estado: {compliance['status']}")  # compliant | non_compliant

print(f"Artículos violados: {compliance['violations']}")# Terminal 2 - Frontend:

print(f"Recomendaciones: {compliance['recommendations']}")cd frontend && npm run dev

```

# 5. Acceder a la aplicación

---# Frontend: http://localhost:3000

# Backend API: http://localhost:8000/docs

## 🚦 Roadmap y Próximas Funcionalidades```



```mermaid📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

timeline

    title Roadmap 2025-2026---

    

    Q1 2025 : MVP Production Ready## 📁 Documentación Principal

            : 100% RFP Coverage

            : GPU Acceleration- 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU

            - 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)

    Q2 2025 : Multi-idioma (ES/EN/FR)- 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)

            : Fine-tuning modelos propios- 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub

            : Blockchain timestamping- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)

            - 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)

    Q3 2025 : Integración Azure/AWS- 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)

            : Federación identidades SSO- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix

            : Mobile app (React Native)- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada

            - 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales

    Q4 2025 : IA Generativa avanzada- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema

            : Auto-redacción clausulas- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders

            : Predicción riesgos ML- ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

            

    Q1 2026 : Expansión internacional![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)

            : SOC 2 Type II![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)

            : ISO 27001![Completado](https://img.shields.io/badge/Completado-100%25-success)

```![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)

![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)

---![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)

![Coverage](https://img.shields.io/badge/Coverage-90%25-green)

## 🤝 Contribución y Soporte![Python](https://img.shields.io/badge/Python-3.11+-green)

![React](https://img.shields.io/badge/React-18.3-blue)

### Equipo de Desarrollo![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)

![License](https://img.shields.io/badge/License-Proprietary-red)

- 👨‍💻 **Lead Developer**: [@rjamoriz](https://github.com/rjamoriz)

- 🏛️ **Arquitecto de Soluciones**: Roberto Amoriz---

- 🤖 **ML Engineer**: Equipo IA

- 🔒 **Security Lead**: Equipo Seguridad## 📋 Descripción del Proyecto



### Reportar IssuesSistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.



```bash**Cliente:** TeFinancia S.A.  

# Template para reportar bugs**Proyecto:** FinancIA 2030  

**Descripción**: Breve descripción del error**Estado:** ✅ **100% RFP COVERAGE ACHIEVED** 🎉 - Production Ready

**Pasos para reproducir**: 

1. Ir a...### 🎯 Sprint 6 - Completado

2. Hacer clic en...

3. Ver error✅ **Enhanced Document Viewer** - Visor PDF avanzado con zoom, rotación, thumbnails  

✅ **Annotation System** - Sistema colaborativo de anotaciones con Canvas overlay  

**Comportamiento esperado**: Qué debería suceder✅ **Document Comparison** - Comparación lado a lado de versiones con sync scroll  

**Comportamiento actual**: Qué sucede realmente✅ **GraphQL API** - API completa con SharePoint y SAP DMS connectors  

**Screenshots**: Si aplica✅ **100% RFP Coverage** - Todos los requisitos implementados

**Entorno**: 

- OS: Windows 11 / Ubuntu 22.04### 🎯 Objetivos Clave Alcanzados

- Docker: 24.0.5

- Navegador: Chrome 120- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato

```- ✅ **Validación automatizada** contra listas de sanciones (OFAC, EU, World Bank)

- ✅ **IA Responsable** con explicabilidad y supervisión humana

---- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)

- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)

## 📜 Licencia y Copyright- ✅ **Seguridad por diseño** con auditoría completa



```---

Copyright © 2024-2025 TeFinancia S.A. - Proyecto FinancIA 2030

Licencia: Propietaria - Uso exclusivo cliente## 🚀 Inicio Rápido



Este software es propiedad de TeFinancia S.A. y está protegido por ¿Quieres probar el sistema? Tienes **dos opciones**:

leyes de derechos de autor. Su uso, distribución o modificación sin 

autorización expresa está prohibida.### Opción A: Docker Hub (Recomendado - Más Rápido) 🐳

```

```bash

---# 1. Clonar repositorio

git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

## 🎓 Referencias y Tecnologíascd Sistema-Corporativo-Documental-con-Capacidades-de-IA/infrastructure/docker



### Frameworks y Librerías Principales# 2. Configurar variables de entorno

cp .env.example .env

- **Frontend**: [React](https://react.dev/) | [TypeScript](https://www.typescriptlang.org/) | [Vite](https://vitejs.dev/)# Editar .env con tu OPENAI_API_KEY y otras credenciales

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) | [SQLAlchemy](https://www.sqlalchemy.org/) | [Celery](https://docs.celeryproject.org/)

- **ML/AI**: [OpenAI](https://openai.com/) | [Sentence-Transformers](https://www.sbert.net/) | [SpaCy](https://spacy.io/)# 3. Desplegar con imágenes pre-construidas desde Docker Hub

- **Databases**: [PostgreSQL](https://www.postgresql.org/) | [Qdrant](https://qdrant.tech/) | [Redis](https://redis.io/)docker-compose -f docker-compose.hub.yml up -d

- **DevOps**: [Docker](https://www.docker.com/) | [GitHub Actions](https://github.com/features/actions) | [NGINX](https://nginx.org/)

# 4. Acceder a la aplicación

### Visualización de Arquitectura# Frontend: http://localhost:3000

# Backend API: http://localhost:8000/docs

- **Mermaid**: Diagramas en Markdown ([docs](https://mermaid.js.org/))# Phoenix (Observability): http://localhost:6006

- **Structurizr**: C4 Model DSL ([docs](https://structurizr.com/))```

- **Kroki**: Generación automática de diagramas ([docs](https://kroki.io/))

- **D3.js**: Visualizaciones interactivas ([docs](https://d3js.org/))📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)

- **React Flow**: Diagramas de flujo interactivos ([docs](https://reactflow.dev/))

### Opción B: Build Local (Desarrollo)

### Normativas y Compliance

```bash

- [EU AI Act](https://artificialintelligenceact.eu/) - Regulación IA Europea# 1. Clonar repositorio

- [GDPR](https://gdpr.eu/) - Protección de Datos (EU)git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

- [NIS2 Directive](https://www.enisa.europa.eu/topics/nis-directive) - Ciberseguridadcd Sistema-Corporativo-Documental-con-Capacidades-de-IA

- [OFAC Sanctions](https://ofac.treasury.gov/) - Lista sanciones USA

# 2. Setup automático (instala todo)

---./scripts/setup.sh



<div align="center"># 3. Iniciar sistema completo

./scripts/start.sh

**🚀 Sistema Corporativo Documental con IA - FinancIA 2030**

# 4. Iniciar aplicación

Made with ❤️ by [Roberto Amoriz](https://github.com/rjamoriz)# Terminal 1 - Backend:

cd backend && source venv/bin/activate && uvicorn main:app --reload

[![GitHub](https://img.shields.io/badge/GitHub-rjamoriz-181717?logo=github)](https://github.com/rjamoriz)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin)](https://linkedin.com/in/rjamoriz)# Terminal 2 - Frontend:

[![Email](https://img.shields.io/badge/Email-Contact-D14836?logo=gmail)](mailto:rjamoriz@example.com)cd frontend && npm run dev



[⬆️ Volver arriba](#-sistema-corporativo-documental-con-capacidades-de-ia)# 5. Acceder a la aplicación

# Frontend: http://localhost:3000

</div># Backend API: http://localhost:8000/docs

```

📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

---

## 📁 Documentación Principal

- 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU
- 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)
- 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)
- 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub
- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)
- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)
- 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)
- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix
- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada
- 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales
- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema
- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders
- ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)
![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)
![Completado](https://img.shields.io/badge/Completado-100%25-success)
![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)
![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)
![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-90%25-green)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18.3-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)

---

## 📋 Descripción del Proyecto

Sistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.

**Cliente:** TeFinancia S.A.  
**Proyecto:** FinancIA 2030  
**Estado:** ✅ **100% RFP COVERAGE ACHIEVED** 🎉 - Production Ready

### 🎯 Sprint 6 - Completado

✅ **Enhanced Document Viewer** - Visor PDF avanzado con zoom, rotación, thumbnails  
✅ **Annotation System** - Sistema colaborativo de anotaciones con Canvas overlay  
✅ **Document Comparison** - Comparación lado a lado de versiones con sync scroll  
✅ **GraphQL API** - API completa con SharePoint y SAP DMS connectors  
✅ **100% RFP Coverage** - Todos los requisitos implementados

### 🎯 Objetivos Clave Alcanzados

- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato
- ✅ **Validación automatizada** contra listas de sanciones (OFAC, EU, World Bank)
- ✅ **IA Responsable** con explicabilidad y supervisión humana
- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)
- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)
- ✅ **Seguridad por diseño** con auditoría completa

---

## 🚀 Inicio Rápido

¿Quieres probar el sistema? Tienes **dos opciones**:

### Opción A: Docker Hub (Recomendado - Más Rápido) 🐳

```bash
# 1. Clonar repositorio
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA/infrastructure/docker

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY y otras credenciales

# 3. Desplegar con imágenes pre-construidas desde Docker Hub
docker-compose -f docker-compose.hub.yml up -d

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Phoenix (Observability): http://localhost:6006
```

📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)

### Opción B: Build Local (Desarrollo)

```bash
# 1. Clonar repositorio
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA

# 2. Setup automático (instala todo)
./scripts/setup.sh

# 3. Iniciar sistema completo
./scripts/start.sh

# 4. Iniciar aplicación
# Terminal 1 - Backend:
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Terminal 2 - Frontend:
cd frontend && npm run dev

# 5. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

---

## 📁 Documentación Principal

- 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU
- 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)
- 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)
- 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub
- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)
- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)
- 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)
- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix
- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada
- 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales
- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema
- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders
- ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)
![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)
![Completado](https://img.shields.io/badge/Completado-100%25-success)
![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)
![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)
![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-90%25-green)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18.3-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)

---

## 📋 Descripción del Proyecto

Sistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.

**Cliente:** TeFinancia S.A.  
**Proyecto:** FinancIA 2030  
**Estado:** ✅ **100% RFP COVERAGE ACHIEVED** 🎉 - Production Ready

### 🎯 Sprint 6 - Completado

✅ **Enhanced Document Viewer** - Visor PDF avanzado con zoom, rotación, thumbnails  
✅ **Annotation System** - Sistema colaborativo de anotaciones con Canvas overlay  
✅ **Document Comparison** - Comparación lado a lado de versiones con sync scroll  
✅ **GraphQL API** - API completa con SharePoint y SAP DMS connectors  
✅ **100% RFP Coverage** - Todos los requisitos implementados

### 🎯 Objetivos Clave Alcanzados

- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato
- ✅ **Validación automatizada** contra listas de sanciones (OFAC, EU, World Bank)
- ✅ **IA Responsable** con explicabilidad y supervisión humana
- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)
- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)
- ✅ **Seguridad por diseño** con auditoría completa

---

## 🚀 Inicio Rápido

¿Quieres probar el sistema? Tienes **dos opciones**:

### Opción A: Docker Hub (Recomendado - Más Rápido) 🐳

```bash
# 1. Clonar repositorio
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA/infrastructure/docker

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY y otras credenciales

# 3. Desplegar con imágenes pre-construidas desde Docker Hub
docker-compose -f docker-compose.hub.yml up -d

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Phoenix (Observability): http://localhost:6006
```

📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)

### Opción B: Build Local (Desarrollo)

```bash
# 1. Clonar repositorio
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA

# 2. Setup automático (instala todo)
./scripts/setup.sh

# 3. Iniciar sistema completo
./scripts/start.sh

# 4. Iniciar aplicación
# Terminal 1 - Backend:
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Terminal 2 - Frontend:
cd frontend && npm run dev

# 5. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

---

## 📁 Documentación Principal

- 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU
- 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)
- 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)
- 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub
- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)
- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)
- 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)
- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix
- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada
- 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales
- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema
- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders
- ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)
![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)
![Completado](https://img.shields.io/badge/Completado-100%25-success)
![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)
![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)
![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-90%25-green)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18.3-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)

---

## 📋 Descripción del Proyecto

Sistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.

**Cliente:** TeFinancia S.A.  
**Proyecto:** FinancIA 2030  
**Estado:** ✅ **100% RFP COVERAGE ACHIEVED** 🎉 - Production Ready

### 🎯 Sprint 6 - Completado

✅ **Enhanced Document Viewer** - Visor PDF avanzado con zoom, rotación, thumbnails  
✅ **Annotation System** - Sistema colaborativo de anotaciones con Canvas overlay  
✅ **Document Comparison** - Comparación lado a lado de versiones con sync scroll  
✅ **GraphQL API** - API completa con SharePoint y SAP DMS connectors  
✅ **100% RFP Coverage** - Todos los requisitos implementados

### 🎯 Objetivos Clave Alcanzados

- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato
- ✅ **Validación automatizada** contra listas de sanciones (OFAC, EU, World Bank)
- ✅ **IA Responsable** con explicabilidad y supervisión humana
- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)
- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)
- ✅ **Seguridad por diseño** con auditoría completa

---

## 🚀 Inicio Rápido

¿Quieres probar el sistema? Tienes **dos opciones**:

### Opción A: Docker Hub (Recomendado - Más Rápido) 🐳

```bash
# 1. Clonar repositorio
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA/infrastructure/docker

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY y otras credenciales

# 3. Desplegar con imágenes pre-construidas desde Docker Hub
docker-compose -f docker-compose.hub.yml up -d

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Phoenix (Observability): http://localhost:6006
```

📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)

### Opción B: Build Local (Desarrollo)

```bash
# 1. Clonar repositorio
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA

# 2. Setup automático (instala todo)
./scripts/setup.sh

# 3. Iniciar sistema completo
./scripts/start.sh

# 4. Iniciar aplicación
# Terminal 1 - Backend:
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Terminal 2 - Frontend:
cd frontend && npm run dev

# 5. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

---

## 📁 Documentación Principal

- 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU
- 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)
- 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)
- 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub
- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)
- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)
- 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)
- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix
- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada
- 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales
- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema
- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders
- ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)
![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)
![Completado](https://img.shields.io/badge/Completado-100%25-success)
![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)
![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)
![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-90%25-green)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18.3-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)

---

## 📋 Descripción del Proyecto

Sistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.

**Cliente:** TeFinancia S.A.  
**Proyecto:** FinancIA 2030  
**Estado:** ✅ **100% RFP COVERAGE ACHIEVED** 🎉 - Production Ready

### 🎯 Sprint 6 - Completado

✅ **Enhanced Document Viewer** - Visor PDF avanzado con zoom, rotación, thumbnails  
✅ **Annotation System** - Sistema colaborativo de anotaciones con Canvas overlay  
✅ **Document Comparison** - Comparación lado a lado de versiones con sync scroll  
✅ **GraphQL API** - API completa con SharePoint y SAP DMS connectors  
✅ **100% RFP Coverage** - Todos los requisitos implementados

### 🎯 Objetivos Clave Alcanzados

- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato
- ✅ **Validación automatizada** contra listas de sanciones (OFAC, EU, World Bank)
- ✅ **IA Responsable** con explicabilidad y supervisión humana
- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)
- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)
- ✅ **Seguridad por diseño** con auditoría completa

---

## 🚀 Inicio Rápido

¿Quieres probar el sistema? Tienes **dos opciones**:

### Opción A: Docker Hub (Recomendado - Más Rápido) 🐳

```bash
# 1. Clonar repositorio
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA/infrastructure/docker

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY y otras credenciales

# 3. Desplegar con imágenes pre-construidas desde Docker Hub
docker-compose -f docker-compose.hub.yml up -d

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Phoenix (Observability): http://localhost:6006
```

📖 **Guía completa de deployment:** [`DEPLOYMENT.md`](DEPLOYMENT.md)

### Opción B: Build Local (Desarrollo)

```bash
# 1. Clonar repositorio
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA

# 2. Setup automático (instala todo)
./scripts/setup.sh

# 3. Iniciar sistema completo
./scripts/start.sh

# 4. Iniciar aplicación
# Terminal 1 - Backend:
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Terminal 2 - Frontend:
cd frontend && npm run dev

# 5. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

📖 **Guía completa:** [`QUICKSTART.md`](QUICKSTART.md)

---

## 📁 Documentación Principal

- 🎮 [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) — **✨ NUEVO** Guía completa de aceleración GPU
- 🐳 [`DOCKER_SETUP_LOCAL.md`](DOCKER_SETUP_LOCAL.md) — **Setup local con Docker** (nuevo)
- 🚀 [`QUICKSTART.md`](QUICKSTART.md) — **¡Empieza aquí!** Guía de inicio rápido (< 10 min)
- 🐳 [`DEPLOYMENT.md`](DEPLOYMENT.md) — **✨ NUEVO** Guía completa de deployment con Docker Hub
- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa (6k palabras)
- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance (8.5k palabras)
- 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment (7k palabras)
- 🔍 [`docs/PHOENIX_OBSERVABILITY.md`](docs/PHOENIX_OBSERVABILITY.md) — Observabilidad de LLMs con Arize Phoenix
- 🎯 [`docs/SPRINT6_COMPLETE.md`](docs/SPRINT6_COMPLETE.md) — **✨ NUEVO** Sprint 6: Sistema de Validación Automatizada
- 📚 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — **✨ NUEVO** Guía completa para usuarios finales
- 🔧 [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — **✨ NUEVO** Guía para administradores del sistema
- 🎬 [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **✨ NUEVO** Guión de demostración para stakeholders
- ✅ [`PROJECT_COMPLETE.md`](PROJECT_COMPLETE.md) — Resumen de proyecto completado

![Estado](https://img.shields.io/badge/Estado-✅%20Production%20Ready-brightgreen)
![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)
![Completado](https://img.shields.io/badge/Completado-100%25-success)
![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25%20🎯-gold)
![Sprint 6](https://img.shields.io/badge/Sprint%206-✅%20Complete-success)
![Tests](https://img.shields.io/badge/Tests-78%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-90%25