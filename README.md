# Sistema Corporativo Documental con Capacidades de IA
## FinancIA 2030 — TeFinancia S.A.

![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow)
![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-Proprietary-red)

---

## 📋 Descripción del Proyecto

Sistema corporativo de gestión documental de última generación que integra capacidades avanzadas de **Inteligencia Artificial** para procesamiento, clasificación, búsqueda híbrida, RAG con citación obligatoria y scoring de riesgo multidimensional con explicabilidad total.

**Cliente:** TeFinancia S.A.  
**Proyecto:** FinancIA 2030  
**Estado:** MVP → PRE → PROD

### 🎯 Objetivos Clave

- ✅ **Procesamiento automático** de 100k+ documentos/año multi-formato
- ✅ **IA Responsable** con explicabilidad y supervisión humana
- ✅ **Cumplimiento normativo** total (EU AI Act, GDPR, NIS2)
- ✅ **Alta disponibilidad** (SLA 99.9%) y rendimiento (búsqueda <2s p95)
- ✅ **Seguridad por diseño** con auditoría completa

---

## 📁 Documentación Principal

- 📄 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Arquitectura técnica completa
- 🏛️ [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) — Gobernanza de IA y compliance
- 🔒 [`docs/DPIA.md`](docs/DPIA.md) — Data Protection Impact Assessment

---

## 🗂️ Estructura del Repositorio

```
.
├── backend/                    # Backend FastAPI (en desarrollo)
├── frontend/                   # Frontend React (planificado)
├── data/                       # Datasets sintéticos (pendiente generación)
├── docs/                       # ✅ Documentación completa
│   ├── ARCHITECTURE.md        # ✅ Arquitectura técnica
│   ├── GOVERNANCE.md          # ✅ Gobernanza de IA
│   └── DPIA.md                # ✅ Evaluación de impacto de privacidad
├── infrastructure/             # IaC y Docker (pendiente)
├── scripts/                    # Scripts de utilidad (pendiente)
└── README.md                  # Este archivo
```

---

## 🚀 Estado Actual del Proyecto

### ✅ Completado

- [x] Documentación arquitectónica exhaustiva
- [x] Marco de gobernanza de IA completo
- [x] DPIA y cumplimiento regulatorio documentado
- [x] Especificación técnica de todos los componentes
- [x] Estructura de repositorio definida

### 🚧 En Progreso

- [ ] Implementación del backend (FastAPI + servicios)
- [ ] Setup de infraestructura (Docker Compose)
- [ ] Generación de 200 documentos sintéticos

### 📅 Pendiente

- [ ] Pipeline completo de procesamiento documental
- [ ] Modelos de IA (NER, clasificación, embeddings)
- [ ] Frontend React con TypeScript
- [ ] Pruebas y validación de KPIs
- [ ] Despliegue en entornos DEV/PRE/PROD

---

## 📊 KPIs y Criterios de Aceptación

### Calidad

| KPI | Objetivo | Estado |
|-----|----------|--------|
| OCR precisión | ≥98% | 🎯 Especificado |
| NER F1 score | ≥0.85 | 🎯 Especificado |
| Clasificación accuracy | ≥0.90 | 🎯 Especificado |
| RAG groundedness | ≥95% | 🎯 Especificado |
| Risk correlation | ≥0.70 | 🎯 Especificado |

### Rendimiento

| KPI | Objetivo | Estado |
|-----|----------|--------|
| Búsqueda p95 | ≤2s | 🎯 Especificado |
| Ingesta throughput | ≥10k págs/hora | 🎯 Especificado |
| Disponibilidad | ≥99.9% | 🎯 Especificado |

---

## 📜 Cumplimiento Normativo

| Regulación | Estado | Documentación |
|------------|--------|---------------|
| **EU AI Act 2024** | ✅ Documentado | `docs/GOVERNANCE.md` |
| **GDPR/LOPDGDD** | ✅ DPIA completo | `docs/DPIA.md` |
| **NIS2 Directive** | ✅ Controles definidos | `docs/GOVERNANCE.md` |
| **ISO 27001/27701/42001** | ✅ Alineado | `docs/GOVERNANCE.md` |

---

## 🛠️ Stack Tecnológico

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL 15 + pgvector
- OpenSearch 2.11+
- Apache Kafka 3.6+
- Redis 7.2+
- MinIO (S3-compatible)

### IA/ML
- Tesseract 5 (OCR)
- spaCy (NER)
- sentence-transformers (embeddings)
- BETO/RoBERTa (clasificación)
- OpenAI GPT-4o-mini / Llama-3 (RAG)
- MLflow + DVC + Evidently AI

### Frontend
- React 18 + TypeScript
- shadcn/ui + Tailwind CSS
- React Query + Zustand

### Infraestructura
- Docker + Docker Compose
- Prometheus + Grafana
- OpenTelemetry
- HashiCorp Vault

---

## 📈 Roadmap

### ✅ Fase 1: Fundamentos (T0–T2) — COMPLETADO

- [x] Setup repositorio y documentación
- [x] Arquitectura técnica completa
- [x] Gobernanza de IA y DPIA
- [ ] Generación de datos sintéticos

### 🚧 Fase 2: Core (T2–T6) — EN PROGRESO

- [ ] Pipeline de procesamiento documental
- [ ] Modelos de NER y clasificación
- [ ] Búsqueda híbrida
- [ ] RAG básico

### 📅 Fase 3: Avanzado (T6–T10)

- [ ] Scoring de riesgo multidimensional
- [ ] Motor de compliance
- [ ] Anonimización
- [ ] Frontend completo

### 📅 Fase 4: Producción (T10–T14+)

- [ ] Dashboards de observabilidad
- [ ] Pruebas de rendimiento y seguridad
- [ ] UAT
- [ ] Go-Live PROD

---

## 📞 Contacto

**Proyecto:** FinancIA 2030  
**Cliente:** TeFinancia S.A.  
**Repository:** https://github.com/rjamoriz/Sistema-Corporativo-Documental-con-Capacidades-de-IA

---

## 📜 Licencia

**Copyright © 2025 TeFinancia S.A. Todos los derechos reservados.**

Este software es propiedad exclusiva de TeFinancia S.A. y está protegido por leyes de propiedad intelectual.

---

**🎯 FinancIA 2030 — Transformando la gestión documental con IA Responsable**
