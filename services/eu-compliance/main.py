"""
EU Compliance Service - FastAPI
Puerto: 8013
Integración con scoring híbrido y modelo de tarjetas de crédito
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import logging

from eu_regulatory_api import EURLexAPI, ComplianceChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EU Regulatory Compliance Service",
    description="Servicio de compliance regulatorio para IA y protección de datos",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
api = EURLexAPI()
checker = ComplianceChecker()


class UseCaseRequest(BaseModel):
    """Caso de uso para evaluar"""
    purpose: str = Field(..., description="Propósito del sistema")
    sector: str = Field(..., description="Sector de aplicación")
    decision_type: str = Field("manual", description="Tipo de decisión: automated/manual")
    involves_biometrics: bool = Field(False, description="Involucra biometría")
    affects_rights: bool = Field(False, description="Afecta derechos fundamentales")
    processes_personal_data: bool = Field(False, description="Procesa datos personales")
    uses_ai: bool = Field(True, description="Usa IA")
    interacts_with_humans: bool = Field(False, description="Interactúa con humanos")
    involves_data_sharing: bool = Field(False, description="Comparte datos")


class ModelComplianceRequest(BaseModel):
    """Información del modelo para verificar compliance"""
    model_name: str
    model_type: str
    processes_personal_data: bool = True
    features: List[str]
    protected_attributes: Optional[List[str]] = None
    accuracy: Optional[float] = None
    bias_mitigation: Optional[bool] = False
    use_case: str


class ComplianceResponse(BaseModel):
    """Respuesta de evaluación de compliance"""
    risk_level: str
    compliance_status: str
    requirements: List[str]
    warnings: List[str]
    applicable_regulations: List[str]
    timestamp: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "EU Regulatory Compliance",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/search-regulations",
            "/gdpr-requirements",
            "/ai-act-structure",
            "/nis2-requirements",
            "/assess-use-case",
            "/check-model-compliance",
            "/generate-report"
        ]
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/search-regulations")
async def search_regulations(keyword: str, limit: int = 10):
    """
    Busca regulaciones por palabra clave
    
    Ejemplo: /search-regulations?keyword=artificial%20intelligence&limit=5
    """
    try:
        results = api.search_regulations(keyword, limit)
        return {
            "keyword": keyword,
            "count": len(results),
            "regulations": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gdpr-requirements")
async def get_gdpr_requirements():
    """
    Obtiene requisitos clave del GDPR
    """
    try:
        gdpr = api.get_gdpr_requirements()
        return gdpr
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai-act-structure")
async def get_ai_act_structure():
    """
    Obtiene estructura y niveles de riesgo del AI Act
    """
    try:
        ai_act = api.get_ai_act_structure()
        return ai_act
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/nis2-requirements")
async def get_nis2_requirements():
    """
    Obtiene requisitos de NIS2 Directive (ciberseguridad)
    """
    try:
        nis2 = api.get_nis2_requirements()
        return nis2
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assess-use-case", response_model=ComplianceResponse)
async def assess_use_case(use_case: UseCaseRequest):
    """
    Evalúa el nivel de riesgo y compliance de un caso de uso
    
    Ejemplo:
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
    """
    try:
        assessment = checker.assess_ai_risk_level(use_case.dict())
        
        return ComplianceResponse(
            risk_level=assessment['risk_level'],
            compliance_status=assessment['compliance_status'],
            requirements=assessment['requirements'],
            warnings=assessment['warnings'],
            applicable_regulations=assessment['applicable_regulations'],
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-model-compliance")
async def check_model_compliance(model_info: ModelComplianceRequest):
    """
    Verifica compliance específico para modelos ML
    
    Especialmente útil para modelos de credit scoring
    
    Ejemplo:
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
    """
    try:
        compliance = checker.check_credit_scoring_compliance(model_info.dict())
        
        return {
            "model_name": model_info.model_name,
            "compliance_checks": compliance,
            "overall_status": compliance['status'],
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": _generate_recommendations(compliance)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-report")
async def generate_report(
    project_name: str,
    use_cases: List[UseCaseRequest]
):
    """
    Genera reporte completo de compliance para múltiples casos de uso
    
    Ejemplo:
    ```json
    {
      "project_name": "Sistema Corporativo Documental",
      "use_cases": [
        {
          "purpose": "Document classification",
          "sector": "document_management",
          ...
        },
        {
          "purpose": "Credit risk scoring",
          "sector": "essential_services",
          ...
        }
      ]
    }
    ```
    """
    try:
        use_cases_dict = [uc.dict() for uc in use_cases]
        report = checker.generate_compliance_report(project_name, use_cases_dict)
        
        return {
            "project_name": project_name,
            "report": report,
            "generated_at": datetime.utcnow().isoformat(),
            "use_cases_count": len(use_cases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/credit-card-model-compliance")
async def get_credit_card_model_compliance():
    """
    Endpoint específico para verificar compliance del modelo de tarjetas de crédito
    
    Retorna análisis completo de compliance para el modelo entrenado
    """
    try:
        # Información del modelo de tarjetas de crédito
        model_info = {
            "model_name": "Credit Card Default Prediction Model",
            "model_type": "GradientBoostingClassifier + CalibratedClassifierCV",
            "processes_personal_data": True,
            "features": [
                "age", "gender", "owns_car", "owns_house", "no_of_children",
                "net_yearly_income", "no_of_days_employed", "occupation_type",
                "total_family_members", "migrant_worker", "yearly_debt_payments",
                "credit_limit", "credit_limit_used(%)", "credit_score",
                "prev_defaults", "default_in_last_6months",
                "credit_utilization_ratio", "debt_to_income_ratio",
                "credit_used_amount", "income_per_family_member",
                "years_employed", "high_risk_indicator"
            ],
            "protected_attributes": ["age", "gender"],
            "accuracy": 0.9801,
            "bias_mitigation": False,  # TODO: Implement bias mitigation
            "use_case": "credit_scoring"
        }
        
        # Evaluar compliance
        compliance = checker.check_credit_scoring_compliance(model_info)
        
        # Evaluar caso de uso
        use_case = {
            "purpose": "AI-powered credit card default prediction",
            "sector": "essential_services",
            "decision_type": "automated",
            "involves_biometrics": False,
            "affects_rights": True,
            "processes_personal_data": True,
            "uses_ai": True,
            "interacts_with_humans": False,
            "involves_data_sharing": False
        }
        
        risk_assessment = checker.assess_ai_risk_level(use_case)
        
        return {
            "model_info": model_info,
            "compliance_checks": compliance,
            "risk_assessment": risk_assessment,
            "overall_status": "HIGH_RISK_REQUIRES_COMPLIANCE",
            "critical_actions": [
                "✅ Implement Data Protection Impact Assessment (DPIA)",
                "✅ Establish legal basis for processing (GDPR Art. 6)",
                "✅ Implement right to explanation mechanism",
                "✅ Establish human oversight procedures",
                "⚠️ Implement bias mitigation for protected attributes",
                "⚠️ Create technical documentation (AI Act requirement)",
                "⚠️ Implement risk management system",
                "⚠️ Establish record-keeping procedures"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_recommendations(compliance: Dict) -> List[str]:
    """Genera recomendaciones basadas en checks de compliance"""
    recommendations = []
    
    # GDPR recommendations
    gdpr_checks = compliance.get('gdpr_compliance', [])
    if any(check['status'] == 'REQUIRED' for check in gdpr_checks):
        recommendations.append("📋 Complete Data Protection Impact Assessment (DPIA)")
        recommendations.append("📋 Document legal basis for data processing")
        recommendations.append("📋 Implement data subject rights procedures")
    
    # AI Act recommendations
    ai_checks = compliance.get('ai_act_compliance', [])
    if ai_checks:
        recommendations.append("📋 Establish risk management system")
        recommendations.append("📋 Create comprehensive technical documentation")
        recommendations.append("📋 Implement human oversight mechanisms")
    
    # Fairness recommendations
    fairness_checks = compliance.get('fairness', [])
    for check in fairness_checks:
        if check.get('status') == 'REVIEW_REQUIRED':
            recommendations.append(f"⚠️ Review handling of protected attributes: {', '.join(check.get('attributes', []))}")
            recommendations.append("⚠️ Implement bias detection and mitigation")
            recommendations.append("⚠️ Conduct fairness audits regularly")
    
    # Transparency recommendations
    recommendations.append("📋 Provide clear explanations of model decisions")
    recommendations.append("📋 Maintain audit logs of all predictions")
    recommendations.append("📋 Establish model monitoring and retraining procedures")
    
    return recommendations


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8013))
    logger.info(f"🚀 Starting EU Compliance Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
