"""
Demo API for Credit Card Model
Simple FastAPI endpoint for frontend integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import os

app = FastAPI(
    title="Credit Card Model Demo API",
    description="API de demostración para el modelo de tarjetas de crédito",
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

# Global variables for models
model = None
fraud_detector = None
label_encoders = None
metadata = None

# Load models on startup
@app.on_event("startup")
async def load_models():
    global model, fraud_detector, label_encoders, metadata
    
    model_dir = "./models"
    
    # Find latest model version
    model_files = [f for f in os.listdir(model_dir) if f.startswith("credit_card_model_")]
    if not model_files:
        print("⚠️ No model files found - using dummy mode")
        return
    
    latest_model = sorted(model_files)[-1]
    version = latest_model.replace("credit_card_model_v", "").replace(".pkl", "")
    
    print(f"📦 Loading models version: {version}")
    
    try:
        model = joblib.load(os.path.join(model_dir, f"credit_card_model_v{version}.pkl"))
        fraud_detector = joblib.load(os.path.join(model_dir, f"fraud_detector_v{version}.pkl"))
        label_encoders = joblib.load(os.path.join(model_dir, f"label_encoders_v{version}.pkl"))
        metadata = joblib.load(os.path.join(model_dir, f"metadata_v{version}.pkl"))
        print(f"✅ Models loaded successfully")
        print(f"   AUC-ROC: {metadata.get('metrics', {}).get('auc_roc', 'N/A')}")
    except Exception as e:
        print(f"❌ Error loading models: {e}")


class CustomerData(BaseModel):
    """Datos del cliente para scoring"""
    age: int = Field(..., ge=18, le=100, description="Edad")
    gender: str = Field(..., description="Género (M/F)")
    owns_car: str = Field(..., description="Posee coche (Y/N)")
    owns_house: str = Field(..., description="Posee casa (Y/N)")
    no_of_children: float = Field(0, ge=0, description="Número de hijos")
    net_yearly_income: float = Field(..., gt=0, description="Ingresos anuales")
    no_of_days_employed: float = Field(..., ge=0, description="Días empleado")
    occupation_type: str = Field(..., description="Tipo de ocupación")
    total_family_members: float = Field(..., gt=0, description="Miembros familia")
    migrant_worker: float = Field(0, description="Trabajador migrante (0/1)")
    yearly_debt_payments: float = Field(..., ge=0, description="Pagos anuales deuda")
    credit_limit: float = Field(..., gt=0, description="Límite de crédito")
    credit_limit_used_pct: float = Field(..., ge=0, le=100, description="% crédito usado")
    credit_score: float = Field(..., ge=300, le=850, description="Score crediticio")
    prev_defaults: int = Field(0, ge=0, description="Defaults previos")
    default_in_last_6months: int = Field(0, ge=0, le=1, description="Default reciente")


class PredictionResponse(BaseModel):
    """Respuesta de predicción"""
    customer_id: str
    default_probability: float
    risk_score: float
    decision: str
    is_fraud_suspicious: bool
    fraud_score: float
    risk_level: str
    main_factors: list
    model_version: str
    timestamp: str


def preprocess_customer_data(data: CustomerData) -> np.ndarray:
    """Preprocesa datos del cliente"""
    
    # Crear DataFrame
    df = pd.DataFrame([{
        'age': data.age,
        'gender': data.gender,
        'owns_car': data.owns_car,
        'owns_house': data.owns_house,
        'no_of_children': data.no_of_children,
        'net_yearly_income': data.net_yearly_income,
        'no_of_days_employed': data.no_of_days_employed,
        'occupation_type': data.occupation_type,
        'total_family_members': data.total_family_members,
        'migrant_worker': data.migrant_worker,
        'yearly_debt_payments': data.yearly_debt_payments,
        'credit_limit': data.credit_limit,
        'credit_limit_used(%)': data.credit_limit_used_pct,
        'credit_score': data.credit_score,
        'prev_defaults': data.prev_defaults,
        'default_in_last_6months': data.default_in_last_6months
    }])
    
    # Codificar categóricas
    for col in ['gender', 'owns_car', 'owns_house', 'occupation_type']:
        if col in label_encoders:
            try:
                df[col] = label_encoders[col].transform(df[col].astype(str))
            except:
                df[col] = -1  # Valor desconocido
    
    # Feature engineering
    df['credit_utilization_ratio'] = df['credit_limit_used(%)'] / 100.0
    df['debt_to_income_ratio'] = df['yearly_debt_payments'] / df['net_yearly_income'].replace(0, 1)
    df['credit_used_amount'] = (df['credit_limit'] * df['credit_limit_used(%)']) / 100.0
    df['income_per_family_member'] = df['net_yearly_income'] / df['total_family_members'].replace(0, 1)
    df['years_employed'] = df['no_of_days_employed'] / 365.0
    df['high_risk_indicator'] = (
        (df['prev_defaults'] > 0) | 
        (df['default_in_last_6months'] > 0) |
        (df['credit_score'] < 600)
    ).astype(int)
    
    # Seleccionar features en el orden correcto
    feature_cols = [
        'age', 'gender', 'owns_car', 'owns_house', 'no_of_children',
        'net_yearly_income', 'no_of_days_employed', 'occupation_type',
        'total_family_members', 'migrant_worker', 'yearly_debt_payments',
        'credit_limit', 'credit_limit_used(%)', 'credit_score',
        'prev_defaults', 'default_in_last_6months',
        'credit_utilization_ratio', 'debt_to_income_ratio',
        'credit_used_amount', 'income_per_family_member',
        'years_employed', 'high_risk_indicator'
    ]
    
    return df[feature_cols].values


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Credit Card Model Demo API",
        "status": "running",
        "model_loaded": model is not None,
        "version": metadata.get('version', 'unknown') if metadata else 'unknown'
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(data: CustomerData):
    """
    Predice riesgo de default para un cliente
    """
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Preprocesar
        X = preprocess_customer_data(data)
        
        # Predicción de default
        probability = model.predict_proba(X)[0][1]
        risk_score = round(probability * 100, 2)
        
        # Decisión
        if probability < 0.20:
            decision = "APPROVED"
            risk_level = "LOW"
        elif probability < 0.35:
            decision = "APPROVED_WITH_CONDITIONS"
            risk_level = "MEDIUM"
        elif probability < 0.50:
            decision = "MANUAL_REVIEW"
            risk_level = "HIGH"
        else:
            decision = "REJECTED"
            risk_level = "VERY_HIGH"
        
        # Detección de fraude
        fraud_pred = fraud_detector.predict(X)[0]
        is_fraud = fraud_pred == -1
        fraud_score = fraud_detector.score_samples(X)[0]
        fraud_score_norm = 1 / (1 + np.exp(fraud_score))
        
        # Factores principales
        main_factors = []
        if data.prev_defaults > 0:
            main_factors.append(f"⚠️ {data.prev_defaults} default(s) previo(s)")
        if data.default_in_last_6months > 0:
            main_factors.append("⚠️ Default en últimos 6 meses")
        if data.credit_score < 600:
            main_factors.append(f"⚠️ Credit score bajo ({data.credit_score})")
        if data.credit_limit_used_pct > 80:
            main_factors.append(f"⚠️ Alta utilización de crédito ({data.credit_limit_used_pct}%)")
        
        debt_to_income = data.yearly_debt_payments / data.net_yearly_income
        if debt_to_income > 0.5:
            main_factors.append(f"⚠️ Alto ratio deuda/ingresos ({debt_to_income:.1%})")
        
        if not main_factors:
            main_factors.append("✅ Perfil de bajo riesgo")
        
        if data.credit_score > 750:
            main_factors.append(f"✅ Excelente credit score ({data.credit_score})")
        
        return PredictionResponse(
            customer_id=f"DEMO_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            default_probability=round(probability, 4),
            risk_score=risk_score,
            decision=decision,
            is_fraud_suspicious=is_fraud,
            fraud_score=round(fraud_score_norm, 4),
            risk_level=risk_level,
            main_factors=main_factors,
            model_version=metadata.get('version', 'unknown') if metadata else 'unknown',
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/demo-cases")
async def get_demo_cases():
    """Retorna casos de ejemplo para demo"""
    return {
        "low_risk": {
            "name": "Cliente Bajo Riesgo",
            "data": {
                "age": 40,
                "gender": "M",
                "owns_car": "Y",
                "owns_house": "Y",
                "no_of_children": 2,
                "net_yearly_income": 150000,
                "no_of_days_employed": 3650,
                "occupation_type": "Core staff",
                "total_family_members": 4,
                "migrant_worker": 0,
                "yearly_debt_payments": 20000,
                "credit_limit": 50000,
                "credit_limit_used_pct": 30,
                "credit_score": 780,
                "prev_defaults": 0,
                "default_in_last_6months": 0
            }
        },
        "medium_risk": {
            "name": "Cliente Riesgo Medio",
            "data": {
                "age": 30,
                "gender": "F",
                "owns_car": "N",
                "owns_house": "N",
                "no_of_children": 1,
                "net_yearly_income": 80000,
                "no_of_days_employed": 1825,
                "occupation_type": "Laborers",
                "total_family_members": 3,
                "migrant_worker": 0,
                "yearly_debt_payments": 35000,
                "credit_limit": 30000,
                "credit_limit_used_pct": 75,
                "credit_score": 650,
                "prev_defaults": 0,
                "default_in_last_6months": 0
            }
        },
        "high_risk": {
            "name": "Cliente Alto Riesgo",
            "data": {
                "age": 25,
                "gender": "M",
                "owns_car": "N",
                "owns_house": "N",
                "no_of_children": 0,
                "net_yearly_income": 40000,
                "no_of_days_employed": 365,
                "occupation_type": "Unknown",
                "total_family_members": 1,
                "migrant_worker": 1,
                "yearly_debt_payments": 25000,
                "credit_limit": 20000,
                "credit_limit_used_pct": 95,
                "credit_score": 550,
                "prev_defaults": 2,
                "default_in_last_6months": 1
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8012))
    print(f"🚀 Starting Credit Card Demo API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
