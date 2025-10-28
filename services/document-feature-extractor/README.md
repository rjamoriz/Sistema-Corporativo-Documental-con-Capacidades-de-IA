# 📄 Document Feature Extractor Service

Servicio especializado en extraer features de documentos no estructurados para scoring de clientes.

## 🎯 Propósito

Convierte información no estructurada de documentos (PDFs, emails, contratos) en features cuantificables para modelos de scoring.

## 🚀 Características

### Features Extraídas:

#### 1. **Análisis de Sentimiento**
- `sentiment_score`: Score general (-1 a 1)
- `sentiment_positive_ratio`: Ratio de sentimiento positivo

#### 2. **Extracción de Entidades**
- `num_monetary_amounts`: Número de montos monetarios
- `total_amount_mentioned`: Suma total de montos
- `num_dates_mentioned`: Fechas mencionadas
- `num_identifiers`: Identificadores (NIF, CIF, DNI)

#### 3. **Indicadores de Riesgo**
- `risk_keywords_count`: Palabras clave de riesgo
- `payment_delay_mentions`: Menciones de retrasos
- `legal_issues_mentions`: Problemas legales

#### 4. **Calidad Documental**
- `document_completeness`: Completitud (0-1)
- `text_quality_score`: Calidad del texto (0-1)
- `has_structured_data`: Contiene datos estructurados

## 📡 API Endpoints

### POST `/extract-features`

Extrae features de documentos.

**Request:**
```json
{
  "customer_id": "CUST_123",
  "document_texts": [
    "Contrato de préstamo por 25.000€ firmado el 15/03/2024...",
    "Email: Cliente solicita extensión de plazo..."
  ],
  "document_types": ["contract", "email"]
}
```

**Response:**
```json
{
  "customer_id": "CUST_123",
  "sentiment_score": 0.65,
  "sentiment_positive_ratio": 0.75,
  "num_monetary_amounts": 3,
  "total_amount_mentioned": 25000.0,
  "num_dates_mentioned": 5,
  "num_identifiers": 2,
  "risk_keywords_count": 1,
  "payment_delay_mentions": 0,
  "legal_issues_mentions": 0,
  "document_completeness": 0.85,
  "num_documents": 2,
  "avg_document_length": 1250.5,
  "text_quality_score": 0.8,
  "has_structured_data": true,
  "extraction_timestamp": "2024-10-28T18:00:00Z",
  "confidence": 0.82
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
PORT=8009                                    # Puerto del servicio
ASTRA_SERVICE_URL=http://astra:8006         # URL de Astra DB
RAG_SERVICE_URL=http://rag:8005             # URL de RAG service
```

## 📊 Métricas Prometheus

- `extraction_requests_total`: Total de requests de extracción
- `extraction_duration_seconds`: Tiempo de extracción
- `features_extracted_total{feature_type}`: Features extraídas por tipo

## 🐳 Docker

```bash
# Build
docker build -t document-feature-extractor .

# Run
docker run -p 8009:8009 document-feature-extractor
```

## 🧪 Testing

```bash
# Test básico
curl -X POST http://localhost:8009/extract-features \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "TEST_001",
    "document_texts": [
      "Contrato de préstamo por 10.000€ con NIF A12345678",
      "Cliente solicita prórroga debido a retraso temporal"
    ]
  }'
```

## 🔗 Integración con Scoring

Este servicio se integra con:
- **Scoring Orchestrator**: Proporciona features documentales
- **SageMaker Predictor**: Features como input adicional
- **Quantum ML**: Enriquece embeddings con metadata

## 📈 Casos de Uso

1. **Scoring de Crédito**: Analizar contratos y documentación financiera
2. **Evaluación de Riesgo**: Detectar indicadores de riesgo en comunicaciones
3. **Due Diligence**: Evaluar completitud y calidad documental
4. **Compliance**: Identificar problemas legales o regulatorios

## 🛡️ Seguridad

- No almacena documentos originales
- Solo procesa texto, no archivos binarios
- Métricas agregadas sin PII
- Logs sin información sensible

## 📝 Notas

- Servicio **independiente** - no modifica otros servicios
- **Stateless** - no requiere base de datos
- **Escalable** - puede procesarse en paralelo
- **Extensible** - fácil añadir nuevas features
