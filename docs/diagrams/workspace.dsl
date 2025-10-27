workspace "Sistema Corporativo Documental con IA" "Sistema de gestión documental enterprise con capacidades de IA responsable" {

    model {
        # Personas
        userFinancial = person "Usuario Financiero" "Analista, Compliance Officer, Ejecutivo de TeFinancia S.A."
        admin = person "Administrador" "Administrador del sistema y gestor de usuarios"
        
        # Software Systems
        dmsSystem = softwareSystem "Sistema Documental IA" "Plataforma de gestión documental con procesamiento inteligente, RAG, y cumplimiento normativo" {
            
            # Containers - Frontend
            webApp = container "React SPA" "Aplicación web de una sola página" "TypeScript, React 18.3, Vite" {
                uiComponents = component "UI Components" "Componentes reutilizables de interfaz" "React + Tailwind CSS"
                stateManagement = component "State Management" "Gestión de estado global" "Zustand"
                apiClient = component "API Client" "Cliente HTTP para backend" "TanStack Query"
                routing = component "Routing" "Navegación de la aplicación" "React Router"
            }
            
            # Containers - Backend
            apiBackend = container "FastAPI Backend" "API principal del sistema" "Python 3.11, FastAPI" {
                authService = component "Authentication Service" "Autenticación y autorización" "OAuth2 + JWT"
                documentService = component "Document Service" "Gestión de documentos" "FastAPI Router"
                searchService = component "Search Service" "Búsqueda híbrida" "FastAPI Router"
                complianceService = component "Compliance Service" "Verificación de cumplimiento" "FastAPI Router"
                riskService = component "Risk Service" "Análisis de riesgo" "FastAPI Router"
            }
            
            # Containers - ML/AI
            mlPipeline = container "ML Pipeline" "Pipeline de procesamiento IA" "PyTorch, Scikit-learn, SpaCy" {
                ocrEngine = component "OCR Engine" "Extracción de texto" "Tesseract, PaddleOCR"
                nerModel = component "NER Model" "Extracción de entidades" "SpaCy"
                classifier = component "Document Classifier" "Clasificación automática" "Random Forest"
                embeddings = component "Embeddings Generator" "Generación de embeddings" "Sentence-BERT"
                explainability = component "Explainability Module" "LIME/SHAP para explicabilidad" "Python"
            }
            
            # Containers - Workers
            celeryWorkers = container "Celery Workers" "Procesamiento asíncrono" "Python, Celery" {
                docProcessor = component "Document Processor" "Procesamiento de documentos" "Celery Task"
                mlInference = component "ML Inference Worker" "Inferencia ML" "Celery Task"
                batchJobs = component "Batch Jobs" "Trabajos programados" "Celery Beat"
            }
            
            # Containers - Databases
            postgres = container "PostgreSQL" "Base de datos relacional" "PostgreSQL 15" "Database"
            vectorDB = container "Qdrant" "Base de datos vectorial" "Qdrant" "Database"
            redis = container "Redis" "Cache y message broker" "Redis 7" "Database"
            objectStorage = container "MinIO" "Almacenamiento de objetos" "MinIO S3-compatible" "Database"
        }
        
        # External Systems
        sharepoint = softwareSystem "SharePoint Online" "Repositorio corporativo Microsoft" "External"
        sapDMS = softwareSystem "SAP DMS" "Sistema de gestión documental SAP" "External"
        ofacAPI = softwareSystem "OFAC Sanctions API" "API de validación de sanciones" "External"
        eurlexAPI = softwareSystem "EUR-Lex API" "Base de datos legislativa de la UE" "External"
        openaiAPI = softwareSystem "OpenAI GPT-4" "Modelos de lenguaje grandes" "External"
        phoenixSystem = softwareSystem "Arize Phoenix" "Plataforma de observabilidad de LLMs" "External"
        
        # Relationships - Users to Containers
        userFinancial -> webApp "Usa"
        admin -> webApp "Administra"
        
        # Relationships - Frontend to Backend
        webApp -> apiBackend "Realiza llamadas API" "HTTPS/JSON"
        apiClient -> authService "Autentica" "REST"
        apiClient -> documentService "Gestiona documentos" "REST"
        apiClient -> searchService "Busca" "REST"
        
        # Relationships - Backend to ML
        documentService -> mlPipeline "Procesa con IA"
        searchService -> embeddings "Genera embeddings"
        complianceService -> explainability "Explica decisiones"
        
        # Relationships - Backend to Workers
        documentService -> celeryWorkers "Encola procesamiento"
        apiBackend -> redis "Usa para caché y mensajes"
        
        # Relationships - Workers to ML
        docProcessor -> ocrEngine "Extrae texto"
        docProcessor -> nerModel "Extrae entidades"
        mlInference -> classifier "Clasifica"
        
        # Relationships - Backend to Databases
        apiBackend -> postgres "Lee/Escribe" "SQL"
        mlPipeline -> vectorDB "Almacena embeddings" "gRPC"
        apiBackend -> objectStorage "Almacena archivos" "S3 API"
        celeryWorkers -> postgres "Actualiza" "SQL"
        
        # Relationships - Backend to External Systems
        apiBackend -> sharepoint "Sincroniza" "Microsoft Graph API"
        apiBackend -> sapDMS "Importa" "GraphQL"
        complianceService -> ofacAPI "Valida" "REST"
        complianceService -> eurlexAPI "Consulta regulaciones" "SPARQL"
        embeddings -> openaiAPI "Genera embeddings" "REST"
        apiBackend -> phoenixSystem "Telemetría" "OpenTelemetry"
    }

    views {
        systemContext dmsSystem "SystemContext" {
            include *
            autoLayout lr
        }

        container dmsSystem "Containers" {
            include *
            autoLayout tb
        }

        component webApp "WebAppComponents" {
            include *
            autoLayout lr
        }

        component apiBackend "BackendComponents" {
            include *
            autoLayout lr
        }

        component mlPipeline "MLPipelineComponents" {
            include *
            autoLayout tb
        }

        styles {
            element "Person" {
                shape Person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
        }
    }

    configuration {
        scope softwaresystem
    }

}
