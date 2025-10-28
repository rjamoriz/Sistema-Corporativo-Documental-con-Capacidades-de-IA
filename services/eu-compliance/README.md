## 🇪🇺 EU Regulatory Compliance Service

Servicio de compliance regulatorio automático integrado con EUR-Lex para cumplimiento de GDPR, AI Act, NIS2 y otras regulaciones europeas.

### 🎯 Características

- ✅ **Búsqueda de regulaciones** en EUR-Lex por palabra clave
- ✅ **Evaluación automática** de nivel de riesgo según AI Act
- ✅ **Verificación de compliance** para modelos ML
- ✅ **Requisitos GDPR** estructurados por artículo
- ✅ **Análisis NIS2** para ciberseguridad
- ✅ **Generación de reportes** de compliance
- ✅ **Integración específica** con modelo de tarjetas de crédito

### 🚀 Inicio Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar servicio
python main.py

# Servicio disponible en: http://localhost:8013
```

### 📡 Endpoints Principales

#### 1. Buscar Regulaciones

```bash
GET /search-regulations?keyword=artificial%20intelligence&limit=5
```

**Respuesta:**
```json
{
  "keyword": "artificial intelligence",
  "count": 5,
  "regulations": [
    {
      "celex": "52021PC0206",
      "title": "Proposal for a Regulation on Artificial Intelligence",
      "date": "2021-04-21"
    }
  ]
}
```

#### 2. Requisitos GDPR

```bash
GET /gdpr-requirements
```

**Respuesta:**
```json
{
  "key_articles": [
    {
      "article": "Article 5",
      "title": "Principles relating to processing of personal data",
      "requirements": [
        "Lawfulness, fairness and transparency",
        "Purpose limitation",
        "Data minimisation"
      ]
    }
  ],
  "celex": "32016R0679",
  "effective_date": "2018-05-25"
}
```

#### 3. Estructura del AI Act

```bash
GET /ai-act-structure
```

**Respuesta:**
```json
{
  "risk_levels": {
    "unacceptable": {
      "level": "Unacceptable Risk",
      "description": "Prohibited AI systems",
      "action": "BANNED"
    },
    "high": {
      "level": "High Risk",
      "requirements": [
        "Risk management system",
        "Data governance",
        "Technical documentation"
      ],
      "action": "STRICT_COMPLIANCE"
    }
  }
}
```

#### 4. Evaluar Caso de Uso

```bash
POST /assess-use-case
```

**Request:**
```json
{
  "purpose": "AI-powered credit scoring",
  "sector": "essential_services",
  "decision_type": "automated",
  "involves_biometrics": false,
  "affects_rights": true,
  "processes_personal_data": true,
  "uses_ai": true
}
```

**Respuesta:**
```json
{
  "risk_level": "high",
  "compliance_status": "REQUIRES_ASSESSMENT",
  "requirements": [
    "Risk management system",
    "Data governance",
    "Technical documentation",
    "GDPR compliance required",
    "Data protection impact assessment (DPIA)"
  ],
  "warnings": [
    "⚠️ HIGH RISK: Strict compliance requirements apply",
    "⚠️ GDPR Art. 22 applies: Automated decisions with legal/significant effects"
  ],
  "applicable_regulations": [
    "GDPR (32016R0679)",
    "AI Act (52021PC0206)"
  ]
}
```

#### 5. Verificar Compliance del Modelo

```bash
POST /check-model-compliance
```

**Request:**
```json
{
  "model_name": "Credit Card Default Model",
  "model_type": "GradientBoostingClassifier",
  "processes_personal_data": true,
  "features": ["age", "credit_score", "income", "prev_defaults"],
  "protected_attributes": ["age", "gender"],
  "accuracy": 0.9801,
  "bias_mitigation": true,
  "use_case": "credit_scoring"
}
```

**Respuesta:**
```json
{
  "model_name": "Credit Card Default Model",
  "compliance_checks": {
    "gdpr_compliance": [
      {
        "requirement": "Legal basis for processing",
        "status": "REQUIRED",
        "article": "GDPR Art. 6"
      },
      {
        "requirement": "Data protection impact assessment",
        "status": "REQUIRED",
        "article": "GDPR Art. 35"
      }
    ],
    "ai_act_compliance": [
      {
        "requirement": "Risk management system",
        "status": "REQUIRED",
        "category": "High Risk AI"
      }
    ],
    "transparency": [
      {
        "item": "Model type disclosed",
        "value": "GradientBoostingClassifier",
        "status": "✅"
      },
      {
        "item": "Model accuracy",
        "value": "98.01%",
        "status": "✅"
      }
    ],
    "fairness": [
      {
        "check": "Protected attributes handling",
        "attributes": ["age", "gender"],
        "status": "REVIEW_REQUIRED"
      }
    ]
  },
  "recommendations": [
    "📋 Complete Data Protection Impact Assessment (DPIA)",
    "⚠️ Review handling of protected attributes: age, gender",
    "⚠️ Implement bias detection and mitigation"
  ]
}
```

#### 6. Compliance del Modelo de Tarjetas de Crédito

```bash
GET /credit-card-model-compliance
```

**Respuesta completa** con análisis específico del modelo entrenado.

#### 7. Generar Reporte Completo

```bash
POST /generate-report
```

**Request:**
```json
{
  "project_name": "Sistema Corporativo Documental",
  "use_cases": [
    {
      "purpose": "Document classification",
      "sector": "document_management",
      "decision_type": "automated",
      "processes_personal_data": false,
      "uses_ai": true
    },
    {
      "purpose": "Credit risk scoring",
      "sector": "essential_services",
      "decision_type": "automated",
      "affects_rights": true,
      "processes_personal_data": true,
      "uses_ai": true
    }
  ]
}
```

**Respuesta:**
```
================================================================================
EU REGULATORY COMPLIANCE REPORT
Project: Sistema Corporativo Documental
Generated: 2024-10-28 19:20:00 UTC
================================================================================

================================================================================
USE CASE #1: Document classification
================================================================================
Risk Level: MINIMAL
Compliance Status: COMPLIANT

📋 REQUIREMENTS:
  • Voluntary codes of conduct

📜 APPLICABLE REGULATIONS:
  • AI Act (52021PC0206)

================================================================================
USE CASE #2: Credit risk scoring
================================================================================
Risk Level: HIGH
Compliance Status: REQUIRES_ASSESSMENT

⚠️ WARNINGS:
  ⚠️ HIGH RISK: Strict compliance requirements apply
  ⚠️ GDPR Art. 22 applies: Automated decisions with legal/significant effects

📋 REQUIREMENTS:
  • Risk management system
  • Data governance
  • Technical documentation
  • GDPR compliance required
  • Data protection impact assessment (DPIA)

📜 APPLICABLE REGULATIONS:
  • GDPR (32016R0679)
  • AI Act (52021PC0206)

================================================================================
SUMMARY
================================================================================
Total Use Cases: 2
  • Unacceptable Risk: 0
  • High Risk: 1
  • Limited Risk: 0
  • Minimal Risk: 1

⚠️ ACTION REQUIRED: High-risk systems require strict compliance
```

### 🔗 Integración con Sistema Existente

#### Integración con Scoring Orchestrator

```python
import requests

# Verificar compliance antes de scoring
def score_with_compliance_check(customer_data):
    # 1. Verificar compliance del modelo
    compliance_response = requests.get(
        "http://localhost:8013/credit-card-model-compliance"
    )
    compliance = compliance_response.json()
    
    if compliance['overall_status'] == 'HIGH_RISK_REQUIRES_COMPLIANCE':
        # Log compliance requirements
        log_compliance_requirements(compliance['critical_actions'])
    
    # 2. Realizar scoring
    scoring_response = requests.post(
        "http://localhost:8012/predict",
        json=customer_data
    )
    result = scoring_response.json()
    
    # 3. Añadir información de compliance
    result['compliance_status'] = compliance['overall_status']
    result['compliance_checks'] = compliance['compliance_checks']
    
    return result
```

#### Integración con Frontend

```javascript
// Mostrar compliance status en UI
async function showModelCompliance() {
  const response = await fetch('http://localhost:8013/credit-card-model-compliance');
  const compliance = await response.json();
  
  // Mostrar badge de compliance
  const badge = document.getElementById('compliance-badge');
  badge.innerHTML = `
    <div class="compliance-status ${compliance.overall_status}">
      <h4>Compliance Status</h4>
      <p>${compliance.overall_status}</p>
      <ul>
        ${compliance.critical_actions.map(action => `<li>${action}</li>`).join('')}
      </ul>
    </div>
  `;
}
```

#### Monitoreo Continuo

```python
# Scheduled job para verificar cambios regulatorios
import schedule
import time

def check_regulatory_updates():
    # Buscar actualizaciones de AI Act
    response = requests.get(
        "http://localhost:8013/search-regulations?keyword=artificial%20intelligence&limit=10"
    )
    regulations = response.json()['regulations']
    
    # Comparar con versión anterior
    if has_new_regulations(regulations):
        send_alert_to_compliance_team(regulations)

# Ejecutar diariamente
schedule.every().day.at("09:00").do(check_regulatory_updates)

while True:
    schedule.run_pending()
    time.sleep(3600)
```

### 📊 Niveles de Riesgo AI Act

| Nivel | Descripción | Acción Requerida |
|---|---|---|
| **Unacceptable** | Sistemas prohibidos | ⛔ BANNED |
| **High** | Riesgo significativo | ⚠️ STRICT_COMPLIANCE |
| **Limited** | Obligaciones de transparencia | ℹ️ TRANSPARENCY_REQUIRED |
| **Minimal** | Riesgo mínimo | ✅ NO_OBLIGATIONS |

### 🎯 Casos de Uso Cubiertos

#### 1. Credit Scoring (HIGH RISK)
- ✅ Evaluación automática de riesgo
- ✅ Requisitos GDPR identificados
- ✅ Requisitos AI Act identificados
- ✅ Recomendaciones de compliance

#### 2. Document Classification (MINIMAL RISK)
- ✅ Sin requisitos estrictos
- ✅ Códigos de conducta voluntarios

#### 3. Biometric Systems (UNACCEPTABLE/HIGH RISK)
- ✅ Detección automática de prohibiciones
- ✅ Requisitos estrictos si permitido

### 🔐 Regulaciones Soportadas

| Regulación | CELEX | Estado | Cobertura |
|---|---|---|---|
| **GDPR** | 32016R0679 | ✅ En vigor | Completa |
| **AI Act** | 52021PC0206 | 🔄 Propuesta | Estructura completa |
| **NIS2** | 32022L2555 | ✅ En vigor | Requisitos clave |
| **Data Governance Act** | 32022R0868 | ✅ En vigor | Básica |

### 🚀 Próximas Mejoras

- [ ] Alertas automáticas por email
- [ ] Export a PDF/Excel
- [ ] Dashboard web interactivo
- [ ] Multi-idioma (ES, FR, DE)
- [ ] Integración con Azure/AWS compliance
- [ ] Análisis de bias automático
- [ ] Monitoreo de cambios regulatorios
- [ ] API webhooks para notificaciones

### 📚 Documentación Adicional

- [EUR-Lex API Documentation](https://eur-lex.europa.eu/content/tools/webservices.html)
- [GDPR Full Text](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- [AI Act Proposal](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021PC0206)
- [NIS2 Directive](https://eur-lex.europa.eu/eli/dir/2022/2555/oj)

### 🐳 Docker

```bash
# Build
docker build -t eu-compliance .

# Run
docker run -p 8013:8013 eu-compliance
```

### 🧪 Testing

```bash
# Test API
python eu_regulatory_api.py

# Test service
curl http://localhost:8013/health
curl http://localhost:8013/gdpr-requirements
curl http://localhost:8013/credit-card-model-compliance
```

### 📞 Soporte

Para consultas sobre compliance regulatorio, contactar al equipo de Legal/Compliance.

---

**🎯 Servicio listo para integración con el sistema de scoring híbrido y modelo de tarjetas de crédito!**
