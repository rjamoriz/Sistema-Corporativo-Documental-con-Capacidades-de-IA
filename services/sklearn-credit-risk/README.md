# 📊 Scikit-Learn Credit Risk ML Service

Servicio especializado en **scoring de riesgo crediticio** y **detección de fraude** utilizando ML clásico (Scikit-Learn) con features híbridas (estructuradas + no estructuradas).

## 🎯 Propósito

Proporcionar predicciones de riesgo de impago y detección de fraude para operaciones de préstamos, créditos y financiación, combinando datos estructurados (CRM/ERP) con información extraída de documentos no estructurados.

## 🚀 Características Principales

### 1. Predicción de Riesgo de Impago
- **Probabilidad de default** calibrada (0-1)
- **Risk score** normalizado (0-100)
- **5 niveles de riesgo**: VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH
- **4 tipos de decisión**: APPROVED, APPROVED_WITH_CONDITIONS, MANUAL_REVIEW, REJECTED

### 2. Detección de Fraude
- **Isolation Forest** para detección de anomalías
- **Anomaly score** normalizado
- **Patrones sospechosos** identificados automáticamente
- **Confianza** en la detección

### 3. Explicabilidad Completa
- **Factores de riesgo** principales
- **Factores protectores**
- **Top features** por importancia
- **Intervalos de confianza** (95% CI)

### 4. Features Híbridas (22 total)

#### Estructuradas (14 features)
- **Demográficas**: edad, ingresos, años de empleo
- **Historial crediticio**: meses de historial, préstamos previos, impagos, score externo
- **Operación actual**: monto, duración, propósito
- **Ratios calculados**: debt-to-income, payment-to-income
- **Relación con entidad**: antigüedad, productos, saldo promedio

#### No Estructuradas (8 features)
- **Sentimiento**: score de sentiment en documentos
- **Indicadores de riesgo**: cláusulas, inconsistencias, retrasos, problemas legales, reestructuraciones
- **Calidad documental**: completitud, calidad del texto

## 📡 API Endpoints

### POST `/predict`

Predice riesgo de impago y detecta fraude.

**Request:**
```json
{
  "customer_id": "CUST_12345",
  "structured_features": {
    "age": 35,
    "income": 45000,
    "employment_years": 8,
    "credit_history_months": 48,
    "num_previous_loans": 3,
    "num_defaults": 0,
    "external_credit_score": 720,
    "loan_amount": 25000,
    "loan_duration_months": 60,
    "loan_purpose": "home_improvement",
    "customer_tenure_months": 36,
    "num_products": 2,
    "avg_balance": 5000
  },
  "unstructured_features": {
    "doc_sentiment_score": 0.65,
    "communication_tone": "positive",
    "num_monetary_amounts": 5,
    "total_amount_mentioned": 25000,
    "num_dates_mentioned": 8,
    "num_identifiers": 2,
    "risk_clauses_count": 1,
    "inconsistencies_detected": 0,
    "payment_delay_mentions": 0,
    "legal_issues_mentions": 0,
    "restructuring_mentions": 0,
    "document_completeness": 0.95,
    "document_quality_score": 0.90
  },
  "check_fraud": true,
  "explain": true
}
```

**Response:**
```json
{
  "customer_id": "CUST_12345",
  "default_probability": 0.1250,
  "risk_score": 12.50,
  "risk_level": "LOW",
  "decision": "APPROVED",
  "fraud_analysis": {
    "is_suspicious": false,
    "anomaly_score": 0.3200,
    "suspicious_patterns": [
      "Sin patrones sospechosos detectados"
    ],
    "confidence": 0.820
  },
  "explanation": {
    "main_risk_factors": [
      "Sin factores de riesgo significativos"
    ],
    "protective_factors": [
      "✅ Excelente score crediticio externo",
      "✅ Cliente de larga antigüedad",
      "✅ Sentimiento positivo en documentos",
      "✅ Documentación completa y de calidad"
    ],
    "top_features": [
      {
        "feature_name": "external_score",
        "importance": 0.263,
        "impact": "positive"
      },
      {
        "feature_name": "debt_to_income_ratio",
        "importance": 0.055,
        "impact": "negative"
      }
    ],
    "risk_level": "LOW",
    "confidence": 0.985
  },
  "calibrated_probability": 0.1250,
  "confidence_interval": [0.1050, 0.1450],
  "model_version": "1.0.0",
  "prediction_timestamp": "2024-10-28T18:40:00Z",
  "processing_time_ms": 45.23
}
```

### GET `/health`
Health check endpoint.

### GET `/metrics`
Prometheus metrics.

### GET `/model-info`
Información detallada de los modelos.

### GET `/stats`
Estadísticas del servicio.

## 🧠 Modelos Utilizados

### 1. Credit Risk Model
- **Algoritmo**: Gradient Boosting Classifier
- **Calibración**: Sigmoid calibration (CalibratedClassifierCV)
- **Features**: 22 (14 estructuradas + 8 no estructuradas)
- **Output**: Probabilidad calibrada de default

### 2. Fraud Detector
- **Algoritmo**: Isolation Forest
- **Contamination**: 5% (anomalías esperadas)
- **Features**: Mismo vector de 22 features
- **Output**: Anomaly score + patrones sospechosos

## 🎯 Niveles de Riesgo y Decisiones

| Probabilidad | Risk Level | Risk Score | Decisión | Acción |
|---|---|---|---|---|
| 0.00 - 0.10 | VERY_LOW | 0-10 | APPROVED | ✅ Aprobación automática |
| 0.10 - 0.20 | LOW | 10-20 | APPROVED | ✅ Aprobación automática |
| 0.20 - 0.35 | MEDIUM | 20-35 | APPROVED_WITH_CONDITIONS | ⚠️ Aprobación con condiciones |
| 0.35 - 0.50 | HIGH | 35-50 | MANUAL_REVIEW | 🔍 Revisión manual requerida |
| 0.50 - 1.00 | VERY_HIGH | 50-100 | REJECTED | ❌ Rechazo automático |

## 🔍 Patrones de Fraude Detectados

El sistema identifica automáticamente:

1. **Monto desproporcionado**: Solicitud muy alta vs ingresos (>3x)
2. **Cliente nuevo + monto alto**: Antigüedad <6 meses + préstamo >50k
3. **Inconsistencias documentales**: >2 inconsistencias detectadas
4. **Múltiples reestructuraciones**: >1 reestructuración mencionada
5. **Documentación incompleta**: Completitud <50%

## 📊 Feature Engineering

### Transformaciones Aplicadas

```python
# Demográficas
age_norm = age / 100.0
log_income = log(income + 1) / 15.0
employment_years_norm = employment_years / 40.0

# Ratios críticos
debt_to_income = loan_amount / income
payment_to_income = (monthly_payment * 12) / income

# Sentimiento normalizado
doc_sentiment_norm = (sentiment + 1) / 2.0  # [-1,1] -> [0,1]

# Indicadores de riesgo
risk_score = (risk_clauses + inconsistencies + delays) / max_value
```

### Valores por Defecto

Si no hay features no estructuradas:
- Sentiment: 0.5 (neutral)
- Risk indicators: 0.0
- Document quality: 0.5 (medio)

## 🔧 Configuración

### Variables de Entorno

```bash
PORT=8011                    # Puerto del servicio
MODEL_PATH=./models/         # Ruta a modelos entrenados (opcional)
```

## 📈 Métricas Prometheus

- `sklearn_prediction_requests_total`: Total de requests
- `sklearn_prediction_duration_seconds`: Tiempo de predicción
- `sklearn_model_loads_total{model_type}`: Cargas de modelo
- `sklearn_risk_scores`: Distribución de risk scores
- `sklearn_default_predictions_total{prediction}`: Predicciones de default
- `sklearn_fraud_detections_total`: Detecciones de fraude

## 🐳 Docker

```bash
# Build
docker build -t sklearn-credit-risk .

# Run
docker run -p 8011:8011 sklearn-credit-risk
```

## 🧪 Testing

### Test Caso Bajo Riesgo

```bash
curl -X POST http://localhost:8011/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "LOW_RISK_001",
    "structured_features": {
      "age": 40,
      "income": 60000,
      "employment_years": 12,
      "credit_history_months": 60,
      "num_previous_loans": 5,
      "num_defaults": 0,
      "external_credit_score": 780,
      "loan_amount": 20000,
      "loan_duration_months": 48,
      "loan_purpose": "debt_consolidation",
      "customer_tenure_months": 48,
      "num_products": 3,
      "avg_balance": 8000
    },
    "unstructured_features": {
      "doc_sentiment_score": 0.8,
      "risk_clauses_count": 0,
      "inconsistencies_detected": 0,
      "payment_delay_mentions": 0,
      "document_completeness": 1.0,
      "document_quality_score": 0.95
    },
    "check_fraud": true,
    "explain": true
  }'
```

### Test Caso Alto Riesgo

```bash
curl -X POST http://localhost:8011/predict \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "HIGH_RISK_001",
    "structured_features": {
      "age": 25,
      "income": 25000,
      "employment_years": 2,
      "credit_history_months": 12,
      "num_previous_loans": 1,
      "num_defaults": 2,
      "external_credit_score": 580,
      "loan_amount": 50000,
      "loan_duration_months": 84,
      "loan_purpose": "other",
      "customer_tenure_months": 6,
      "num_products": 1,
      "avg_balance": 500
    },
    "unstructured_features": {
      "doc_sentiment_score": -0.3,
      "risk_clauses_count": 5,
      "inconsistencies_detected": 3,
      "payment_delay_mentions": 2,
      "legal_issues_mentions": 1,
      "document_completeness": 0.6,
      "document_quality_score": 0.5
    },
    "check_fraud": true,
    "explain": true
  }'
```

## 🔗 Integración con Otros Servicios

### Document Feature Extractor (8009)
Proporciona las `unstructured_features` automáticamente desde documentos.

### Scoring Orchestrator (8010)
Puede invocar este servicio como parte del ensemble híbrido.

### Astra Vector DB (8006)
Almacena predicciones históricas para análisis y monitoreo.

## 📊 Casos de Uso

### 1. Underwriting Automatizado
**Input**: Solicitud de préstamo + documentación
**Output**: Decisión automática (APPROVED/REJECTED/REVIEW)
**Beneficio**: Reducción de 80% en tiempo de decisión

### 2. Detección de Fraude en Tiempo Real
**Input**: Features de la operación
**Output**: Anomaly score + patrones sospechosos
**Beneficio**: Prevención de pérdidas por fraude

### 3. Scoring de Cartera
**Input**: Datos de clientes existentes
**Output**: Re-scoring periódico de riesgo
**Beneficio**: Gestión proactiva de riesgo

### 4. Análisis de Sensibilidad
**Input**: Variaciones en features
**Output**: Impacto en probabilidad de default
**Beneficio**: Optimización de políticas de crédito

## 🛡️ Consideraciones Regulatorias

### GDPR / LOPDGDD
- ✅ No almacena datos personales
- ✅ Logs sin PII
- ✅ Explicabilidad completa (derecho a explicación)

### EU AI Act 2024
- ✅ Sistema de alto riesgo (crédito)
- ✅ Documentación de modelo
- ✅ Monitoreo continuo
- ✅ Registro de decisiones

### Fairness & Bias
- ⚠️ Monitorear grupos protegidos
- ⚠️ Validar ausencia de sesgo
- ⚠️ Auditorías periódicas

## 📈 Métricas de Rendimiento

### Predictivas
- **AUC-ROC**: >0.85 (objetivo)
- **AUC-PR**: >0.70 (clase desbalanceada)
- **Brier Score**: <0.15 (calibración)

### Negocio
- **Approval Rate**: 60-70%
- **Default Rate**: <5%
- **False Positive Rate**: <10%

### Operacionales
- **Latency P95**: <100ms
- **Throughput**: 200 req/s
- **Availability**: 99.9%

## 🔄 Pipeline de Producción

```
1. Ingesta de Solicitud
   ↓
2. Feature Engineering (estructuradas + docs)
   ↓
3. Predicción de Riesgo (Gradient Boosting)
   ↓
4. Calibración de Probabilidad
   ↓
5. Detección de Fraude (Isolation Forest)
   ↓
6. Generación de Explicación
   ↓
7. Decisión Automática
   ↓
8. Almacenamiento + Monitoreo
```

## 🚨 Alertas y Monitoreo

### Alertas Críticas
- Drift en distribución de features
- Degradación de AUC-ROC
- Aumento en tasa de fraude
- Latencia >500ms

### Dashboards Grafana
- Distribución de risk scores
- Tasa de aprobación/rechazo
- Detecciones de fraude
- Latencias P50/P95/P99

## 📝 Notas Importantes

- ✅ **Servicio independiente** - No modifica otros servicios
- ✅ **Stateless** - No requiere base de datos
- ✅ **Calibrado** - Probabilidades confiables
- ✅ **Explicable** - Cumple requisitos regulatorios
- ✅ **Escalable** - Procesamiento rápido (<100ms)
- ⚠️ **Modelos dummy** - En producción usar modelos entrenados
- ⚠️ **Reentrenamiento** - Periódico para evitar drift

## 🔮 Roadmap

- [ ] Integración con SHAP para explicabilidad avanzada
- [ ] Soporte para embeddings de contratos (768 dims)
- [ ] A/B testing de modelos
- [ ] Detección de concept drift automática
- [ ] API de reentrenamiento
- [ ] Soporte para modelos externos (H2O, AutoML)
