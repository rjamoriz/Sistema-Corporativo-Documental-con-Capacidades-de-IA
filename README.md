# FinancIA 2030 — Sistema Documental con IA (TeFinancia S.A.)

**Estado:** Scaffold inicial · **Lenguaje:** ES · **Fecha:** 2025‑10‑09

> Este repositorio contiene la base del proyecto para el Sistema Corporativo Documental con Capacidades de IA, alineado con la RFP de TeFinancia, el marco regulatorio europeo (EU AI Act 2024, GDPR/LOPDGDD, NIS2, ISO/ENS) 



## Índice
- [1. Resumen Ejecutivo](#1-resumen-ejecutivo)
- [2. Alcance y Objetivos](#2-alcance-y-objetivos)
- [3. Arquitectura (alto nivel)](#3-arquitectura-alto-nivel)
- [4. Estructura del Repositorio](#4-estructura-del-repositorio)
- [5. Puesta en Marcha Rápida](#5-puesta-en-marcha-rápida)
- [6. KPIs y Criterios de Aceptación](#6-kpis-y-criterios-de-aceptación)
- [7. Cumplimiento y Gobernanza](#7-cumplimiento-y-gobernanza)
- [8. Roadmap](#8-roadmap)
- [9. Contribución y Calidad](#9-contribución-y-calidad)
- [10. Licencia](#10-licencia)

> **Documento base**: ver [`docs/Prompt_Maestro_FinancIA2030.txt`](docs/Prompt_Maestro_FinancIA2030.txt)

---

## 1. Resumen Ejecutivo
Plataforma documental con IA que cubre **ingesta multiformato**, **OCR y extracción/NER**, **clasificación**, **búsqueda híbrida (BM25 + vectorial)** y **RAG con citación obligatoria**, **scoring de riesgo multidimensional** con **explicabilidad**, más **gobernanza/seguridad** y **observabilidad**, cumpliendo EU AI Act y GDPR.

## 2. Alcance y Objetivos
- **MVP → PROD** con entornos DEV/PRE/PROD y SLA objetivo ≥ 99,9%.
- KPIs: OCR ≥ 98%, F1 NER/cláusulas ≥ 0,85, grounded ≥ 95%, p95 búsqueda ≤ 2 s en corpus ≤ 5 M páginas.
- Ver [docs/architecture/system-architecture.mmd](docs/architecture/system-architecture.mmd) para el diagrama (Mermaid).

## 3. Arquitectura (alto nivel)
- **Backend**: FastAPI, PostgreSQL+pgvector, OpenSearch, Kafka, Redis, MinIO, Prometheus/Grafana/OTel.
- **Procesamiento**: Tesseract, PyMuPDF, Whisper, spaCy/Transformers, LangChain, MLflow/DVC/Evidently.
- **Frontend**: React+TypeScript (shadcn/ui, Tailwind, React Query), visor PDF y chat RAG.
- **Seguridad**: SSO OIDC/SAML, MFA, RBAC/ABAC, cifrado TLS/at-rest, logs inmutables 2 años.
- **Cumplimiento**: DPIA, Model Cards, auditoría, gestión de derechos ARSOPL.

## 4. Estructura del Repositorio
```
financia2030/
├─ backend/               # FastAPI + servicios (plantilla)
├─ frontend/              # Base React/TS (pendiente de generar proyecto Vite)
├─ infrastructure/        # docker-compose.yml (plantilla) + notas
├─ scripts/               # setup/start/stop/test (plantillas)
├─ data/                  # datasets sintéticos / golden set (pendiente)
└─ docs/
   ├─ Prompt_Maestro_FinancIA2030.txt
   ├─ architecture/
   │  └─ system-architecture.mmd
   └─ governance/
      ├─ DPIA_template.md
      └─ Model_Card_template.md
```

## 5. Puesta en Marcha Rápida
1. **Requisitos**: Docker 24+, Docker Compose v2, Python 3.11+ (para desarrollo).
2. **Clonar** y crear `.env` a partir de comentarios en `infrastructure/docker-compose.yml`.
3. **Levantar base** (servicios mínimos):  
   ```bash
   docker compose -f infrastructure/docker-compose.yml up -d
   ```
4. **Backend (dev)**:  
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
5. **Probar salud**: `GET http://localhost:8000/health`

## 6. KPIs y Criterios de Aceptación
- OCR ≥ 98%; F1 NER/cláusulas ≥ 0,85; grounded ≥ 95%.
- p95 búsqueda ≤ 2 s; ingestión ≥ 10k págs/h/nodo; disponibilidad ≥ 99,9%.
- Auditoría con `prompt_hash`, `retrieval_ids`; export SIEM; DPIA/Model Cards completas.

## 7. Cumplimiento y Gobernanza
- **Plantillas**: [`docs/governance/DPIA_template.md`](docs/governance/DPIA_template.md), [`docs/governance/Model_Card_template.md`](docs/governance/Model_Card_template.md).
- **Diagrama de gobierno**: ver `docs/architecture/system-architecture.mmd`.
- **Logs inmutables**, **retención 2 años**, **seguridad ENS/ISO** (ver `infrastructure/docker-compose.yml` comentarios).

## 8. Roadmap
- **T0–T2**: taxonomías, datasets sintéticos, pipelines OCR/Extract.
- **T2–T6**: clasificación + indexación; RAG básico; KPIs iniciales.
- **T6–T10**: compliance engine; riesgo+explicabilidad; dashboards; hardening.
- **T10–T14**: PRE integral; pruebas rendimiento/seguridad/LLM; UAT; plan migración.
- **Go‑Live**: PROD + operación y mejora continua (MLOps/LLMOps).

## 9. Contribución y Calidad
- **Estilo**: Black/Flake8/Mypy en Python; ESLint/Prettier en FE.
- **Pruebas**: unitarias, integración y E2E; red-teaming LLM; groundedness eval.
- **ADR**: registra decisiones en `docs/architecture/` (ADR-xxx.md).

## 10. Licencia
A definir por TeFinancia. Licencias de terceros según sus términos.