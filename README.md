# Sistema Corporativo Documental con Capacidades de IA

![Estado](https://img.shields.io/badge/Estado-%20Production%20Ready-brightgreen) ![Versión](https://img.shields.io/badge/Versión-1.0.0-blue) ![RFP Coverage](https://img.shields.io/badge/RFP%20Coverage-100%25-gold)

Plataforma enterprise para ingestión, procesamiento y búsqueda de documentos con IA (OCR, NER, embeddings, RAG) y módulos de cumplimiento (EU AI Act, GDPR). Optimizada para GPU y operación en producción.

Links rápidos: [Inicio rápido](#inicio-rápido)  [Documentación](docs/)  [Diagramas (SVG)](docs/generated-diagrams/)  [Vista interactiva](docs/index.html)

---

## Resumen ejecutivo

Solución endtoend que integra pipelines de ML, búsqueda híbrida (léxica + semántica), almacenamiento de objetos y base vectorial para habilitar casos de uso corporativos: clasificación, extracción de entidades, validación de compliance y análisis de riesgo. Arquitectura modular, observable y escalable con componentes desacoplados.

---

## Arquitectura (visual listo para presentar)

Vista ejecutiva de microservicios:

<img src="docs/generated-diagrams/microservices-overview.svg" alt="Microservices Overview" width="100%" />

Vista de contexto (C4):

<img src="docs/generated-diagrams/c4-context.svg" alt="C4 Context" width="100%" />

Vista de microservicios (C4-Componentes):

<img src="docs/generated-diagrams/c4-component.svg" alt="C4 Components / Microservices" width="100%" />

Vista de contenedores (C4):

<img src="docs/generated-diagrams/c4-container.svg" alt="C4 Container" width="100%" />

Nota: Los SVG se generan automáticamente desde docs/diagrams/ mediante GitHub Actions. Si aún no aparecen, consulta la versión interactiva en docs/index.html.

---

## Características principales

- Ingesta y procesamiento documental a escala (PDF/Office/Imagen) con OCR.
- Búsqueda híbrida + RAG con citación de fuentes y trazabilidad.
- Extracción de entidades (NER) y clasificación automática.
- Módulos de cumplimiento (GDPR, EU AI Act) con auditoría de evidencias.
- Observabilidad de LLMs y métricas operativas (latencia, throughput, errores).
- Despliegue reproducible con Docker Compose; listo para CI/CD.

---

## Stack tecnológico

- Backend: FastAPI (Python 3.11), SQLAlchemy, Celery.
- Frontend: React 18, TypeScript, Vite.
- Datos: PostgreSQL, Qdrant (vectores), Redis, MinIO (S3).
- ML/IA: OpenAI/SBERT, SpaCy, PyTorch.
- DevOps: Docker Compose, GitHub Actions, NGINX.

---

## Inicio rápido

1) Clona el repositorio
`powershell
git clone https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA.git
cd "Sistema-Corporativo-Documental-con-Capacidades-de-IA"
`

2) Configura variables de entorno
`powershell
copy .env.example .env
# Edita .env (OPENAI_API_KEY y demás credenciales)
`

3) Levanta los servicios
`powershell
docker-compose up -d
`
Accesos:
- Frontend: http://localhost:3000
- Backend (OpenAPI): http://localhost:8000/docs

---

## Documentación

- docs/ARCHITECTURE.md  Arquitectura técnica
- docs/ADMIN_GUIDE.md  Guía de administración
- docs/USER_GUIDE.md  Manual de usuario
- docs/API_REFERENCE.md  Referencia API

---

 2024-2025 TeFinancia S.A.  Uso propietario
