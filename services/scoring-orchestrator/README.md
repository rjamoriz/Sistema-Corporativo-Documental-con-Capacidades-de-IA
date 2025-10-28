# 🎯 Scoring Orchestrator Service

Servicio orquestador que combina múltiples modelos ML para generar scoring híbrido de clientes basado en datos estructurados y no estructurados.

## 🎯 Propósito

Coordina llamadas a múltiples servicios ML (SageMaker, Quantum ML, Document Extractor) y genera un score final mediante ensemble, proporcionando decisiones de crédito con explicabilidad completa.

## 🚀 Características

### Orquestación Multi-Modelo

- **Document Feature Extractor**: Extrae features de documentos no estructurados
- **SageMaker Predictor**: Scoring ML clásico (LightGBM/XGBoost)
- **Quantum ML**: Clasificación cuántica con VQC
- **Ensemble Scoring**: Combina predicciones con pesos configurables

### Decisiones de Scoring

| Score | Decisión | Descripción |
|---|---|---|
| 75-100 | `APPROVED` | Aprobación directa |
| 60-74 | `APPROVED_WITH_CONDITIONS` | Aprobación condicional |
| 40-59 | `REVIEW_REQUIRED` | Requiere revisión manual |
| 0-39 | `REJECTED` | Rechazo |

## 📡 API Endpoints

### POST `/score`

Calcula score híbrido de cliente.

**Request:**
```json
{
  "customer_id": "CUST_123",
  "structured_data": {
    "age": 35,
    "income": 45000,
    "credit_history_months": 24,
    "num_operations": 12,
    "amount": 25000,
    "duration": 36
  },
  "document_texts": [
    "Contrato de préstamo por 25.000€...",
    "Email del cliente solicitando extensión..."
  ],
  "use_quantum": true,
  "use_sagemaker": true,
  "explain": true
}
```

**Response:**
```json
{
  "customer_id": "CUST_123",
  "final_score": 76.5,
  "decision": "APPROVED",
  "confidence": 0.85,
  "sagemaker_prediction": {
    "model_name": "SageMaker LightGBM",
    "prediction": 1,
    "probability": 0.82,
    "score": 82.0,
    "confidence": 0.82,
    "execution_time_ms": 45.2,
    "success": true
  },
  "quantum_prediction": {
    "model_name": "Quantum VQC",
    "prediction": 2,
    "confidence": 0.78,
    "score": 78.0,
    "execution_time_ms": 120.5,
    "success": true
  },
  "document_features": {
    "sentiment_score": 0.65,
    "risk_keywords_count": 1,
    "document_completeness": 0.85,
    "confidence": 0.82
  },
  "explanation": {
    "main_factors": [
      "✅ Alta probabilidad de aprobación ML clásico (82%)",
      "✅ Alta confianza en modelo cuántico (78%)",
      "✅ Sentimiento positivo en documentos (0.65)",
      "✅ Documentación completa (85%)"
    ],
    "structured_contribution": 0.5,
    "unstructured_contribution": 0.2,
    "quantum_contribution": 0.3,
    "top_positive_features": [
      {"feature": "income", "impact": 0.15},
      {"feature": "credit_history", "impact": 0.12}
    ],
    "top_negative_features": [
      {"feature": "risk_indicators", "impact": -0.08}
    ]
  },
  "timestamp": "2024-10-28T18:30:00Z",
  "processing_time_ms": 185.7,
  "models_used": ["document_extractor", "sagemaker", "quantum_ml"]
}
```

### GET `/health`
Health check endpoint.

### GET `/metrics`
Prometheus metrics.

### GET `/stats`
Estadísticas del servicio.

## 🔧 Configuración

### Variables de Entorno

```bash
PORT=8010                                                    # Puerto del servicio
DOCUMENT_EXTRACTOR_URL=http://document-feature-extractor:8009
SAGEMAKER_URL=http://sagemaker-predictor:8008
QUANTUM_ML_URL=http://quantum-ml-pennylane:8007
ASTRA_DB_URL=http://astra-vector-db-service:8006
```

## 📊 Algoritmo de Ensemble

### Pesos de Modelos

```python
final_score = (
    0.5 * sagemaker_score +      # 50% - ML clásico
    0.3 * quantum_score +         # 30% - Quantum ML
    0.2 * document_quality_score  # 20% - Docs no estructurados
)
```

### Lógica de Decisión

1. **Extracción de Features Documentales** (si hay documentos)
   - Sentiment, entidades, riesgo, calidad

2. **Predicción SageMaker** (si habilitado)
   - Combina features estructuradas + documentales
   - Genera score y explicación SHAP

3. **Predicción Quantum ML** (si habilitado)
   - Crea embedding de features
   - Clasificación cuántica con VQC

4. **Ensemble Scoring**
   - Weighted average de predicciones
   - Cálculo de confianza
   - Determinación de decisión

5. **Explicación**
   - Factores principales
   - Contribuciones por tipo de dato
   - Top features positivas/negativas

## 📊 Métricas Prometheus

- `scoring_requests_total`: Total de requests de scoring
- `scoring_duration_seconds`: Tiempo de scoring
- `model_calls_total{model, status}`: Llamadas a modelos
- `ensemble_scores`: Distribución de scores finales

## 🐳 Docker

```bash
# Build
docker build -t scoring-orchestrator .

# Run
docker run -p 8010:8010 \
  -e SAGEMAKER_URL=http://sagemaker:8008 \
  -e QUANTUM_ML_URL=http://quantum:8007 \
  scoring-orchestrator
```

## 🧪 Testing

```bash
# Test completo con documentos
curl -X POST http://localhost:8010/score \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "TEST_001",
    "structured_data": {
      "age": 35,
      "income": 50000,
      "credit_history_months": 36,
      "num_operations": 15,
      "amount": 30000,
      "duration": 48
    },
    "document_texts": [
      "Contrato firmado el 15/03/2024 por 30.000€",
      "Cliente con buen historial de pagos"
    ],
    "use_quantum": true,
    "use_sagemaker": true,
    "explain": true
  }'
```

## 🔗 Integración

### Flujo Completo

```
Cliente → Scoring Orchestrator
    ↓
    ├─→ Document Feature Extractor (8009)
    │   └─→ Features documentales
    │
    ├─→ SageMaker Predictor (8008)
    │   └─→ Score ML clásico + SHAP
    │
    ├─→ Quantum ML (8007)
    │   └─→ Score cuántico + confianza
    │
    └─→ Ensemble
        └─→ Score final + decisión + explicación
```

## 🛡️ Características de Seguridad

- **No modifica servicios existentes** - Solo consume APIs
- **Timeouts configurables** - Evita bloqueos
- **Manejo de errores robusto** - Continúa si un modelo falla
- **Validación de inputs** - Pydantic models
- **Logs sin PII** - Solo IDs de clientes

## 📈 Casos de Uso

1. **Scoring de Crédito Híbrido**
   - Combina datos CRM + documentos del cliente
   - Decisión automática con explicación

2. **Evaluación de Riesgo Completa**
   - Análisis de documentos + modelos predictivos
   - Detección de anomalías cuánticas

3. **Due Diligence Automatizada**
   - Calidad documental + scoring financiero
   - Review automático de completitud

4. **Aprobación Inteligente**
   - Múltiples modelos para mayor precisión
   - Explicabilidad completa para compliance

## 🎯 Ventajas del Ensemble

| Ventaja | Descripción |
|---|---|
| **Mayor Precisión** | Combina fortalezas de múltiples modelos |
| **Robustez** | Si un modelo falla, otros compensan |
| **Explainability** | Contribución de cada fuente de datos |
| **Flexibilidad** | Modelos opcionales según caso de uso |
| **Escalabilidad** | Fácil añadir nuevos modelos |

## 📝 Notas Importantes

- ✅ **Servicio independiente** - No modifica otros servicios
- ✅ **Stateless** - No requiere base de datos propia
- ✅ **Async HTTP** - Llamadas paralelas cuando posible
- ✅ **Fault-tolerant** - Maneja fallos de modelos individuales
- ✅ **Observable** - Métricas Prometheus completas
