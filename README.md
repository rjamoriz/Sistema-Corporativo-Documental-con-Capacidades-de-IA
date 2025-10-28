# 🚀 FinancIA 2030 - Sistema Corporativo Documental con IA

![Estado](https://img.shields.io/badge/Estado-%20Production%20Ready-brightgreen) ![Versión](https://img.shields.io/badge/Versión-1.0.0-blue) ![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25-gold) ![License](https://img.shields.io/badge/License-Proprietary-red)

**Plataforma enterprise de gestión documental inteligente** con capacidades avanzadas de IA para procesamiento, clasificación, búsqueda semántica y análisis de riesgo. Diseñada para entornos financieros y corporativos con requisitos estrictos de cumplimiento normativo.

**Links rápidos:** [🚀 Inicio rápido](#-inicio-rápido) | [📚 Documentación](docs/) | [🏗️ Arquitectura](#-arquitectura-de-la-solución) | [🎯 Características](#-características-principales)

---

## 📋 Tabla de Contenidos

- [Resumen Ejecutivo](#-resumen-ejecutivo)
- [Arquitectura de la Solución](#-arquitectura-de-la-solución)
- [Características Principales](#-características-principales)
- [Funcionalidades Clave](#-funcionalidades-clave)
- [Stack Tecnológico](#-stack-tecnológico)
- [Inicio Rápido](#-inicio-rápido)
- [Documentación](#-documentación)

---

## 🎯 Resumen Ejecutivo

**FinancIA 2030** es una solución end-to-end de gestión documental corporativa que integra:

- **🤖 Inteligencia Artificial**: OCR, NER, clasificación automática, embeddings semánticos y RAG
- **🔍 Búsqueda Híbrida**: Combinación de búsqueda léxica (BM25) y semántica (vectores)
- **⚖️ Cumplimiento Normativo**: EU AI Act 2024, GDPR/LOPDGDD, NIS2, ISO 27001/27701/42001
- **📊 Análisis de Riesgo**: Scoring multidimensional con explicabilidad total
- **🔐 Seguridad Enterprise**: Autenticación SSO/MFA, cifrado end-to-end, auditoría completa
- **📈 Observabilidad**: Monitoreo de LLMs con Arize Phoenix, métricas operativas en tiempo real

### Casos de Uso

✅ **Gestión de contratos** - Clasificación, extracción de cláusulas, alertas de vencimiento  
✅ **Compliance financiero** - Validación automática de documentación regulatoria  
✅ **Análisis de riesgo** - Scoring de documentos con explicabilidad  
✅ **Búsqueda inteligente** - RAG conversacional con citación de fuentes  
✅ **Procesamiento masivo** - Ingestión y OCR de miles de documentos  
✅ **Auditoría y trazabilidad** - Logs inmutables de todas las operaciones

---

## 🏗️ Arquitectura de la Solución

### Vista de Alto Nivel

```mermaid
graph TB
    subgraph "🌐 Capa de Presentación"
        UI[React Frontend<br/>TypeScript + Vite]
    end
    
    subgraph "🔒 API Gateway"
        API[FastAPI Gateway<br/>Auth + Rate Limiting]
    end
    
    subgraph "⚙️ Microservicios Core"
        DOC[📄 Document Service<br/>Ingestión + Procesamiento]
        SEARCH[🔍 Search Service<br/>Híbrida: Léxica + Semántica]
        RAG[🤖 RAG Service<br/>Asistente Conversacional]
        ML[🧠 ML Service<br/>Clasificación + NER]
    end
    
    subgraph "📊 Servicios de Negocio"
        RISK[⚠️ Risk Analysis<br/>Scoring Multidimensional]
        COMP[⚖️ Compliance<br/>Motor de Reglas]
        SYNTH[🧬 Synthetic Data<br/>Generación de Datos]
    end
    
    subgraph "💾 Capa de Datos"
        PG[(PostgreSQL<br/>+pgvector)]
        OS[(OpenSearch<br/>BM25)]
        REDIS[(Redis<br/>Cache)]
        MINIO[(MinIO<br/>S3 Storage)]
        QDRANT[(Qdrant<br/>Vector DB)]
    end
    
    subgraph "🔧 Infraestructura"
        CELERY[Celery Workers<br/>Procesamiento Async]
        PHOENIX[Arize Phoenix<br/>LLM Observability]
    end
    
    UI -->|HTTPS| API
    API --> DOC
    API --> SEARCH
    API --> RAG
    API --> ML
    API --> RISK
    API --> COMP
    API --> SYNTH
    
    DOC --> PG
    DOC --> MINIO
    DOC --> CELERY
    
    SEARCH --> OS
    SEARCH --> QDRANT
    
    RAG --> QDRANT
    RAG --> PG
    RAG --> PHOENIX
    
    ML --> PG
    ML --> REDIS
    
    RISK --> PG
    COMP --> PG
    SYNTH --> PG
    
    CELERY --> REDIS
    
    style UI fill:#4FC3F7,stroke:#0277BD,stroke-width:3px,color:#000
    style API fill:#FFB74D,stroke:#E65100,stroke-width:3px,color:#000
    style DOC fill:#BA68C8,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style SEARCH fill:#9575CD,stroke:#4527A0,stroke-width:2px,color:#fff
    style RAG fill:#7E57C2,stroke:#311B92,stroke-width:2px,color:#fff
    style ML fill:#5C6BC0,stroke:#1A237E,stroke-width:2px,color:#fff
    style RISK fill:#66BB6A,stroke:#1B5E20,stroke-width:2px,color:#000
    style COMP fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#000
    style SYNTH fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style PG fill:#42A5F5,stroke:#0D47A1,stroke-width:2px,color:#fff
    style OS fill:#26C6DA,stroke:#006064,stroke-width:2px,color:#000
    style REDIS fill:#EF5350,stroke:#B71C1C,stroke-width:2px,color:#fff
    style MINIO fill:#FF7043,stroke:#BF360C,stroke-width:2px,color:#fff
    style QDRANT fill:#AB47BC,stroke:#4A148C,stroke-width:2px,color:#fff
    style CELERY fill:#FFA726,stroke:#E65100,stroke-width:2px,color:#000
    style PHOENIX fill:#EC407A,stroke:#880E4F,stroke-width:2px,color:#fff
```

### Pipeline de Procesamiento Documental

```mermaid
graph LR
    A[📥 Upload] -->|Validación| B[🔍 Ingest]
    B -->|OCR| C[📝 Transform]
    C -->|Extracción| D[🔬 Extract]
    D -->|NER + Metadata| E[🏷️ Classify]
    E -->|ML Model| F[📊 Index]
    F -->|Dual Index| G[🔍 Search/RAG]
    D -->|Validación| H[⚖️ Compliance]
    D -->|Análisis| I[⚠️ Risk Scoring]
    
    style A fill:#4FC3F7,stroke:#0277BD,stroke-width:3px,color:#000
    style B fill:#BA68C8,stroke:#6A1B9A,stroke-width:3px,color:#fff
    style C fill:#9575CD,stroke:#4527A0,stroke-width:3px,color:#fff
    style D fill:#7E57C2,stroke:#311B92,stroke-width:3px,color:#fff
    style E fill:#FFB74D,stroke:#E65100,stroke-width:3px,color:#000
    style F fill:#66BB6A,stroke:#1B5E20,stroke-width:3px,color:#000
    style G fill:#26C6DA,stroke:#006064,stroke-width:3px,color:#000
    style H fill:#EC407A,stroke:#880E4F,stroke-width:3px,color:#fff
    style I fill:#FFA726,stroke:#E65100,stroke-width:3px,color:#000
```

### Arquitectura de Microservicios (Vista Detallada)

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[React SPA<br/>Port 3000]
    end
    
    subgraph "Backend Services - Port 8000"
        direction TB
        AUTH[🔐 Auth Module<br/>JWT + SSO]
        DOCS[📄 Documents API<br/>/api/v1/documents]
        SRCH[🔍 Search API<br/>/api/v1/search]
        RAGAPI[🤖 RAG API<br/>/api/v1/rag]
        MLAPI[🧠 ML API<br/>/api/v1/ml]
        RISKAPI[⚠️ Risk API<br/>/api/v1/risk]
        COMPAPI[⚖️ Compliance API<br/>/api/v1/compliance]
        SYNTHAPI[🧬 Synthetic API<br/>/api/v1/synthetic]
        GRAPHQL[📊 GraphQL API<br/>/graphql]
    end
    
    subgraph "Processing Layer"
        WORKER1[Celery Worker 1<br/>OCR + Transform]
        WORKER2[Celery Worker 2<br/>ML + Classification]
        WORKER3[Celery Worker 3<br/>Embeddings + Index]
    end
    
    subgraph "Data Layer"
        direction LR
        DB1[(PostgreSQL<br/>Metadata + Users)]
        DB2[(OpenSearch<br/>Full-Text Search)]
        DB3[(Qdrant<br/>Vector Search)]
        DB4[(Redis<br/>Queue + Cache)]
        DB5[(MinIO<br/>Object Storage)]
    end
    
    FE -->|REST/GraphQL| AUTH
    AUTH --> DOCS
    AUTH --> SRCH
    AUTH --> RAGAPI
    AUTH --> MLAPI
    AUTH --> RISKAPI
    AUTH --> COMPAPI
    AUTH --> SYNTHAPI
    AUTH --> GRAPHQL
    
    DOCS --> WORKER1
    MLAPI --> WORKER2
    SRCH --> WORKER3
    
    WORKER1 --> DB4
    WORKER2 --> DB4
    WORKER3 --> DB4
    
    DOCS --> DB1
    DOCS --> DB5
    SRCH --> DB2
    SRCH --> DB3
    RAGAPI --> DB3
    MLAPI --> DB1
    RISKAPI --> DB1
    COMPAPI --> DB1
    
    style FE fill:#4FC3F7,stroke:#0277BD,stroke-width:3px,color:#000
    style AUTH fill:#EF5350,stroke:#B71C1C,stroke-width:3px,color:#fff
    style DOCS fill:#BA68C8,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style SRCH fill:#9575CD,stroke:#4527A0,stroke-width:2px,color:#fff
    style RAGAPI fill:#7E57C2,stroke:#311B92,stroke-width:2px,color:#fff
    style MLAPI fill:#5C6BC0,stroke:#1A237E,stroke-width:2px,color:#fff
    style RISKAPI fill:#66BB6A,stroke:#1B5E20,stroke-width:2px,color:#000
    style COMPAPI fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#000
    style SYNTHAPI fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    style GRAPHQL fill:#26C6DA,stroke:#006064,stroke-width:2px,color:#000
    style WORKER1 fill:#FFA726,stroke:#E65100,stroke-width:2px,color:#000
    style WORKER2 fill:#FFB74D,stroke:#EF6C00,stroke-width:2px,color:#000
    style WORKER3 fill:#FFCC80,stroke:#F57C00,stroke-width:2px,color:#000
    style DB1 fill:#42A5F5,stroke:#0D47A1,stroke-width:2px,color:#fff
    style DB2 fill:#26C6DA,stroke:#006064,stroke-width:2px,color:#000
    style DB3 fill:#AB47BC,stroke:#4A148C,stroke-width:2px,color:#fff
    style DB4 fill:#EF5350,stroke:#B71C1C,stroke-width:2px,color:#fff
    style DB5 fill:#FF7043,stroke:#BF360C,stroke-width:2px,color:#fff
```

### Arquitectura v2.0 - Quantum & GPU Enhancement

```mermaid
graph TB
    subgraph "🌐 Sistema Actual v1.0"
        APP[App Principal<br/>Backend + Frontend]
        DB[(Bases de Datos<br/>PostgreSQL + OpenSearch + Qdrant)]
    end
    
    subgraph "🎮 GPU Acceleration Layer"
        GPU[GPU Embedding Service<br/>Puerto 8001]
        FAISS[FAISS-GPU<br/>Vector Search]
    end
    
    subgraph "⚛️ Quantum Computing Layer"
        DWAVE[D-Wave Service<br/>Puerto 8002<br/>QUBO + Simulated Annealing]
        IBM[IBM Qiskit Service<br/>Puerto 8003<br/>QAOA + Circuits]
        NVIDIA[NVIDIA cuQuantum Service<br/>Puerto 8004<br/>GPU Simulation]
    end
    
    subgraph "🤖 Enhanced AI Layer"
        RAG[RAG Enhanced Service<br/>Puerto 8005<br/>OpenAI + Anthropic]
    end
    
    subgraph "📊 Monitoring Layer"
        PROM[Prometheus<br/>Puerto 9090]
        GRAF[Grafana<br/>Puerto 3001]
    end
    
    APP -.->|Opcional| GPU
    APP -.->|Opcional| DWAVE
    APP -.->|Opcional| IBM
    APP -.->|Opcional| NVIDIA
    APP -.->|Opcional| RAG
    
    GPU --> FAISS
    RAG --> GPU
    
    GPU --> PROM
    DWAVE --> PROM
    IBM --> PROM
    NVIDIA --> PROM
    RAG --> PROM
    
    PROM --> GRAF
    
    style APP fill:#4FC3F7,stroke:#0277BD,stroke-width:3px,color:#000
    style GPU fill:#FFB74D,stroke:#E65100,stroke-width:3px,color:#000
    style FAISS fill:#FFA726,stroke:#EF6C00,stroke-width:2px,color:#000
    style DWAVE fill:#BA68C8,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style IBM fill:#9575CD,stroke:#4527A0,stroke-width:2px,color:#fff
    style NVIDIA fill:#7E57C2,stroke:#311B92,stroke-width:2px,color:#fff
    style RAG fill:#66BB6A,stroke:#1B5E20,stroke-width:2px,color:#000
    style PROM fill:#EF5350,stroke:#B71C1C,stroke-width:2px,color:#fff
    style GRAF fill:#EC407A,stroke:#880E4F,stroke-width:2px,color:#fff
```

**Características v2.0:**
- ⚡ **GPU Acceleration**: Embeddings 10-20× más rápidos
- ⚛️ **Quantum Computing**: Optimización QUBO para deduplicación
- 🧠 **Quantum ML**: Clasificación con circuitos cuánticos
- 🤖 **Enhanced RAG**: LLMs con trazabilidad 100%
- 📊 **Monitoring**: Prometheus + Grafana opensource
- 🔌 **Modular**: Servicios independientes, no afectan app actual

---

## 📁 Estructura del Proyecto

```
Sistema-Corporativo-Documental-con-Capacidades-de-IA/
├── 📂 backend/                          # Backend existente (FastAPI)
│   ├── api/                             # Endpoints REST
│   ├── core/                            # Configuración y seguridad
│   ├── models/                          # Modelos SQLAlchemy
│   ├── services/                        # Lógica de negocio
│   ├── ml/                              # Modelos ML
│   └── main.py                          # Punto de entrada
│
├── 📂 frontend/                         # Frontend existente (React + TypeScript)
│   ├── src/
│   │   ├── components/                  # Componentes React
│   │   ├── pages/                       # Páginas
│   │   ├── services/                    # API clients
│   │   └── App.tsx                      # App principal
│   └── package.json
│
├── 📂 services/                         # ✨ NUEVOS SERVICIOS v2.0
│   ├── 🎮 gpu-embedding/               # GPU Embedding Service
│   │   ├── main.py                      # FastAPI service
│   │   ├── Dockerfile                   # CUDA 12.1 + PyTorch
│   │   ├── requirements.txt             # Dependencias GPU
│   │   ├── README.md                    # Documentación
│   │   └── .env.example                 # Configuración
│   │
│   ├── ⚛️ quantum-dwave/               # Quantum D-Wave Service
│   │   ├── main.py                      # QUBO + Simulated Annealing
│   │   ├── Dockerfile
│   │   ├── requirements.txt             # D-Wave Ocean SDK
│   │   └── .env.example
│   │
│   ├── ⚛️ quantum-ibm/                 # Quantum IBM Qiskit Service
│   │   ├── main.py                      # QAOA + Circuits
│   │   ├── Dockerfile
│   │   ├── requirements.txt             # Qiskit + Aer
│   │   └── .env.example
│   │
│   ├── ⚛️ quantum-nvidia/              # Quantum NVIDIA cuQuantum Service
│   │   ├── main.py                      # GPU Quantum Simulation
│   │   ├── Dockerfile                   # CUDA + Qiskit-Aer-GPU
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   ├── 🤖 rag-enhanced/                # RAG Enhanced Service
│   │   ├── main.py                      # RAG + LLMs
│   │   ├── Dockerfile
│   │   ├── requirements.txt             # LangChain + OpenAI + Anthropic
│   │   └── .env.example
│   │
│   └── README.md                        # 📚 README consolidado servicios
│
├── 📂 monitoring/                       # ✨ MONITOREO (Opensource)
│   ├── prometheus/
│   │   └── prometheus.yml               # Configuración Prometheus
│   └── grafana/
│       └── datasources/
│           └── prometheus.yml           # Datasource Grafana
│
├── 📂 docs/                             # 📚 DOCUMENTACIÓN
│   ├── ARCHITECTURE.md                  # Arquitectura técnica
│   ├── QUANTUM_GPU_ENHANCEMENT_PLAN.md  # ✨ Plan v2.0 completo
│   ├── IMPLEMENTATION_GUIDE_V2.md       # ✨ Guía de implementación
│   ├── TESTING_GUIDE.md                 # ✨ Guía de testing
│   ├── API_DOCUMENTATION.md             # Documentación API
│   └── DEPLOYMENT.md                    # Guía de despliegue
│
├── 📂 infrastructure/                   # Infraestructura
│   └── docker/                          # Configuraciones Docker
│
├── 📄 docker-compose.yml                # Compose app principal
├── 📄 docker-compose.quantum-gpu.yml    # ✨ Compose servicios v2.0
├── 📄 README.md                         # Este archivo
└── 📄 .env.example                      # Variables de entorno

Leyenda:
📂 Carpeta existente
✨ Nuevo en v2.0
🎮 GPU Service
⚛️ Quantum Service
🤖 AI Service
📚 Documentación
```

**Estadísticas del Proyecto:**
- **Servicios v1.0:** 1 aplicación monolítica
- **Servicios v2.0:** +5 microservicios modulares
- **Líneas de código v2.0:** ~4,500+
- **Documentación v2.0:** ~3,000+ líneas
- **Endpoints API v2.0:** +25 nuevos endpoints
- **Frameworks cuánticos:** 3 (D-Wave, IBM Qiskit, NVIDIA cuQuantum)

---

## 🗄️ Arquitectura DataStax Astra DB - Vector Search

### Diagrama de Componente

```mermaid
graph TB
    subgraph "📱 Cliente"
        USER[Usuario/Aplicación]
    end
    
    subgraph "🎯 API Layer"
        API[FastAPI Service<br/>Puerto 8006]
        CACHE[Redis Cache<br/>Consultas Frecuentes]
    end
    
    subgraph "🔄 Processing Layer"
        DOC[Document Processor<br/>PDF, DOCX, TXT]
        CHUNK[Text Chunker<br/>Overlapping Windows]
        EMB[Embedding Generator<br/>OpenAI/Cohere/BERT]
    end
    
    subgraph "🎮 GPU Integration"
        GPU[GPU Embedding Service<br/>Puerto 8001<br/>10-20x Faster]
    end
    
    subgraph "☁️ DataStax Astra DB Cloud"
        ASTRA[(Astra DB<br/>Vector Collection)]
        HNSW[HNSW Index<br/>ANN Search]
        META[Metadata Store<br/>JSON Fields]
    end
    
    subgraph "📊 Monitoring"
        PROM[Prometheus<br/>Métricas]
        GRAF[Grafana<br/>Dashboards]
    end
    
    USER -->|Upload Doc| API
    USER -->|Search Query| API
    
    API -->|Check Cache| CACHE
    API -->|Process| DOC
    DOC -->|Extract Text| CHUNK
    CHUNK -->|Generate Embeddings| EMB
    
    EMB -.->|Optional GPU| GPU
    GPU -.->|Fast Embeddings| EMB
    
    EMB -->|Store Vector| ASTRA
    API -->|Vector Search| HNSW
    HNSW -->|ANN Results| API
    ASTRA -->|Metadata| META
    
    API -->|Metrics| PROM
    PROM -->|Visualize| GRAF
    
    API -->|Results + Cache| USER
    
    style USER fill:#4FC3F7,stroke:#0277BD,stroke-width:2px,color:#000
    style API fill:#66BB6A,stroke:#2E7D32,stroke-width:3px,color:#fff
    style CACHE fill:#FFA726,stroke:#EF6C00,stroke-width:2px,color:#000
    style DOC fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000
    style CHUNK fill:#FFCC80,stroke:#FB8C00,stroke-width:2px,color:#000
    style EMB fill:#FFD54F,stroke:#F9A825,stroke-width:2px,color:#000
    style GPU fill:#FF6F00,stroke:#E65100,stroke-width:3px,color:#fff
    style ASTRA fill:#7E57C2,stroke:#4527A0,stroke-width:3px,color:#fff
    style HNSW fill:#9575CD,stroke:#5E35B1,stroke-width:2px,color:#fff
    style META fill:#B39DDB,stroke:#673AB7,stroke-width:2px,color:#000
    style PROM fill:#EF5350,stroke:#C62828,stroke-width:2px,color:#fff
    style GRAF fill:#EC407A,stroke:#AD1457,stroke-width:2px,color:#fff
```

### Flujo de Datos

**Ingestión de Documentos:**
```
Usuario → API → Document Processor → Text Chunker → Embedding Generator → [GPU Service] → Astra DB
```

**Búsqueda Semántica:**
```
Query → API → [Cache Check] → Embedding Generator → [GPU Service] → HNSW Search → Ranking → Usuario
```

---

## 🧮 Algoritmo HNSW (Hierarchical Navigable Small World)

### Fundamentos Matemáticos

DataStax Astra DB utiliza el algoritmo **HNSW** para búsquedas vectoriales eficientes (ANN - Approximate Nearest Neighbor).

#### 1. Estructura Jerárquica

El índice HNSW construye una estructura de grafo multi-capa donde cada capa $l$ contiene un subconjunto de nodos:

$$
\text{Probabilidad de inserción en capa } l: \quad P(l) = \frac{1}{2^l}
$$

**Número máximo de capas:**

$$
L_{max} = \lfloor -\ln(N) \cdot m_L \rfloor
$$

Donde:
- $N$ = número total de vectores
- $m_L$ = factor de normalización (típicamente $\frac{1}{\ln(2)}$)

#### 2. Distancia entre Vectores

Para vectores $\mathbf{v}_i, \mathbf{v}_j \in \mathbb{R}^d$, HNSW soporta múltiples métricas:

**Similitud Coseno (usada en Astra DB):**

$$
\text{similarity}(\mathbf{v}_i, \mathbf{v}_j) = \frac{\mathbf{v}_i \cdot \mathbf{v}_j}{\|\mathbf{v}_i\| \|\mathbf{v}_j\|} = \frac{\sum_{k=1}^{d} v_{i,k} \cdot v_{j,k}}{\sqrt{\sum_{k=1}^{d} v_{i,k}^2} \cdot \sqrt{\sum_{k=1}^{d} v_{j,k}^2}}
$$

**Distancia Euclidiana:**

$$
d(\mathbf{v}_i, \mathbf{v}_j) = \|\mathbf{v}_i - \mathbf{v}_j\| = \sqrt{\sum_{k=1}^{d} (v_{i,k} - v_{j,k})^2}
$$

#### 3. Algoritmo de Búsqueda

**Entrada:** Vector query $\mathbf{q}$, número de vecinos $K$

**Proceso:**

1. **Capa superior** ($l = L_{max}$): Encontrar punto de entrada $e_p$

$$
e_p = \arg\min_{v \in \text{Layer}_l} d(\mathbf{q}, \mathbf{v})
$$

2. **Descenso por capas** ($l = L_{max} \to 0$):

Para cada capa $l$:

$$
\text{candidates} = \{v \in \text{neighbors}(e_p) : d(\mathbf{q}, v) < d(\mathbf{q}, e_p)\}
$$

3. **Búsqueda en capa 0** (más densa):

Mantener lista de $K$ vecinos más cercanos:

$$
\text{result} = \text{top-K}\{\mathbf{v} \in \text{Layer}_0 : \text{similarity}(\mathbf{q}, \mathbf{v})\}
$$

#### 4. Complejidad Computacional

**Tiempo de búsqueda:**

$$
O(\log N \cdot M)
$$

Donde:
- $N$ = número de vectores en el índice
- $M$ = número máximo de conexiones por nodo (típicamente 16-32)

**Comparación con búsqueda lineal:**

| Método | Complejidad | Ejemplo (1M vectores) |
|--------|-------------|----------------------|
| **Búsqueda Lineal** | $O(N \cdot d)$ | ~1,000,000 comparaciones |
| **HNSW** | $O(\log N \cdot M)$ | ~300 comparaciones |
| **Speedup** | $\frac{N \cdot d}{\log N \cdot M}$ | **~3,300x más rápido** |

#### 5. Parámetros de Optimización

**Factor de construcción** ($ef_{construction}$):

$$
ef_{construction} \geq K
$$

Controla la calidad del índice durante construcción.

**Factor de búsqueda** ($ef_{search}$):

$$
ef_{search} \geq K
$$

Trade-off entre precisión y velocidad:

$$
\text{Recall} \propto ef_{search}, \quad \text{Latency} \propto ef_{search}
$$

#### 6. Ejemplo Práctico

Para un sistema con:
- $N = 1,000,000$ documentos
- $d = 1536$ dimensiones (OpenAI ada-002)
- $M = 16$ conexiones
- $K = 5$ vecinos

**Búsqueda HNSW:**

$$
\text{Comparaciones} \approx \log_2(1,000,000) \cdot 16 \approx 320
$$

$$
\text{Latencia} \approx 1-5 \text{ ms}
$$

**vs Búsqueda Lineal:**

$$
\text{Comparaciones} = 1,000,000
$$

$$
\text{Latencia} \approx 500-1000 \text{ ms}
$$

**Mejora:** $\frac{1000}{5} = 200\text{x más rápido}$

---

### 📊 Ventajas de HNSW en Astra DB

1. **Escalabilidad:** $O(\log N)$ permite millones de vectores
2. **Precisión:** Recall > 95% con configuración óptima
3. **Velocidad:** Latencias < 10ms para búsquedas
4. **Memoria Eficiente:** Solo mantiene grafo, no matriz completa
5. **Actualización Dinámica:** Inserción/eliminación en tiempo real

---

## ⚛️ Arquitectura Quantum ML - PennyLane

### Diagrama de Componente

```mermaid
graph TB
    subgraph "🌐 Client Layer"
        CLIENT[Aplicaciones Cliente]
        API_GW[API Gateway]
    end
    
    subgraph "⚛️ Quantum ML Service - Puerto 8007"
        FASTAPI[FastAPI Server]
        
        subgraph "Modelos Cuánticos"
            VQC[Variational Quantum Classifier<br/>Clasificación de Documentos]
            QAUTO[Quantum Autoencoder<br/>Compresión de Embeddings]
            QANOM[Quantum Anomaly Detector<br/>Detección de Outliers]
        end
        
        subgraph "Backend Cuántico"
            PENNYLANE[PennyLane Framework<br/>Diferenciación Automática]
            QDEV[Quantum Device<br/>default.qubit<br/>4 qubits, 3 layers]
            QCIRCUIT[Circuitos Cuánticos<br/>StronglyEntanglingLayers]
        end
        
        subgraph "Explainability"
            SHAP_Q[SHAP TreeExplainer<br/>Quantum Circuits]
            METRICS_Q[Métricas Cuánticas<br/>Circuit Depth, Gates]
        end
    end
    
    subgraph "🔗 Servicios Integrados"
        GPU_EMB[GPU Embedding Service<br/>Puerto 8001]
        ASTRA_DB[Astra VectorDB<br/>Puerto 8006]
        PROMETHEUS[Prometheus<br/>Puerto 9090]
    end
    
    CLIENT --> API_GW
    API_GW --> FASTAPI
    
    FASTAPI --> VQC
    FASTAPI --> QAUTO
    FASTAPI --> QANOM
    
    VQC --> PENNYLANE
    QAUTO --> PENNYLANE
    QANOM --> PENNYLANE
    
    PENNYLANE --> QDEV
    QDEV --> QCIRCUIT
    
    VQC --> SHAP_Q
    QAUTO --> SHAP_Q
    
    FASTAPI --> METRICS_Q
    
    FASTAPI -.->|Obtener Embeddings| GPU_EMB
    FASTAPI -.->|Almacenar Resultados| ASTRA_DB
    METRICS_Q -->|Scrape Métricas| PROMETHEUS
    
    style VQC fill:#00d4ff,stroke:#0099cc,stroke-width:3px,color:#000
    style QAUTO fill:#00d4ff,stroke:#0099cc,stroke-width:3px,color:#000
    style QANOM fill:#00d4ff,stroke:#0099cc,stroke-width:3px,color:#000
    style PENNYLANE fill:#ffaa00,stroke:#ff8800,stroke-width:3px,color:#000
    style QDEV fill:#ffaa00,stroke:#ff8800,stroke-width:3px,color:#000
    style QCIRCUIT fill:#ffaa00,stroke:#ff8800,stroke-width:3px,color:#000
    style SHAP_Q fill:#ff00ff,stroke:#cc00cc,stroke-width:3px,color:#000
    style FASTAPI fill:#00ff88,stroke:#00cc66,stroke-width:3px,color:#000
```

### Flujo de Clasificación Cuántica

```mermaid
sequenceDiagram
    participant C as Cliente
    participant API as FastAPI
    participant VQC as Quantum Classifier
    participant PL as PennyLane
    participant QD as Quantum Device
    participant SHAP as SHAP Explainer
    
    C->>API: POST /qml/classify
    Note over C,API: {embedding: [0.1, 0.2, ...],<br/>explain: true}
    
    API->>VQC: classify(embedding)
    VQC->>VQC: preprocess_input()
    Note over VQC: Normalizar a [0, 2π]<br/>para Angle Encoding
    
    VQC->>PL: quantum_neural_network()
    PL->>QD: Ejecutar circuito
    
    Note over QD: 1. AngleEmbedding<br/>2. StronglyEntanglingLayers<br/>3. Medir Pauli-Z
    
    QD-->>PL: quantum_output
    PL-->>VQC: expectation_values
    
    VQC->>VQC: softmax(quantum_output)
    Note over VQC: Convertir a probabilidades
    
    VQC->>SHAP: compute_shap_values()
    SHAP->>SHAP: Calcular contribuciones
    SHAP-->>VQC: shap_values
    
    VQC-->>API: classification_result
    Note over API: {predicted_class: 2,<br/>confidence: 0.85,<br/>quantum_output: [...],<br/>shap_values: [...]}
    
    API-->>C: JSON Response
```

### Ventajas del Quantum ML

| Característica | Descripción | Beneficio |
|---|---|---|
| **Ventaja Cuántica** | Procesamiento paralelo cuántico | >1.2x vs modelos clásicos en alta dimensión |
| **Generalización** | Mejor con pocos datos | Reduce overfitting |
| **Expresividad** | Espacios de Hilbert exponenciales | Captura patrones complejos |
| **Explainability** | SHAP para circuitos cuánticos | Transparencia total |

### Casos de Uso Quantum ML

1. **Clasificación de Documentos Complejos**
   - Documentos con múltiples idiomas
   - Estructuras no lineales
   - Patrones ocultos en embeddings

2. **Optimización de Embeddings**
   - Reducción de dimensionalidad cuántica
   - Compresión sin pérdida de información
   - Autoencoders variacionales

3. **Detección de Anomalías**
   - Documentos fraudulentos
   - Patrones inusuales
   - Outliers en alta dimensión

---

## 🤖 Arquitectura AWS SageMaker - Predictive ML

### Diagrama de Componente

```mermaid
graph TB
    subgraph "🌐 Client Layer"
        CLIENT[Aplicaciones Cliente]
        API_GW[API Gateway]
    end
    
    subgraph "🤖 SageMaker Predictor Service - Puerto 8008"
        FASTAPI[FastAPI Server]
        
        subgraph "Modelos ML"
            LGBM[LightGBM Classifier<br/>Gradient Boosting]
            XGB[XGBoost Classifier<br/>Extreme Gradient Boosting]
        end
        
        subgraph "Explainability"
            SHAP[SHAP TreeExplainer<br/>Feature Importance]
            CONTRIB[Feature Contributions<br/>Waterfall Plots]
        end
        
        subgraph "Model Management"
            LOADER[Model Loader<br/>Pickle/Joblib]
            CACHE[Model Cache<br/>In-Memory]
            DUMMY[Dummy Models<br/>Development]
        end
        
        subgraph "Monitoring"
            PROM_M[Prometheus Metrics<br/>Latency, Confidence]
            HEALTH[Health Checks]
        end
    end
    
    subgraph "☁️ AWS Services (Opcional)"
        SM_ENDPOINT[SageMaker Endpoint<br/>Producción]
        
        subgraph "Training Pipeline"
            S3_DATA[S3 Data Bucket<br/>Datasets]
            GLUE[AWS Glue<br/>Data Processing]
            SM_TRAIN[SageMaker Training<br/>ml.c5.xlarge]
            S3_MODEL[S3 Model Bucket<br/>Artifacts]
        end
        
        ECR[Amazon ECR<br/>Container Registry]
    end
    
    subgraph "🔗 Servicios Integrados"
        ASTRA_DB[Astra VectorDB<br/>Almacenar Predicciones]
        PROMETHEUS[Prometheus<br/>Monitoring]
    end
    
    CLIENT --> API_GW
    API_GW --> FASTAPI
    
    FASTAPI --> LGBM
    FASTAPI --> XGB
    
    LGBM --> SHAP
    XGB --> SHAP
    SHAP --> CONTRIB
    
    LOADER --> LGBM
    LOADER --> XGB
    LOADER --> CACHE
    LOADER --> DUMMY
    
    FASTAPI --> PROM_M
    FASTAPI --> HEALTH
    
    FASTAPI -.->|Modo Producción| SM_ENDPOINT
    
    S3_DATA --> GLUE
    GLUE --> SM_TRAIN
    SM_TRAIN --> S3_MODEL
    S3_MODEL --> SM_ENDPOINT
    ECR --> SM_ENDPOINT
    
    FASTAPI -.->|Guardar Resultados| ASTRA_DB
    PROM_M -->|Scrape| PROMETHEUS
    
    style LGBM fill:#00d4ff,stroke:#0099cc,stroke-width:3px,color:#000
    style XGB fill:#00d4ff,stroke:#0099cc,stroke-width:3px,color:#000
    style SHAP fill:#ffaa00,stroke:#ff8800,stroke-width:3px,color:#000
    style CONTRIB fill:#ffaa00,stroke:#ff8800,stroke-width:3px,color:#000
    style SM_ENDPOINT fill:#ff00ff,stroke:#cc00cc,stroke-width:3px,color:#000
    style FASTAPI fill:#00ff88,stroke:#00cc66,stroke-width:3px,color:#000
    style DUMMY fill:#ff6600,stroke:#cc5200,stroke-width:3px,color:#000
```

### Flujo de Predicción con Explainability

```mermaid
sequenceDiagram
    participant C as Cliente
    participant API as FastAPI
    participant M as ML Model
    participant SHAP as SHAP Explainer
    participant DB as Astra DB
    
    C->>API: POST /predict
    Note over C,API: {features: {<br/>  amount: 25000,<br/>  duration: 24,<br/>  age: 35<br/>}, explain: true}
    
    API->>M: Load Model
    Note over M: LightGBM o XGBoost
    
    API->>M: predict(features)
    M->>M: Feature Engineering
    Note over M: Normalización<br/>Encoding categórico
    
    M->>M: Model Inference
    M-->>API: prediction + probabilities
    Note over API: prediction: 1<br/>probability: 0.85
    
    alt Explain = True
        API->>SHAP: compute_shap_values()
        Note over SHAP: TreeExplainer<br/>Calcular contribuciones
        
        SHAP->>SHAP: For each feature
        Note over SHAP: amount: +0.15<br/>duration: -0.05<br/>age: +0.08
        
        SHAP-->>API: shap_values + base_value
        
        API->>API: Format explanation
        Note over API: Feature names<br/>Feature values<br/>SHAP values<br/>Base value
    end
    
    API->>DB: Store prediction
    Note over DB: Guardar para<br/>análisis posterior
    
    API-->>C: JSON Response
    Note over C,API: {prediction: 1,<br/>probability: 0.85,<br/>risk_score: 85.0,<br/>explanation: {...}}
```

### Capacidades del SageMaker Predictor

| Característica | Descripción | Beneficio |
|---|---|---|
| **Dual Model Support** | LightGBM + XGBoost | Comparación de rendimiento |
| **SHAP Explainability** | Contribución de cada feature | Transparencia total |
| **Batch Processing** | Predicciones masivas | Alta eficiencia |
| **AWS Integration** | SageMaker opcional | Escalabilidad cloud |
| **Local Development** | Modelos dummy | Sin costos AWS |

### Casos de Uso Predictive ML

1. **Evaluación de Crédito**
   - Scoring de solicitudes
   - Análisis de riesgo
   - Explicación de decisiones

2. **Análisis de Riesgo Financiero**
   - Predicción de default
   - Clasificación de documentos
   - Detección de fraude

3. **Aprobación de Préstamos**
   - Decisión automática
   - Explicación regulatoria
   - Cumplimiento normativo

### Interpretación SHAP

**Ejemplo de Explicación:**

```
Base Value: 0.50 (50% probabilidad base)

Feature Contributions:
+ Amount (25000€):        +0.15  → Aumenta riesgo
- Duration (24 meses):    -0.05  → Reduce riesgo
+ Age (35 años):          +0.08  → Aumenta confianza
+ Employment (60 meses):  +0.12  → Aumenta confianza
- Dependents (2):         -0.02  → Reduce ligeramente

Final Prediction: 0.85 (85% probabilidad)
Risk Score: 85/100
```

**Interpretación:**
- Valores SHAP **positivos**: Aumentan la probabilidad de la clase positiva
- Valores SHAP **negativos**: Disminuyen la probabilidad
- **Base value**: Predicción promedio del modelo
- **Suma de contribuciones**: Lleva del base value a la predicción final

---

## ✨ Características Principales

### 🤖 Inteligencia Artificial

- **OCR Avanzado**: Tesseract + PyTesseract para documentos escaneados
- **NER (Named Entity Recognition)**: Extracción de personas, organizaciones, DNI, IBAN, fechas
- **Clasificación Automática**: Modelo BETO fine-tuned para 10+ categorías documentales
- **Embeddings Semánticos**: Sentence-BERT para representación vectorial
- **RAG (Retrieval Augmented Generation)**: Asistente conversacional con citación obligatoria

### 🔍 Búsqueda y Recuperación

- **Búsqueda Híbrida**: Combina BM25 (léxica) + vectores (semántica) con re-ranking
- **Filtros Avanzados**: Por tipo, fecha, autor, categoría, riesgo, compliance
- **Búsqueda Facetada**: Agregaciones y estadísticas en tiempo real
- **Búsqueda Conversacional**: Interfaz de chat con contexto histórico

### ⚖️ Cumplimiento Normativo

- **EU AI Act 2024**: Clasificación de riesgo, documentación obligatoria, auditoría
- **GDPR/LOPDGDD**: Anonimización, derecho al olvido, consentimiento
- **NIS2 Directive**: Ciberseguridad, gestión de incidentes
- **ISO 27001/27701/42001**: Gestión de seguridad y privacidad
- **Motor de Reglas**: Validación automática de compliance con evidencias

### 📊 Análisis y Reporting

- **Scoring de Riesgo**: Análisis multidimensional (legal, financiero, operacional)
- **Explicabilidad**: Cada decisión con evidencias y razonamiento
- **Dashboards Interactivos**: Métricas operativas y de negocio
- **Alertas Automáticas**: Notificaciones de vencimientos, anomalías, incumplimientos

### 🔐 Seguridad Enterprise

- **Autenticación**: SSO, LDAP/AD, MFA
- **Autorización**: RBAC granular por documento y operación
- **Cifrado**: TLS 1.3 en tránsito, AES-256 en reposo
- **Auditoría**: Logs inmutables de todas las operaciones
- **Anonimización**: PII detection y enmascaramiento automático

---

## 🎯 Funcionalidades Clave

### 📄 Gestión Documental

| Funcionalidad | Descripción |
|---------------|-------------|
| **Ingestión Multi-canal** | Upload web, API REST, conectores (SharePoint, SAP DMS), carpetas vigiladas |
| **Procesamiento Automático** | OCR, conversión de formatos, normalización, extracción de metadatos |
| **Versionado** | Control de versiones con diff visual y rollback |
| **Deduplicación** | Detección automática de duplicados por hash SHA-256 |
| **Comparación** | Diff side-by-side de documentos con highlighting |
| **Anotaciones** | Sistema de comentarios y marcado colaborativo |

### 🔍 Búsqueda Inteligente

| Funcionalidad | Descripción |
|---------------|-------------|
| **Búsqueda Full-Text** | Indexación completa con OpenSearch (BM25) |
| **Búsqueda Semántica** | Vectores con Qdrant para búsqueda por significado |
| **Búsqueda Híbrida** | Fusión de resultados léxicos y semánticos con re-ranking |
| **Filtros Dinámicos** | Por tipo, fecha, categoría, autor, riesgo, compliance |
| **Sugerencias** | Autocompletado y corrección ortográfica |
| **Historial** | Búsquedas recientes y guardadas |

### 🤖 Asistente IA (RAG)

| Funcionalidad | Descripción |
|---------------|-------------|
| **Chat Conversacional** | Interfaz de chat con contexto histórico |
| **Citación Obligatoria** | Cada respuesta con fuentes y extractos relevantes |
| **Multi-documento** | Respuestas que sintetizan información de múltiples docs |
| **Explicabilidad** | Razonamiento paso a paso de las respuestas |
| **Observabilidad** | Monitoreo de prompts, latencia, tokens con Arize Phoenix |

### 📊 Análisis de Riesgo

| Funcionalidad | Descripción |
|---------------|-------------|
| **Scoring Multidimensional** | Legal, financiero, operacional, reputacional |
| **Explicabilidad Total** | Evidencias y factores que contribuyen al score |
| **Alertas Automáticas** | Notificaciones de documentos de alto riesgo |
| **Tendencias** | Evolución del riesgo en el tiempo |
| **Reportes** | Informes ejecutivos y detallados |

### ⚖️ Compliance

| Funcionalidad | Descripción |
|---------------|-------------|
| **Motor de Reglas** | Validación automática de requisitos normativos |
| **Auditoría Completa** | Logs inmutables de todas las validaciones |
| **Evidencias** | Captura automática de pruebas de cumplimiento |
| **Alertas de Vencimiento** | Notificaciones de documentos próximos a expirar |
| **Reportes Regulatorios** | Generación automática de informes para autoridades |

### 🧬 Datos Sintéticos

| Funcionalidad | Descripción |
|---------------|-------------|
| **Generación Automática** | Creación de documentos sintéticos para testing |
| **Templates Configurables** | Distribuciones predefinidas (default, financial, contracts) |
| **Auto-upload** | Carga automática de documentos generados |
| **Historial** | Seguimiento de generaciones con métricas |

---

## 🛠️ Stack Tecnológico

### Backend

| Componente | Tecnología | Versión | Propósito |
|------------|-----------|---------|-----------|
| **Framework** | FastAPI | 0.104+ | API REST de alto rendimiento |
| **ORM** | SQLAlchemy | 2.0+ | Abstracción de base de datos |
| **Task Queue** | Celery | 5.3+ | Procesamiento asíncrono |
| **Auth** | JWT + OAuth2 | - | Autenticación y autorización |
| **Validación** | Pydantic | 2.0+ | Validación de datos |

### Frontend

| Componente | Tecnología | Versión | Propósito |
|------------|-----------|---------|-----------|
| **Framework** | React | 18+ | UI interactiva |
| **Lenguaje** | TypeScript | 5.0+ | Type safety |
| **Build Tool** | Vite | 4.0+ | Build rápido y HMR |
| **UI Library** | Material-UI | 5.0+ | Componentes profesionales |
| **State Management** | React Query | 4.0+ | Gestión de estado servidor |
| **Routing** | React Router | 6.0+ | Navegación SPA |

### Datos y Almacenamiento

| Componente | Tecnología | Versión | Propósito |
|------------|-----------|---------|-----------|
| **Base de Datos** | PostgreSQL | 15+ | Datos relacionales + pgvector |
| **Full-Text Search** | OpenSearch | 2.11+ | Búsqueda léxica (BM25) |
| **Vector Database** | Qdrant | 1.7+ | Búsqueda semántica |
| **Cache** | Redis | 7.0+ | Cache + cola de tareas |
| **Object Storage** | MinIO | Latest | Almacenamiento S3-compatible |

### Machine Learning e IA

| Componente | Tecnología | Versión | Propósito |
|------------|-----------|---------|-----------|
| **LLM** | OpenAI GPT-4 | - | RAG y generación de texto |
| **Embeddings** | Sentence-BERT | - | Vectorización semántica |
| **NER** | SpaCy | 3.7+ | Extracción de entidades |
| **OCR** | Tesseract | 5.0+ | Reconocimiento de texto |
| **ML Framework** | PyTorch | 2.0+ | Modelos personalizados |
| **Observability** | Arize Phoenix | Latest | Monitoreo de LLMs |

### DevOps e Infraestructura

| Componente | Tecnología | Versión | Propósito |
|------------|-----------|---------|-----------|
| **Containerización** | Docker | 24+ | Empaquetado de servicios |
| **Orquestación** | Docker Compose | 2.0+ | Orquestación local |
| **CI/CD** | GitHub Actions | - | Automatización de pipelines |
| **Reverse Proxy** | NGINX | 1.25+ | Load balancing y SSL |
| **Monitoring** | Prometheus + Grafana | - | Métricas y alertas |

---

## 🚀 Inicio Rápido

### Prerrequisitos

- **Docker** 24.0+ y **Docker Compose** 2.0+
- **Git** para clonar el repositorio
- **8GB RAM** mínimo (16GB recomendado)
- **20GB** de espacio en disco
- **GPU NVIDIA** (opcional, para aceleración)

### Instalación Estándar

#### 1️⃣ Clonar el Repositorio

```powershell
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA.git
cd Sistema-Corporativo-Documental-con-Capacidades-de-IA
```

#### 2️⃣ Configurar Variables de Entorno

```powershell
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env con tus credenciales
notepad .env
```

**Variables críticas a configurar:**

```env
# OpenAI API (requerido para RAG)
OPENAI_API_KEY=sk-...

# Base de datos
POSTGRES_PASSWORD=tu_password_seguro

# MinIO (S3)
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=tu_password_seguro

# JWT Secret
JWT_SECRET_KEY=genera_un_secret_aleatorio_seguro
```

#### 3️⃣ Levantar los Servicios

```powershell
# Modo estándar (CPU)
docker-compose up -d

# Modo GPU (si tienes NVIDIA GPU)
docker-compose -f docker-compose.gpu.yml up -d
```

#### 4️⃣ Verificar el Despliegue

```powershell
# Verificar que todos los contenedores están corriendo
docker ps

# Ver logs del backend
docker logs financia_backend -f
```

#### 5️⃣ Acceder a la Aplicación

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Frontend** | http://localhost:3000 | admin@demo.documental.com / Demo2025! |
| **Backend API** | http://localhost:8000/docs | - |
| **MinIO Console** | http://localhost:9001 | admin / [tu_password] |
| **Phoenix UI** | http://localhost:6006 | - |
| **OpenSearch** | http://localhost:9200 | admin / admin |

### Instalación con GPU (Aceleración NVIDIA)

Para aprovechar la aceleración GPU en OCR y ML:

```powershell
# 1. Instalar NVIDIA Container Toolkit
# Seguir: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# 2. Verificar GPU disponible
nvidia-smi

# 3. Levantar con configuración GPU
docker-compose -f docker-compose.gpu.yml up -d
```

### Primeros Pasos

1. **Login**: Accede a http://localhost:3000 con las credenciales de demo
2. **Subir Documentos**: Ve a "Documentos" → "Subir" y carga tus primeros archivos
3. **Búsqueda**: Prueba la búsqueda híbrida en la barra superior
4. **RAG**: Abre el "Asistente IA" y haz preguntas sobre tus documentos
5. **Dashboard**: Explora las métricas en el panel de administración

### Scripts de Utilidad

```powershell
# Verificar estado del sistema
.\verify_system.ps1

# Reiniciar servicios
docker-compose restart

# Ver logs de todos los servicios
docker-compose logs -f

# Detener todos los servicios
docker-compose down

# Limpiar volúmenes (⚠️ borra datos)
docker-compose down -v
```

---

## 📚 Documentación

### Guías de Usuario

- **[📖 Manual de Usuario](docs/USER_GUIDE.md)** - Guía completa para usuarios finales
- **[🎬 Script de Demo](docs/DEMO_SCRIPT.md)** - Demostración guiada de funcionalidades
- **[🧬 Generador de Datos Sintéticos](docs/SYNTHETIC_DATA_GUIDE.md)** - Cómo generar datos de prueba

### Guías Técnicas

- **[🏗️ Arquitectura del Sistema](docs/ARCHITECTURE.md)** - Diseño técnico detallado
- **[🔧 Guía de Administración](docs/ADMIN_GUIDE.md)** - Configuración y mantenimiento
- **[🚀 Guía de Despliegue](docs/DEPLOYMENT_GUIDE.md)** - Despliegue en producción
- **[📡 Referencia API](docs/API_REFERENCE.md)** - Documentación completa de endpoints

### Guías Especializadas

- **[🔌 Conectores](docs/CONNECTORS_GUIDE.md)** - Integración con SharePoint, SAP DMS, etc.
- **[📊 GraphQL](docs/GRAPHQL_QUICKSTART.md)** - API GraphQL y ejemplos
- **[🔍 SPARQL](docs/SPARQL_EXAMPLES.md)** - Consultas sobre ontología
- **[👁️ Observabilidad Phoenix](docs/PHOENIX_OBSERVABILITY.md)** - Monitoreo de LLMs
- **[⚖️ Compliance y Gobernanza](docs/GOVERNANCE.md)** - Cumplimiento normativo

### Documentación de Desarrollo

- **[🧪 Guía de Testing](docs/IMPLEMENTATION_GUIDE.md)** - Testing y QA
- **[🔐 Análisis de Riesgo](docs/RFP_ANALYSIS.md)** - Análisis de requisitos
- **[📋 Sistema de Validación](docs/VALIDATION_SYSTEM.md)** - Validación de compliance

---

## 🤝 Soporte y Contacto

### Soporte Técnico

- **Email**: financia2030@tefinancia.es
- **Documentación**: [docs/](docs/)
- **Issues**: GitHub Issues (repositorio privado)

### Equipo de Desarrollo

**TeFinancia S.A. - FinancIA 2030 Team**

---

## 📄 Licencia

© 2024-2025 **TeFinancia S.A.** - Todos los derechos reservados

Este software es **propietario** y confidencial. El uso, copia, modificación o distribución no autorizada está estrictamente prohibido.

Para consultas sobre licenciamiento: legal@tefinancia.es

---

## 🎯 Roadmap

### ✅ Completado (v1.0)

- ✅ Pipeline completo de procesamiento documental
- ✅ Búsqueda híbrida (léxica + semántica)
- ✅ RAG con citación obligatoria
- ✅ Análisis de riesgo multidimensional
- ✅ Motor de compliance con EU AI Act
- ✅ Observabilidad con Arize Phoenix
- ✅ Conectores SharePoint y SAP DMS
- ✅ API GraphQL
- ✅ Sistema de anotaciones
- ✅ Comparación de documentos

### 🚧 En Desarrollo (v1.1)

- 🚧 Integración con Microsoft Teams
- 🚧 Workflow de aprobaciones
- 🚧 Firma electrónica
- 🚧 Mobile app (iOS/Android)
- 🚧 Exportación a blockchain

### ⚛️ Planificado (v2.0) - Quantum & GPU Enhancement

**🚀 Plan de Mejora Integral con Computación Cuántica y Aceleración GPU**

Ver documento completo: **[QUANTUM_GPU_ENHANCEMENT_PLAN.md](docs/QUANTUM_GPU_ENHANCEMENT_PLAN.md)**

**Objetivos principales:**

- ⚡ **Aceleración GPU (NVIDIA RTX)**: Embeddings y FAISS-GPU para reducir tiempo de indexado > 80%
- ⚛️ **Computación Cuántica**: Optimización QUBO para deduplicación y clustering (D-Wave + IBM Qiskit + NVIDIA cuQuantum)
- 🧠 **Quantum Machine Learning**: Kernels cuánticos para clasificación avanzada
- 🤖 **RAG Optimizado**: LLMs con contexto mejorado y trazabilidad 100%
- 📊 **Observabilidad Avanzada**: Prometheus + Grafana + Arize Phoenix

**Componentes nuevos (modulares, sin romper app actual):**

1. `gpu-embedding-service` - Aceleración de embeddings con GPU
2. `quantum-dedupe-dwave` - Deduplicación con D-Wave Ocean SDK
3. `quantum-dedupe-ibm` - Deduplicación con IBM Qiskit
4. `qml-classifier-nvidia` - ML cuántico con cuQuantum
5. `rag-enhanced-service` - RAG optimizado con GPU

**Beneficios esperados:**

- 🚀 Ingestión 3-5× más rápida
- 🎯 +15% precisión en deduplicación
- 📉 -20-30% reducción en revisión manual
- ⚛️ Capacidades de investigación cuántica sin hardware externo

### 🔮 Futuro (v3.0+)

- 🔮 Multi-tenancy completo
- 🔮 IA explicable (XAI) avanzada
- 🔮 Federación de búsqueda
- 🔮 Integración con ERP/CRM
- 🔮 Análisis predictivo con quantum computing

---

<div align="center">

**⭐ Si este proyecto te resulta útil, considera darle una estrella ⭐**

Hecho con ❤️ por el equipo de **FinancIA 2030**

</div>
