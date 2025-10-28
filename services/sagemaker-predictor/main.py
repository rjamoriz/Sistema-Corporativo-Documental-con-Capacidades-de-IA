"""
AWS SageMaker Predictive ML Service
Servicio de ML predictivo con explainability (SHAP) para decisiones financieras
Basado en: awslabs/sagemaker-explaining-credit-decisions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

# SHAP for model explainability
import shap

# LightGBM and XGBoost
import lightgbm as lgb
import xgboost as xgb

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from starlette.responses import Response

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8008"))
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models")
USE_SAGEMAKER = os.getenv("USE_SAGEMAKER", "false").lower() == "true"
SAGEMAKER_ENDPOINT = os.getenv("SAGEMAKER_ENDPOINT", "")

# Prometheus metrics
prediction_requests = Counter('prediction_requests_total', 'Total prediction requests', ['model', 'status'])
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency', ['model'])
shap_computation_time = Histogram('shap_computation_seconds', 'SHAP computation time')
model_confidence = Gauge('model_confidence_score', 'Model confidence score')

# FastAPI app
app = FastAPI(
    title="SageMaker Predictive ML Service",
    description="Servicio de ML predictivo con explainability para decisiones financieras",
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

# Pydantic models
class DocumentFeatures(BaseModel):
    """Features extraídas de un documento financiero"""
    # Características del documento
    document_type: str = Field(..., description="Tipo de documento")
    amount: float = Field(..., description="Monto o valor")
    duration: int = Field(default=12, description="Duración en meses")
    
    # Características adicionales (opcionales)
    age: Optional[int] = Field(None, description="Edad del solicitante")
    employment_duration: Optional[int] = Field(None, description="Duración del empleo")
    num_dependents: Optional[int] = Field(default=0, description="Número de dependientes")
    
    # Características categóricas
    purpose: Optional[str] = Field(None, description="Propósito del crédito")
    housing: Optional[str] = Field(default="own", description="Tipo de vivienda")
    job_type: Optional[str] = Field(None, description="Tipo de trabajo")
    
    # Metadata
    document_id: Optional[str] = Field(None, description="ID del documento")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class PredictionRequest(BaseModel):
    """Request para predicción"""
    features: DocumentFeatures
    explain: bool = Field(default=True, description="Incluir explicación SHAP")
    model_type: str = Field(default="lightgbm", description="Tipo de modelo (lightgbm, xgboost)")

class ShapExplanation(BaseModel):
    """Explicación SHAP de una predicción"""
    feature_names: List[str]
    feature_values: List[float]
    shap_values: List[float]
    base_value: float
    expected_value: float

class PredictionResult(BaseModel):
    """Resultado de predicción"""
    prediction: int
    probability: float
    confidence: float
    risk_score: float
    explanation: Optional[ShapExplanation] = None
    model_type: str
    execution_time: float
    document_id: Optional[str] = None
    timestamp: str

class BatchPredictionRequest(BaseModel):
    """Request para predicción en batch"""
    features_list: List[DocumentFeatures]
    explain: bool = Field(default=False, description="Incluir explicaciones SHAP")
    model_type: str = Field(default="lightgbm")

class BatchPredictionResult(BaseModel):
    """Resultado de predicción en batch"""
    predictions: List[PredictionResult]
    total_processed: int
    execution_time: float

class ModelPerformance(BaseModel):
    """Métricas de rendimiento del modelo"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float

class PredictiveMLModel:
    """Clase para manejar modelos predictivos con explainability"""
    
    def __init__(self, model_type: str = "lightgbm"):
        self.model_type = model_type
        self.model = None
        self.explainer = None
        self.feature_names = []
        self.is_trained = False
        
        # Intentar cargar modelo pre-entrenado
        self._load_model()
    
    def _load_model(self):
        """Cargar modelo pre-entrenado si existe"""
        model_file = Path(MODEL_PATH) / f"{self.model_type}_model.pkl"
        
        if model_file.exists():
            try:
                self.model = joblib.load(model_file)
                self.is_trained = True
                logger.info(f"✅ Modelo {self.model_type} cargado desde {model_file}")
                
                # Inicializar explainer SHAP
                if self.model_type == "lightgbm":
                    self.explainer = shap.TreeExplainer(self.model)
                elif self.model_type == "xgboost":
                    self.explainer = shap.TreeExplainer(self.model)
                
                logger.info("✅ SHAP explainer inicializado")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo cargar modelo: {e}")
                self._create_dummy_model()
        else:
            logger.info(f"ℹ️ No existe modelo pre-entrenado, usando modelo dummy")
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Crear modelo dummy para demostración"""
        logger.info("📝 Creando modelo dummy para demostración...")
        
        # Crear datos sintéticos
        np.random.seed(42)
        n_samples = 1000
        
        # Features
        X = pd.DataFrame({
            'amount': np.random.uniform(1000, 50000, n_samples),
            'duration': np.random.randint(6, 60, n_samples),
            'age': np.random.randint(18, 70, n_samples),
            'employment_duration': np.random.randint(0, 40, n_samples),
            'num_dependents': np.random.randint(0, 5, n_samples),
        })
        
        # Target (simulado)
        y = (X['amount'] / X['duration'] > 800).astype(int)
        
        # Entrenar modelo
        if self.model_type == "lightgbm":
            self.model = lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif self.model_type == "xgboost":
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        
        self.model.fit(X, y)
        self.feature_names = list(X.columns)
        self.is_trained = True
        
        # Inicializar explainer
        self.explainer = shap.TreeExplainer(self.model)
        
        logger.info(f"✅ Modelo dummy {self.model_type} entrenado con {n_samples} muestras")
    
    def _features_to_dataframe(self, features: DocumentFeatures) -> pd.DataFrame:
        """Convertir features a DataFrame para predicción"""
        data = {
            'amount': features.amount,
            'duration': features.duration,
            'age': features.age or 30,
            'employment_duration': features.employment_duration or 12,
            'num_dependents': features.num_dependents,
        }
        
        return pd.DataFrame([data])
    
    def predict(self, features: DocumentFeatures, explain: bool = True) -> Dict[str, Any]:
        """
        Realizar predicción con explicación SHAP
        
        Args:
            features: Características del documento
            explain: Si incluir explicación SHAP
        
        Returns:
            Diccionario con predicción y explicación
        """
        start_time = datetime.now()
        
        if not self.is_trained:
            raise ValueError("Modelo no está entrenado")
        
        # Convertir features a DataFrame
        X = self._features_to_dataframe(features)
        
        # Predicción
        prediction = int(self.model.predict(X)[0])
        probabilities = self.model.predict_proba(X)[0]
        probability = float(probabilities[prediction])
        confidence = float(max(probabilities))
        
        # Risk score (0-100)
        risk_score = float(probabilities[1] * 100)
        
        result = {
            "prediction": prediction,
            "probability": probability,
            "confidence": confidence,
            "risk_score": risk_score,
            "model_type": self.model_type
        }
        
        # Explicación SHAP
        if explain and self.explainer:
            shap_start = datetime.now()
            
            shap_values = self.explainer.shap_values(X)
            
            # Para clasificación binaria, tomar valores de clase positiva
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            
            explanation = {
                "feature_names": list(X.columns),
                "feature_values": X.iloc[0].tolist(),
                "shap_values": shap_values[0].tolist() if len(shap_values.shape) > 1 else shap_values.tolist(),
                "base_value": float(self.explainer.expected_value[1] if isinstance(self.explainer.expected_value, list) else self.explainer.expected_value),
                "expected_value": float(self.explainer.expected_value[1] if isinstance(self.explainer.expected_value, list) else self.explainer.expected_value)
            }
            
            result["explanation"] = explanation
            
            shap_time = (datetime.now() - shap_start).total_seconds()
            shap_computation_time.observe(shap_time)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result["execution_time"] = execution_time
        
        # Update metrics
        model_confidence.set(confidence)
        
        return result
    
    def batch_predict(self, features_list: List[DocumentFeatures], explain: bool = False) -> List[Dict[str, Any]]:
        """Predicción en batch"""
        results = []
        
        for features in features_list:
            try:
                result = self.predict(features, explain=explain)
                results.append(result)
            except Exception as e:
                logger.error(f"Error en predicción: {e}")
                results.append({
                    "error": str(e),
                    "document_id": features.document_id
                })
        
        return results

# Inicializar modelos
lightgbm_model = PredictiveMLModel(model_type="lightgbm")
xgboost_model = PredictiveMLModel(model_type="xgboost")

def get_model(model_type: str) -> PredictiveMLModel:
    """Obtener modelo según tipo"""
    if model_type == "lightgbm":
        return lightgbm_model
    elif model_type == "xgboost":
        return xgboost_model
    else:
        raise ValueError(f"Tipo de modelo no soportado: {model_type}")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint con información del servicio"""
    return {
        "service": "SageMaker Predictive ML Service",
        "version": "1.0.0",
        "status": "operational",
        "models": {
            "lightgbm": {
                "trained": lightgbm_model.is_trained,
                "features": lightgbm_model.feature_names
            },
            "xgboost": {
                "trained": xgboost_model.is_trained,
                "features": xgboost_model.feature_names
            }
        },
        "sagemaker_enabled": USE_SAGEMAKER,
        "endpoints": {
            "predict": "/predict",
            "batch_predict": "/batch-predict",
            "explain": "/explain",
            "health": "/health",
            "metrics": "/metrics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sagemaker-predictor",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "lightgbm": lightgbm_model.is_trained,
            "xgboost": xgboost_model.is_trained
        }
    }

@app.post("/predict", response_model=PredictionResult)
async def predict(request: PredictionRequest):
    """
    Realizar predicción con explicación SHAP
    
    Args:
        request: Features del documento y configuración
    
    Returns:
        Predicción con explicación
    """
    try:
        with prediction_latency.labels(model=request.model_type).time():
            model = get_model(request.model_type)
            
            result = model.predict(request.features, explain=request.explain)
            
            if request.features.document_id:
                result["document_id"] = request.features.document_id
            
            result["timestamp"] = datetime.now().isoformat()
            
            prediction_requests.labels(model=request.model_type, status='success').inc()
            
            return PredictionResult(**result)
    
    except Exception as e:
        prediction_requests.labels(model=request.model_type, status='error').inc()
        logger.error(f"Error en predicción: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-predict", response_model=BatchPredictionResult)
async def batch_predict(request: BatchPredictionRequest):
    """
    Predicción en batch
    
    Args:
        request: Lista de features y configuración
    
    Returns:
        Lista de predicciones
    """
    try:
        start_time = datetime.now()
        
        model = get_model(request.model_type)
        results = model.batch_predict(request.features_list, explain=request.explain)
        
        # Convertir a PredictionResult
        predictions = []
        for i, result in enumerate(results):
            if "error" not in result:
                result["timestamp"] = datetime.now().isoformat()
                if request.features_list[i].document_id:
                    result["document_id"] = request.features_list[i].document_id
                predictions.append(PredictionResult(**result))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return BatchPredictionResult(
            predictions=predictions,
            total_processed=len(predictions),
            execution_time=execution_time
        )
    
    except Exception as e:
        logger.error(f"Error en batch prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain")
async def explain_prediction(request: PredictionRequest):
    """
    Obtener solo la explicación SHAP de una predicción
    
    Args:
        request: Features del documento
    
    Returns:
        Explicación SHAP detallada
    """
    try:
        model = get_model(request.model_type)
        result = model.predict(request.features, explain=True)
        
        return {
            "explanation": result.get("explanation"),
            "prediction": result["prediction"],
            "risk_score": result["risk_score"],
            "model_type": request.model_type
        }
    
    except Exception as e:
        logger.error(f"Error en explicación: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/info")
async def get_models_info():
    """Información detallada de los modelos"""
    return {
        "lightgbm": {
            "type": "LightGBM Classifier",
            "trained": lightgbm_model.is_trained,
            "features": lightgbm_model.feature_names,
            "explainer": "SHAP TreeExplainer"
        },
        "xgboost": {
            "type": "XGBoost Classifier",
            "trained": xgboost_model.is_trained,
            "features": xgboost_model.feature_names,
            "explainer": "SHAP TreeExplainer"
        }
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")

@app.get("/stats")
async def get_stats():
    """Estadísticas del servicio"""
    return {
        "service": "sagemaker-predictor",
        "models": {
            "lightgbm": {
                "trained": lightgbm_model.is_trained,
                "type": lightgbm_model.model_type
            },
            "xgboost": {
                "trained": xgboost_model.is_trained,
                "type": xgboost_model.model_type
            }
        },
        "sagemaker": {
            "enabled": USE_SAGEMAKER,
            "endpoint": SAGEMAKER_ENDPOINT if USE_SAGEMAKER else None
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting SageMaker Predictive ML Service on port {SERVICE_PORT}")
    logger.info(f"📊 LightGBM Model: {'✅ Loaded' if lightgbm_model.is_trained else '❌ Not loaded'}")
    logger.info(f"📊 XGBoost Model: {'✅ Loaded' if xgboost_model.is_trained else '❌ Not loaded'}")
    logger.info(f"🔍 SHAP Explainability: Enabled")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=SERVICE_PORT,
        log_level="info"
    )
