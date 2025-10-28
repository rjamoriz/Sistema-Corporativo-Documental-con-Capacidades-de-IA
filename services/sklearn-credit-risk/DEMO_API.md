# 🎯 Demo API - Credit Card Model

API de demostración para probar el modelo de tarjetas de crédito desde el frontend con un solo click.

## 🚀 Iniciar Demo API

```bash
cd services/sklearn-credit-risk
python demo_api.py
```

La API estará disponible en: `http://localhost:8012`

## 📡 Endpoints Disponibles

### GET `/`
Información del servicio

### GET `/health`
Health check

### GET `/demo-cases`
Retorna 3 casos de ejemplo pre-configurados:
- **low_risk**: Cliente de bajo riesgo
- **medium_risk**: Cliente de riesgo medio
- **high_risk**: Cliente de alto riesgo

### POST `/predict`
Predice riesgo de default para un cliente

**Request Body:**
```json
{
  "age": 35,
  "gender": "M",
  "owns_car": "Y",
  "owns_house": "Y",
  "no_of_children": 2,
  "net_yearly_income": 150000,
  "no_of_days_employed": 2000,
  "occupation_type": "Core staff",
  "total_family_members": 4,
  "migrant_worker": 0,
  "yearly_debt_payments": 25000,
  "credit_limit": 50000,
  "credit_limit_used_pct": 65,
  "credit_score": 720,
  "prev_defaults": 0,
  "default_in_last_6months": 0
}
```

**Response:**
```json
{
  "customer_id": "DEMO_20241028190524",
  "default_probability": 0.0523,
  "risk_score": 5.23,
  "decision": "APPROVED",
  "is_fraud_suspicious": false,
  "fraud_score": 0.3245,
  "risk_level": "LOW",
  "main_factors": [
    "✅ Perfil de bajo riesgo",
    "✅ Excelente credit score (720)"
  ],
  "model_version": "20251028_190524",
  "timestamp": "2024-10-28T19:05:24.123456Z"
}
```

## 🎨 Integración con Frontend

### Ejemplo con JavaScript/Fetch

```javascript
// Obtener casos de demo
async function getDemoCases() {
  const response = await fetch('http://localhost:8012/demo-cases');
  const cases = await response.json();
  return cases;
}

// Hacer predicción
async function predictRisk(customerData) {
  const response = await fetch('http://localhost:8012/predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(customerData)
  });
  
  const result = await response.json();
  return result;
}

// Ejemplo de uso
async function demoLowRisk() {
  const cases = await getDemoCases();
  const result = await predictRisk(cases.low_risk.data);
  
  console.log(`Decisión: ${result.decision}`);
  console.log(`Risk Score: ${result.risk_score}%`);
  console.log(`Factores: ${result.main_factors.join(', ')}`);
}
```

### Ejemplo con React

```jsx
import { useState } from 'react';

function CreditCardDemo() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const testLowRisk = async () => {
    setLoading(true);
    try {
      // Obtener casos de demo
      const casesRes = await fetch('http://localhost:8012/demo-cases');
      const cases = await casesRes.json();
      
      // Hacer predicción
      const predRes = await fetch('http://localhost:8012/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cases.low_risk.data)
      });
      
      const prediction = await predRes.json();
      setResult(prediction);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="credit-card-demo">
      <h2>🎯 Demo Modelo de Tarjetas de Crédito</h2>
      
      <button onClick={testLowRisk} disabled={loading}>
        {loading ? 'Procesando...' : 'Probar Cliente Bajo Riesgo'}
      </button>
      
      {result && (
        <div className="result-card">
          <h3>Resultado</h3>
          <p><strong>Decisión:</strong> {result.decision}</p>
          <p><strong>Risk Score:</strong> {result.risk_score}%</p>
          <p><strong>Nivel de Riesgo:</strong> {result.risk_level}</p>
          <p><strong>Fraude Sospechoso:</strong> {result.is_fraud_suspicious ? 'Sí' : 'No'}</p>
          
          <h4>Factores Principales:</h4>
          <ul>
            {result.main_factors.map((factor, i) => (
              <li key={i}>{factor}</li>
            ))}
          </ul>
          
          <p><small>Modelo: {result.model_version}</small></p>
        </div>
      )}
    </div>
  );
}

export default CreditCardDemo;
```

### Ejemplo con Vue.js

```vue
<template>
  <div class="credit-card-demo">
    <h2>🎯 Demo Modelo de Tarjetas de Crédito</h2>
    
    <div class="demo-buttons">
      <button @click="testCase('low_risk')" :disabled="loading">
        Cliente Bajo Riesgo
      </button>
      <button @click="testCase('medium_risk')" :disabled="loading">
        Cliente Riesgo Medio
      </button>
      <button @click="testCase('high_risk')" :disabled="loading">
        Cliente Alto Riesgo
      </button>
    </div>
    
    <div v-if="result" class="result-card">
      <h3>Resultado</h3>
      <div class="metric">
        <span class="label">Decisión:</span>
        <span :class="['value', decisionClass]">{{ result.decision }}</span>
      </div>
      <div class="metric">
        <span class="label">Risk Score:</span>
        <span class="value">{{ result.risk_score }}%</span>
      </div>
      <div class="metric">
        <span class="label">Nivel de Riesgo:</span>
        <span class="value">{{ result.risk_level }}</span>
      </div>
      
      <h4>Factores Principales:</h4>
      <ul>
        <li v-for="(factor, i) in result.main_factors" :key="i">
          {{ factor }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CreditCardDemo',
  data() {
    return {
      result: null,
      loading: false
    };
  },
  computed: {
    decisionClass() {
      const map = {
        'APPROVED': 'success',
        'APPROVED_WITH_CONDITIONS': 'warning',
        'MANUAL_REVIEW': 'warning',
        'REJECTED': 'danger'
      };
      return map[this.result?.decision] || '';
    }
  },
  methods: {
    async testCase(caseType) {
      this.loading = true;
      try {
        // Obtener casos
        const casesRes = await fetch('http://localhost:8012/demo-cases');
        const cases = await casesRes.json();
        
        // Predecir
        const predRes = await fetch('http://localhost:8012/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(cases[caseType].data)
        });
        
        this.result = await predRes.json();
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.credit-card-demo {
  padding: 20px;
}

.demo-buttons {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.demo-buttons button {
  padding: 10px 20px;
  font-size: 14px;
  border: none;
  border-radius: 5px;
  background: #00d4ff;
  color: #000;
  cursor: pointer;
  font-weight: bold;
}

.demo-buttons button:hover {
  background: #00b8e6;
}

.demo-buttons button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.result-card {
  margin-top: 20px;
  padding: 20px;
  border: 2px solid #00d4ff;
  border-radius: 10px;
  background: #1a1a1a;
}

.metric {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
  padding: 10px;
  background: #2a2a2a;
  border-radius: 5px;
}

.metric .label {
  font-weight: bold;
}

.metric .value.success {
  color: #00ff88;
}

.metric .value.warning {
  color: #ffaa00;
}

.metric .value.danger {
  color: #ff6600;
}
</style>
```

## 🎯 Casos de Demo Incluidos

### 1. Cliente Bajo Riesgo
- **Edad**: 40 años
- **Ingresos**: 150,000€/año
- **Credit Score**: 780
- **Defaults previos**: 0
- **Resultado esperado**: APPROVED (Risk Score: ~5%)

### 2. Cliente Riesgo Medio
- **Edad**: 30 años
- **Ingresos**: 80,000€/año
- **Credit Score**: 650
- **Utilización crédito**: 75%
- **Resultado esperado**: APPROVED_WITH_CONDITIONS (Risk Score: ~25%)

### 3. Cliente Alto Riesgo
- **Edad**: 25 años
- **Ingresos**: 40,000€/año
- **Credit Score**: 550
- **Defaults previos**: 2
- **Default reciente**: Sí
- **Resultado esperado**: REJECTED (Risk Score: ~85%)

## 📊 Interpretación de Resultados

### Decisiones

| Decisión | Significado | Risk Score |
|---|---|---|
| `APPROVED` | Aprobación automática | <20% |
| `APPROVED_WITH_CONDITIONS` | Aprobación condicional | 20-35% |
| `MANUAL_REVIEW` | Revisión manual requerida | 35-50% |
| `REJECTED` | Rechazo automático | >50% |

### Niveles de Riesgo

| Nivel | Descripción |
|---|---|
| `LOW` | Bajo riesgo de default |
| `MEDIUM` | Riesgo medio |
| `HIGH` | Alto riesgo |
| `VERY_HIGH` | Riesgo muy alto |

## 🔧 Configuración

### Puerto
Por defecto: `8012`

Cambiar con variable de entorno:
```bash
PORT=9000 python demo_api.py
```

### CORS
Configurado para aceptar requests desde cualquier origen (`*`).

Para producción, restringir a dominios específicos en `demo_api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],
    ...
)
```

## 🐳 Docker (Opcional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY demo_api.py .
COPY models/ ./models/

EXPOSE 8012

CMD ["python", "demo_api.py"]
```

```bash
docker build -t credit-card-demo .
docker run -p 8012:8012 credit-card-demo
```

## 📝 Notas

- ✅ La API carga automáticamente el modelo más reciente de `./models/`
- ✅ Incluye preprocesamiento completo (feature engineering)
- ✅ Detección de fraude integrada
- ✅ Respuestas en tiempo real (<100ms)
- ✅ CORS habilitado para desarrollo
- ⚠️ Para producción: añadir autenticación y rate limiting

## 🎉 ¡Listo para Demostración!

1. Iniciar API: `python demo_api.py`
2. Abrir frontend
3. Click en botón de demo
4. Ver resultados en tiempo real

**¡El modelo está listo para impresionar!** 🚀💳✨
