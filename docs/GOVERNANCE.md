# Marco de Gobernanza de IA — FinancIA 2030
## Política de IA Responsable y Cumplimiento Regulatorio

**Versión:** 1.0  
**Fecha:** 2025-10-09  
**Aprobado por:** Comité de Ética de IA  
**Próxima revisión:** 2026-01-09

---

## 1. PROPÓSITO Y ALCANCE

Este documento establece el marco de gobernanza para el desarrollo, despliegue y operación de sistemas de Inteligencia Artificial en el Sistema Corporativo Documental de TeFinancia S.A., garantizando:

- **Cumplimiento normativo** con EU AI Act 2024, GDPR/LOPDGDD, Data Governance Act, NIS2
- **IA Responsable** con principios de transparencia, equidad, explicabilidad y sostenibilidad
- **Gestión de riesgos** sistemática y documentada
- **Auditoría y trazabilidad** total de decisiones automatizadas

**Alcance:** Todos los sistemas de ML/IA del proyecto, incluyendo:
- Modelos de NER y clasificación
- Sistemas de embeddings y búsqueda semántica
- LLMs para RAG y explicabilidad
- Modelos de scoring de riesgo

---

## 2. MARCO NORMATIVO

### 2.1 EU AI Act 2024

#### Clasificación de Riesgo

| Sistema IA | Nivel de Riesgo | Justificación | Obligaciones |
|-----------|----------------|---------------|--------------|
| **NER & Clasificación** | Limitado | Procesamiento documental sin decisiones de alto impacto | Transparencia básica, documentación |
| **Scoring de Riesgo** | Alto | Evaluación automatizada que afecta decisiones financieras/legales | DPIA, human oversight, explicabilidad, auditoría continua, registros de calidad |
| **RAG / Asistente** | Alto | Asesoramiento que puede influir en decisiones contractuales | Transparencia obligatoria, supervisión humana, logs completos |
| **Búsqueda Semántica** | Mínimo | Herramienta de recuperación sin decisión automatizada | Documentación técnica |

#### Obligaciones para Sistemas de Alto Riesgo

✅ **Implementadas:**

1. **Sistema de Gestión de Riesgos**
   - Identificación y análisis de riesgos conocidos y previsibles
   - Estimación y evaluación de riesgos emergentes
   - Adopción de medidas de gestión de riesgos
   - Revisión trimestral

2. **Gobernanza de Datos**
   - Datasets de entrenamiento documentados (DVC)
   - Criterios de calidad verificables
   - Detección y mitigación de sesgos
   - Trazabilidad completa (data lineage)

3. **Documentación Técnica**
   - Model Cards para cada modelo
   - Especificaciones de funcionamiento
   - Limitaciones y casos de uso
   - Métricas de rendimiento

4. **Transparencia y Provision de Información**
   - Notificación clara cuando interactúa con IA
   - Explicación de decisiones (SHAP/LIME)
   - Información sobre capacidades y limitaciones

5. **Supervisión Humana (Human-in-the-Loop)**
   - HITL obligatorio para decisiones de scoring < 80% confianza
   - Capacidad de override manual
   - Monitorización continua

6. **Precisión, Robustez y Ciberseguridad**
   - Test suites exhaustivos
   - Adversarial testing (jailbreak, prompt injection)
   - Monitorización de drift
   - Hardening de infraestructura

7. **Registro y Logs**
   - Logs inmutables con retención ≥2 años
   - Trazabilidad: versión modelo + input hash + output
   - Exportación a sistemas externos (SIEM)

### 2.2 GDPR/LOPDGDD

#### Principios Aplicados

1. **Licitud, Lealtad y Transparencia**
   - Base legal: consentimiento + interés legítimo + obligación legal
   - Información clara en política de privacidad
   - Avisos en punto de captura

2. **Limitación de Finalidad**
   - Finalidades: gestión documental, compliance, análisis de riesgo
   - Prohibición de reutilización incompatible

3. **Minimización de Datos**
   - Solo datos necesarios para la finalidad
   - Anonimización cuando sea posible
   - Pseudonimización para analytics

4. **Exactitud**
   - Procedimientos de rectificación
   - Validación en captura
   - Actualización periódica

5. **Limitación del Plazo de Conservación**
   - Políticas de retención por tipo de documento
   - Borrado automático al vencimiento
   - Excepciones por obligación legal

6. **Integridad y Confidencialidad**
   - Cifrado TLS 1.3 + AES-256
   - Control de acceso RBAC/ABAC
   - Backups cifrados

7. **Responsabilidad Proactiva**
   - DPIA realizada
   - Registro de actividades de tratamiento
   - Evaluaciones periódicas

#### Derechos de los Interesados (ARSOPL)

| Derecho | Procedimiento | Plazo |
|---------|--------------|-------|
| **Acceso** | Portal self-service + solicitud formal | 1 mes |
| **Rectificación** | Formulario web + validación | 1 mes |
| **Supresión** | Análisis de base legal + ejecución | 1 mes |
| **Oposición** | Evaluación de motivos legítimos | 1 mes |
| **Portabilidad** | Export JSON/CSV/PDF de datos | 1 mes |
| **Limitación** | Marcado de restricción en BBDD | Inmediato |

#### DPIA (Data Protection Impact Assessment)

**Obligatoriedad:** SÍ  
**Motivo:** Evaluación sistemática con decisiones automatizadas de alto riesgo

**Contenido mínimo:**
- Descripción sistemática del tratamiento
- Necesidad y proporcionalidad
- Evaluación de riesgos (probabilidad × impacto)
- Medidas de mitigación
- Consulta al DPO

**Frecuencia de revisión:** Anual o cuando cambios significativos

### 2.3 NIS2 Directive

#### Medidas de Ciberseguridad

✅ **Controles Técnicos:**
- Análisis de riesgos y políticas de seguridad
- Gestión de incidentes (CERT/CSIRT)
- Continuidad de negocio y DR (RPO 1h, RTO 4h)
- Seguridad en la cadena de suministro (SCA)
- Cifrado y control de acceso
- MFA obligatorio para accesos privilegiados

✅ **Controles de Gestión:**
- Formación en ciberseguridad
- Notificación de incidentes graves (24h a autoridad)
- Evaluaciones de efectividad anuales
- Responsable designado (CISO)

### 2.4 ISO/IEC 27001, 27701, 42001

#### Alineamiento de Controles

| Control ISO 27001 | Implementación FinancIA 2030 |
|-------------------|------------------------------|
| A.5.1 Políticas | Política de IA Responsable aprobada |
| A.8.2 Clasificación | 3 niveles: público, interno, confidencial |
| A.9.2 Control de acceso | RBAC + ABAC + MFA |
| A.12.3 Backup | Diario completo + incremental horario |
| A.18.1 Requisitos legales | Matriz de cumplimiento actualizada |

| Control ISO 42001 (AI) | Implementación |
|------------------------|----------------|
| 5.2 Política de IA | Documento aprobado y comunicado |
| 6.1 Gestión de riesgos IA | Matriz de riesgos + revisión trimestral |
| 7.2 Competencia | Formación obligatoria en IA ética |
| 8.2 Impacto de sistemas IA | AIIA (AI Impact Assessment) por sistema |

---

## 3. ESTRUCTURA DE GOBERNANZA

### 3.1 Comité de Ética de IA

**Composición:**
- CTO (Presidente)
- DPO (Data Protection Officer)
- CISO (Chief Information Security Officer)
- Legal & Compliance Manager
- AI/ML Lead Engineer
- Representante de usuarios

**Responsabilidades:**
- Aprobar políticas y directrices
- Revisar sistemas de alto riesgo antes de despliegue
- Evaluar incidentes éticos o de sesgo
- Decisiones sobre casos límite
- Auditorías trimestrales

**Frecuencia:** Reuniones mensuales + extraordinarias

### 3.2 Matriz RACI

| Actividad | Comité IA | AI Engineer | Legal | DPO | CISO | Auditor |
|-----------|-----------|-------------|-------|-----|------|---------|
| Política de IA | A | C | C | I | I | I |
| Desarrollo de modelo | I | R | C | C | I | - |
| DPIA | C | I | C | R | C | I |
| Despliegue PROD | A | R | C | C | C | - |
| Monitorización drift | I | R | I | I | I | C |
| Auditoría anual | I | C | C | C | C | R |
| Gestión de incidentes | C | R | C | C | R | I |

**Leyenda:** R=Responsable, A=Aprobador, C=Consultado, I=Informado

### 3.3 Registro de Sistemas IA

| ID | Sistema | Tipo | Riesgo | DPIA | Model Card | Estado |
|----|---------|------|--------|------|------------|--------|
| AI-001 | NER Extractor | ML | Limitado | N/A | ✅ | Prod |
| AI-002 | Doc Classifier | ML | Limitado | N/A | ✅ | Prod |
| AI-003 | Risk Scorer | ML | **Alto** | ✅ | ✅ | Pre |
| AI-004 | RAG Assistant | LLM | **Alto** | ✅ | ✅ | Pre |
| AI-005 | Semantic Search | Embedding | Mínimo | N/A | ✅ | Prod |

---

## 4. MODEL CARDS (ISO/IEC 23894)

### 4.1 Template

```markdown
# Model Card: [Nombre del Modelo]

## Detalles del Modelo
- **Nombre:** [nombre_modelo]
- **Versión:** [x.y.z]
- **Fecha de entrenamiento:** [YYYY-MM-DD]
- **Desarrollado por:** [equipo]
- **Tipo:** [clasificación / NER / embedding / LLM]
- **Arquitectura:** [BERT / spaCy / transformer]

## Uso Previsto
- **Casos de uso:** [descripción]
- **Usuarios objetivo:** [gestores / compliance / auditoría]
- **Casos de uso NO previstos:** [usos prohibidos]

## Datos de Entrenamiento
- **Dataset:** [nombre y versión]
- **Tamaño:** [N documentos / tokens]
- **Distribución:** [clases balanceadas / desbalanceadas]
- **Idiomas:** [ES / EN / CA...]
- **Período temporal:** [YYYY a YYYY]
- **Sesgo conocido:** [descripción]

## Métricas de Rendimiento
| Métrica | Train | Validation | Test |
|---------|-------|------------|------|
| Accuracy | 0.XX | 0.XX | 0.XX |
| Precision | 0.XX | 0.XX | 0.XX |
| Recall | 0.XX | 0.XX | 0.XX |
| F1 | 0.XX | 0.XX | 0.XX |

**Desagregado por segmento:**
- [Segmento A]: F1 = 0.XX
- [Segmento B]: F1 = 0.XX

## Consideraciones Éticas
- **Equidad:** [análisis de disparate impact]
- **Privacidad:** [técnicas de protección aplicadas]
- **Transparencia:** [explicabilidad disponible]

## Limitaciones
- [Limitación 1]
- [Limitación 2]
- [Limitación 3]

## Recomendaciones de Uso
- Umbral de confianza mínimo: [0.X]
- Supervisión humana: [siempre / cuando confidence < X]
- Frecuencia de reentrenamiento: [trimestral / anual]

## Monitorización
- **Drift detection:** [Evidently AI cada 24h]
- **Alertas configuradas:** [accuracy < 0.X, data drift > Y]
- **Última evaluación:** [YYYY-MM-DD]
- **Estado:** [✅ OK / ⚠️ Warning / ❌ Critical]

## Contacto
- **Owner:** [nombre]
- **Email:** [email]
```

### 4.2 Ejemplo: Risk Scoring Model

Ver archivo: `/docs/model_cards/risk_scorer_v1.0.md`

---

## 5. GESTIÓN DE RIESGOS IA

### 5.1 Matriz de Riesgos

| ID | Riesgo | Probabilidad | Impacto | Nivel | Mitigación | Owner |
|----|--------|--------------|---------|-------|------------|-------|
| R-001 | Sesgo en clasificación | Media | Alto | **Alto** | Auditoría de datos, métricas por segmento, HITL | AI Lead |
| R-002 | Alucinaciones en RAG | Media | Alto | **Alto** | Prompt engineering, citación obligatoria, verificación | AI Lead |
| R-003 | Drift de modelos | Alta | Medio | **Alto** | Monitorización continua (Evidently), alertas | MLOps |
| R-004 | Fuga de PII | Baja | Muy Alto | **Alto** | Presidio, DLP, logs sanitizados | CISO |
| R-005 | Prompt injection | Media | Alto | **Alto** | Input sanitization, guardrails, rate limiting | CISO |
| R-006 | Decisiones inexplicables | Baja | Alto | **Medio** | SHAP/LIME, evidencias por dimensión | AI Lead |
| R-007 | Disponibilidad | Baja | Alto | **Medio** | HA, DR, SLA 99.9% | Ops |

**Niveles:**  
- **Crítico:** Probabilidad Alta + Impacto Muy Alto  
- **Alto:** P.Alta+I.Alto o P.Media+I.MuyAlto  
- **Medio:** Resto combinaciones relevantes  
- **Bajo:** P.Baja+I.Bajo

### 5.2 Plan de Mitigación de Riesgos

#### R-001: Sesgo en Clasificación

**Mitigaciones:**
1. **Datos de entrenamiento:**
   - Dataset balanceado por clases
   - Sobremuestreo de clases minoritarias (SMOTE)
   - Validación de distribución por segmentos

2. **Evaluación:**
   - Métricas desagregadas por tipo de documento
   - Fairness metrics (disparate impact, equal opportunity)
   - Test set estratificado

3. **Operación:**
   - Monitorización de distribución de predicciones
   - Alertas de cambio significativo
   - HITL para casos de baja confianza (<0.8)

#### R-002: Alucinaciones en RAG

**Mitigaciones:**
1. **Prompt engineering:**
   - Instrucción explícita: "responde SOLO con contexto"
   - Template con anti-alucinación
   - Temperature muy baja (0.1)

2. **Verificación:**
   - Post-procesamiento: verificar que cada afirmación tiene cita
   - Reranking con modelo cross-encoder
   - Lista blanca de fuentes aprobadas

3. **Supervisión:**
   - Flag de respuestas sin fuentes para revisión
   - Feedback loop con usuarios expertos

#### R-004: Fuga de PII

**Mitigaciones:**
1. **Prevención:**
   - Microsoft Presidio en pipelines de procesamiento
   - Anonimización antes de analytics
   - Pseudonimización reversible con clave en Vault

2. **Detección:**
   - DLP (Data Loss Prevention) en egreso
   - Logs sanitizados automáticamente
   - Alertas de patrones sospechosos (IBAN, DNI en responses)

3. **Respuesta:**
   - Protocolo de notificación de brecha (72h AEPD)
   - Revocación de credenciales comprometidas
   - Post-mortem obligatorio

---

## 6. EXPLICABILIDAD Y TRANSPARENCIA

### 6.1 Niveles de Explicación

| Audiencia | Nivel | Contenido | Formato |
|-----------|-------|-----------|---------|
| **Usuario final** | Alto nivel | "Este documento se clasificó como X por contener cláusulas Y" | UI tooltip |
| **Revisor legal** | Medio | Evidencias específicas (páginas, snippets) + score por dimensión | Dashboard |
| **Auditor** | Técnico | SHAP values, feature importance, linaje completo | Report PDF |
| **Ingeniero** | Debug | Logs completos, embeddings, activaciones intermedias | Logs JSON |

### 6.2 Técnicas Aplicadas

#### 6.2.1 Clasificación (BETO)

**Método:** Attention weights + SHAP

```python
# Palabras más influyentes en la decisión
explanation = {
    "predicted_class": "contrato_prestamo_personal",
    "confidence": 0.92,
    "top_features": [
        {"token": "préstamo", "weight": 0.35},
        {"token": "TAE", "weight": 0.28},
        {"token": "amortización", "weight": 0.19}
    ]
}
```

#### 6.2.2 Risk Scoring

**Método:** Reglas + evidencias por dimensión

```json
{
  "overall_score": 68,
  "breakdown": {
    "legal": {
      "score": 45,
      "weight": 0.25,
      "findings": [
        {
          "issue": "Cláusula de jurisdicción ambigua",
          "severity": "medium",
          "evidence": {
            "document_id": "uuid",
            "page": 12,
            "text": "Las partes se someten... [snippet]"
          }
        }
      ]
    },
    "financial": { ... }
  }
}
```

#### 6.2.3 RAG

**Método:** Citación obligatoria

```
Respuesta: El préstamo tiene un TAE del 7.5% según la sección 3.2 del contrato.

Fuentes:
- [Contrato de Préstamo Personal - Juan Pérez, Página 3]
- [Anexo de Condiciones Financieras, Página 1]
```

---

## 7. SOSTENIBILIDAD E IMPACTO AMBIENTAL

### 7.1 Huella de Carbono

**Objetivo:** Reducir emisiones de CO₂ en un 20% anual

**Medición:**
- MLCo2 Impact para entrenamientos
- Green Algorithms Calculator para inferencias
- Reporte trimestral

**Acciones:**
- Entrenar en horas valle (energía renovable)
- Optimizar modelos (quantization, distillation)
- Reutilizar modelos pre-entrenados
- Infraestructura en DCs con PUE <1.3

### 7.2 Métricas

| Métrica | Q1 2025 | Q2 2025 | Objetivo 2025 |
|---------|---------|---------|---------------|
| kgCO₂e por entrenamiento | 15 | 12 | <10 |
| kgCO₂e por 1M inferencias | 0.5 | 0.4 | <0.3 |
| % energía renovable | 60% | 70% | >80% |

---

## 8. AUDITORÍA Y TRAZABILIDAD

### 8.1 Logs Obligatorios

```json
{
  "id": "uuid",
  "timestamp": "2025-10-09T10:30:45Z",
  "user_id": "uuid",
  "action": "rag.query",
  "resource_type": "document",
  "resource_id": "uuid",
  "metadata": {
    "model_version": "gpt-4o-mini-2024-07-18",
    "prompt_hash": "sha256:abc123...",
    "retrieval_ids": ["doc1", "doc2"],
    "response_tokens": 250,
    "citations_count": 2,
    "processing_time_ms": 1850,
    "confidence": 0.89
  },
  "result": "success",
  "ip": "10.0.1.50",
  "user_agent": "Mozilla/5.0..."
}
```

### 8.2 Retención y Exportación

- **Retención:** 2 años mínimo (regulatorio), 5 años histórico
- **Formato exportación:** JSON Lines
- **Destino:** SIEM (Splunk/ELK) + S3 Glacier para archivo
- **Integridad:** Checksums SHA-256 + firma digital

### 8.3 Alertas Automáticas

| Evento | Umbral | Acción |
|--------|--------|--------|
| Intentos fallidos de login | ≥5 en 10min | Bloqueo temporal + notificación CISO |
| Acceso a docs confidenciales | Fuera horario laboral | Revisión manual + log detallado |
| Drift de modelo | Accuracy < 80% | Alerta a AI Lead + HITL obligatorio |
| PII en response | Detección Presidio | Block response + incident ticket |
| Latencia anómala | p99 > 10s | Escalado automático + notificación Ops |

---

## 9. FORMACIÓN Y CONCIENCIACIÓN

### 9.1 Plan de Formación

| Audiencia | Módulo | Duración | Frecuencia |
|-----------|--------|----------|------------|
| **Todo el personal** | IA Responsable 101 | 2h | Anual |
| **Desarrolladores** | Secure AI Development | 8h | Anual |
| **Usuarios RAG** | Uso Seguro del Asistente | 1h | Onboarding |
| **Legal/Compliance** | Regulación IA (EU AI Act) | 4h | Semestral |
| **Gestión** | Gobernanza de IA | 3h | Anual |

### 9.2 Materiales

- Guías rápidas (one-pagers)
- Videos tutoriales
- Sandbox de pruebas
- Casos de uso reales
- Quiz de evaluación

---

## 10. REGULATORY INTELLIGENCE

### 10.1 Monitorización de Cambios Normativos

**Fuentes:**
- EUR-Lex API (legislación EU)
- AEPD boletines
- ISO updates
- Industry consortia (AI Alliance, Partnership on AI)

**Proceso:**
1. Suscripción a feeds RSS + webhooks
2. Análisis de impacto por Legal
3. Gap analysis vs. políticas actuales
4. Plan de adaptación si procede
5. Actualización de documentación

**Responsable:** Legal & Compliance Manager  
**Revisión:** Trimestral

### 10.2 Próximas Regulaciones Relevantes

| Regulación | Estado | Impacto Esperado | Fecha Límite |
|------------|--------|------------------|--------------|
| EU AI Liability Directive | Propuesta | Responsabilidad civil por IA | 2026 Q2 |
| EU AI Act - Implementing Acts | En desarrollo | Requisitos técnicos detallados | 2025-2027 |
| ISO 42001 Certification | Disponible | Certificación opcional | N/A |

---

## 11. INCIDENTES Y GESTIÓN DE CRISIS

### 11.1 Protocolo de Respuesta

**Severidades:**

| Nivel | Descripción | Respuesta | Notificación |
|-------|-------------|-----------|--------------|
| **S1 - Crítico** | Fuga masiva de PII, decisión errónea con daño grave | Inmediata, 24/7 | CEO, DPO, AEPD (72h) |
| **S2 - Alto** | Sesgo detectado en producción, alucinación documentada | <4h, horario laboral | Comité IA, Legal |
| **S3 - Medio** | Drift significativo, latencia elevada | <24h | AI Lead, Ops |
| **S4 - Bajo** | Incidencias menores | <7 días | Ticket estándar |

**Pasos:**
1. **Detección:** Automatizada (alertas) o manual (report)
2. **Contención:** Rollback modelo, desactivar feature, HITL forzado
3. **Investigación:** Root cause analysis, logs, reproducción
4. **Remediación:** Fix + test + despliegue
5. **Post-mortem:** Documento de lecciones aprendidas
6. **Prevención:** Actualizar controles, tests, documentación

### 11.2 Registro de Incidentes

| ID | Fecha | Severidad | Sistema | Descripción | Estado | Owner |
|----|-------|-----------|---------|-------------|--------|-------|
| INC-001 | 2025-09-15 | S3 | Classifier | Drift detectado en "poliza_seguro" | Cerrado | AI Lead |
| INC-002 | 2025-10-01 | S2 | RAG | Respuesta sin citas válidas | Cerrado | AI Lead |

---

## 12. REVERSIBILIDAD Y PORTABILIDAD

### 12.1 Exportación de Datos

**Formato:** JSON Lines + CSV + PDF (según tipo)

**Contenido obligatorio:**
- Todos los documentos originales (MinIO)
- Metadatos estructurados (PostgreSQL dump)
- Embeddings (formato numpy .npy)
- Modelos entrenados (ONNX + PyTorch .pth)
- Logs de auditoría (JSON Lines)
- Configuraciones (YAML/JSON)
- Documentación (Markdown → PDF)

**Procedimiento:**
```bash
# Script de exportación completa
./scripts/export_all_data.sh --output /mnt/export --format archive

# Verificación de integridad
sha256sum -c checksums.txt
```

**Plazo máximo:** 30 días desde solicitud

### 12.2 Migración a Otro Sistema

**Garantías:**
- APIs estándar (REST OpenAPI 3.0)
- Formatos abiertos (JSON, CSV, PDF, ONNX)
- Documentación completa de esquemas
- Scripts de conversión si formatos propietarios
- Soporte durante migración (90 días post-fin contrato)

---

## 13. MÉTRICAS DE GOBERNANZA

### 13.1 KPIs de Cumplimiento

| KPI | Objetivo | Actual | Estado |
|-----|----------|--------|--------|
| Model Cards completados | 100% | 100% | ✅ |
| DPIA para sistemas alto riesgo | 100% | 100% | ✅ |
| Formación obligatoria completada | 100% | 85% | ⚠️ |
| Auditorías planificadas realizadas | 100% | 100% | ✅ |
| Incidentes S1/S2 sin resolver >30d | 0 | 0 | ✅ |
| Drift detection uptime | >99% | 99.8% | ✅ |

### 13.2 Dashboard de Gobernanza

**Ubicación:** `https://financia.tefinancia.local/governance`

**Paneles:**
- Estado de sistemas IA (verde/amarillo/rojo)
- Métricas de riesgo agregadas
- Cumplimiento normativo (% completitud)
- Incidentes recientes
- Formaciones pendientes
- Próximas auditorías

---

## 14. APÉNDICES

### Apéndice A: Checklist de Lanzamiento

- [ ] DPIA completada y aprobada por DPO
- [ ] Model Card publicado
- [ ] Tests de robustez (adversarial) pasados
- [ ] Métricas de equidad validadas
- [ ] Explicabilidad implementada y probada
- [ ] HITL configurado
- [ ] Monitorización de drift activa
- [ ] Logs y auditoría operativos
- [ ] Formación a usuarios impartida
- [ ] Documentación técnica y de usuario entregada
- [ ] Plan de rollback definido
- [ ] Aprobación del Comité de IA obtenida

### Apéndice B: Contactos Clave

| Rol | Nombre | Email | Teléfono |
|-----|--------|-------|----------|
| DPO | [Nombre] | dpo@tefinancia.es | +34 XXX |
| CISO | [Nombre] | ciso@tefinancia.es | +34 XXX |
| AI Lead | [Nombre] | ai-lead@tefinancia.es | +34 XXX |
| Legal | [Nombre] | legal@tefinancia.es | +34 XXX |

### Apéndice C: Glosario de Términos

- **Drift:** Cambio en la distribución de datos que degrada el rendimiento del modelo
- **HITL:** Human-in-the-Loop, supervisión humana de decisiones automatizadas
- **Model Card:** Documentación estandarizada de modelos de ML
- **RAG:** Retrieval-Augmented Generation, técnica de LLM con retrieval
- **SHAP:** SHapley Additive exPlanations, método de explicabilidad

---

**Documento controlado — Aprobado por Comité de Ética de IA**  
**Próxima revisión:** 2026-01-09  
**Historial de cambios:** Ver `/docs/governance/CHANGELOG.md`
