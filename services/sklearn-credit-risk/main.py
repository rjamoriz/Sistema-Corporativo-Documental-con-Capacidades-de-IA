"""
Scikit-Learn Credit Risk ML Service
Scoring de riesgo crediticio con ML clásico + features híbridas
Puerto: 8011
"""

import os
import logging
import pickle
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import uvicorn

# Scikit-learn imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
import joblib

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus Metrics - with duplicate protection
for collector in list(REGISTRY._collector_to_names.keys()):
    try:
        REGISTRY.unregister(collector)
    except Exception:
        pass

prediction_requests = Counter('sklearn_prediction_requests_total', 'Total prediction requests')
prediction_duration = Histogram('sklearn_prediction_duration_seconds', 'Time to predict')
model_loads = Counter('sklearn_model_loads_total', 'Model load operations', ['model_type'])
risk_scores = Histogram('sklearn_risk_scores', 'Distribution of risk scores')
default_predictions = Counter('sklearn_default_predictions_total', 'Default predictions', ['prediction'])
fraud_detections = Counter('sklearn_fraud_detections_total', 'Fraud detections')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    logger.info("🚀 Starting Scikit-Learn Credit Risk ML Service...")
    
    # Initialize models
    global credit_risk_model, fraud_detector, scaler
    credit_risk_model = _create_credit_risk_model()
    fraud_detector = _create_fraud_detector()
    scaler = StandardScaler()
    
    logger.info("✅ Models initialized")
    yield
    logger.info("👋 Shutting down Scikit-Learn Credit Risk ML Service")


app = FastAPI(
    title="Scikit-Learn Credit Risk ML API",
    description="Scoring de riesgo crediticio con ML clásico y detección de fraude",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# MODELS
# ============================================

class RiskLevel(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class DecisionType(str, Enum):
    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    REJECTED = "REJECTED"


class StructuredFeatures(BaseModel):
    """Features estructuradas del cliente"""
    # Demográficas
    age: int = Field(..., ge=18, le=100, description="Edad del cliente")
    income: float = Field(..., ge=0, description="Ingresos anuales")
    employment_years: int = Field(..., ge=0, description="Años de empleo")
    
    # Historial crediticio
    credit_history_months: int = Field(..., ge=0, description="Meses de historial")
    num_previous_loans: int = Field(..., ge=0, description="Préstamos previos")
    num_defaults: int = Field(0, ge=0, description="Impagos históricos")
    external_credit_score: Optional[int] = Field(None, ge=300, le=850, description="Score externo")
    
    # Operación actual
    loan_amount: float = Field(..., gt=0, description="Monto solicitado")
    loan_duration_months: int = Field(..., gt=0, le=360, description="Duración en meses")
    loan_purpose: str = Field(..., description="Propósito del préstamo")
    
    # Relación con la entidad
    customer_tenure_months: int = Field(..., ge=0, description="Antigüedad como cliente")
    num_products: int = Field(0, ge=0, description="Productos contratados")
    avg_balance: float = Field(0, ge=0, description="Saldo promedio")


class UnstructuredFeatures(BaseModel):
    """Features extraídas de documentos no estructurados"""
    # Sentimiento y tono
    doc_sentiment_score: float = Field(0.0, ge=-1, le=1, description="Sentiment score")
    communication_tone: str = Field("neutral", description="Tono de comunicaciones")
    
    # Entidades extraídas
    num_monetary_amounts: int = Field(0, ge=0, description="Montos mencionados")
    total_amount_mentioned: float = Field(0, ge=0, description="Suma de montos")
    num_dates_mentioned: int = Field(0, ge=0, description="Fechas mencionadas")
    num_identifiers: int = Field(0, ge=0, description="Identificadores encontrados")
    
    # Indicadores de riesgo documental
    risk_clauses_count: int = Field(0, ge=0, description="Cláusulas de riesgo")
    inconsistencies_detected: int = Field(0, ge=0, description="Inconsistencias")
    payment_delay_mentions: int = Field(0, ge=0, description="Menciones de retrasos")
    legal_issues_mentions: int = Field(0, ge=0, description="Problemas legales")
    restructuring_mentions: int = Field(0, ge=0, description="Reestructuraciones")
    
    # Calidad documental
    document_completeness: float = Field(1.0, ge=0, le=1, description="Completitud")
    document_quality_score: float = Field(1.0, ge=0, le=1, description="Calidad")
    
    # Embeddings (opcional)
    contract_embedding: Optional[List[float]] = Field(None, description="Vector embedding del contrato")


class PredictionRequest(BaseModel):
    customer_id: str = Field(..., description="ID del cliente")
    structured_features: StructuredFeatures
    unstructured_features: Optional[UnstructuredFeatures] = None
    check_fraud: bool = Field(True, description="Ejecutar detección de fraude")
    explain: bool = Field(True, description="Incluir explicación")


class FeatureImportance(BaseModel):
    feature_name: str
    importance: float
    impact: str  # "positive" or "negative"


class RiskExplanation(BaseModel):
    main_risk_factors: List[str]
    protective_factors: List[str]
    top_features: List[FeatureImportance]
    risk_level: RiskLevel
    confidence: float


class FraudAnalysis(BaseModel):
    is_suspicious: bool
    anomaly_score: float
    suspicious_patterns: List[str]
    confidence: float


class PredictionResponse(BaseModel):
    customer_id: str
    
    # Predicción principal
    default_probability: float = Field(..., description="Probabilidad de impago (0-1)")
    risk_score: float = Field(..., description="Score de riesgo (0-100)")
    risk_level: RiskLevel
    decision: DecisionType
    
    # Análisis de fraude
    fraud_analysis: Optional[FraudAnalysis] = None
    
    # Explicación
    explanation: Optional[RiskExplanation] = None
    
    # Métricas de calibración
    calibrated_probability: float = Field(..., description="Probabilidad calibrada")
    confidence_interval: Tuple[float, float] = Field(..., description="Intervalo de confianza 95%")
    
    # Metadata
    model_version: str
    prediction_timestamp: str
    processing_time_ms: float


# ============================================
# MODEL CREATION
# ============================================

def _create_credit_risk_model():
    """Crea modelo de riesgo crediticio (dummy para desarrollo)"""
    logger.info("📊 Creating credit risk model...")
    
    # En producción, cargar modelo entrenado
    # model = joblib.load('models/credit_risk_model.pkl')
    
    # Para desarrollo: modelo dummy
    model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    # Entrenar con datos dummy
    X_dummy = np.random.randn(1000, 20)
    y_dummy = np.random.randint(0, 2, 1000)
    model.fit(X_dummy, y_dummy)
    
    # Calibrar probabilidades
    calibrated_model = CalibratedClassifierCV(model, cv=3, method='sigmoid')
    calibrated_model.fit(X_dummy, y_dummy)
    
    model_loads.labels(model_type='credit_risk').inc()
    logger.info("✅ Credit risk model loaded")
    
    return calibrated_model


def _create_fraud_detector():
    """Crea detector de fraude (Isolation Forest)"""
    logger.info("🔍 Creating fraud detector...")
    
    # Isolation Forest para detección de anomalías
    detector = IsolationForest(
        n_estimators=100,
        contamination=0.05,  # 5% de anomalías esperadas
        random_state=42
    )
    
    # Entrenar con datos dummy
    X_dummy = np.random.randn(1000, 20)
    detector.fit(X_dummy)
    
    model_loads.labels(model_type='fraud_detector').inc()
    logger.info("✅ Fraud detector loaded")
    
    return detector


# ============================================
# FEATURE ENGINEERING
# ============================================

class FeatureEngineer:
    """Ingeniero de features híbridas"""
    
    @staticmethod
    def create_features(
        structured: StructuredFeatures,
        unstructured: Optional[UnstructuredFeatures]
    ) -> np.ndarray:
        """Crea vector de features combinadas"""
        
        features = []
        
        # === FEATURES ESTRUCTURADAS ===
        
        # Demográficas normalizadas
        features.append(structured.age / 100.0)
        features.append(np.log1p(structured.income) / 15.0)  # Log-transform
        features.append(structured.employment_years / 40.0)
        
        # Historial crediticio
        features.append(structured.credit_history_months / 120.0)
        features.append(structured.num_previous_loans / 20.0)
        features.append(structured.num_defaults / 5.0)
        
        # Score externo normalizado
        if structured.external_credit_score:
            features.append((structured.external_credit_score - 300) / 550.0)
        else:
            features.append(0.5)  # Valor medio si no disponible
        
        # Operación actual
        features.append(np.log1p(structured.loan_amount) / 15.0)
        features.append(structured.loan_duration_months / 360.0)
        
        # Ratios importantes
        debt_to_income = structured.loan_amount / max(structured.income, 1)
        features.append(min(debt_to_income, 2.0) / 2.0)  # Cap at 2.0
        
        monthly_payment = structured.loan_amount / max(structured.loan_duration_months, 1)
        payment_to_income = (monthly_payment * 12) / max(structured.income, 1)
        features.append(min(payment_to_income, 1.0))  # Cap at 1.0
        
        # Relación con entidad
        features.append(structured.customer_tenure_months / 120.0)
        features.append(structured.num_products / 10.0)
        features.append(np.log1p(structured.avg_balance) / 15.0)
        
        # === FEATURES NO ESTRUCTURADAS ===
        
        if unstructured:
            # Sentimiento
            features.append((unstructured.doc_sentiment_score + 1) / 2.0)  # Normalize to [0,1]
            
            # Indicadores de riesgo documental
            features.append(unstructured.risk_clauses_count / 10.0)
            features.append(unstructured.inconsistencies_detected / 5.0)
            features.append(unstructured.payment_delay_mentions / 5.0)
            features.append(unstructured.legal_issues_mentions / 3.0)
            features.append(unstructured.restructuring_mentions / 3.0)
            
            # Calidad documental
            features.append(unstructured.document_completeness)
            features.append(unstructured.document_quality_score)
        else:
            # Valores por defecto si no hay docs
            features.extend([0.5] * 8)
        
        return np.array(features).reshape(1, -1)
    
    @staticmethod
    def get_feature_names() -> List[str]:
        """Retorna nombres de features"""
        return [
            "age_norm", "log_income", "employment_years",
            "credit_history", "num_loans", "num_defaults", "external_score",
            "log_loan_amount", "loan_duration",
            "debt_to_income_ratio", "payment_to_income_ratio",
            "customer_tenure", "num_products", "log_avg_balance",
            "doc_sentiment", "risk_clauses", "inconsistencies",
            "payment_delays", "legal_issues", "restructuring",
            "doc_completeness", "doc_quality"
        ]


# ============================================
# RISK ASSESSMENT
# ============================================

class RiskAssessor:
    """Evaluador de riesgo crediticio"""
    
    @staticmethod
    def assess_risk(probability: float) -> Tuple[RiskLevel, DecisionType]:
        """Determina nivel de riesgo y decisión"""
        
        if probability < 0.10:
            return RiskLevel.VERY_LOW, DecisionType.APPROVED
        elif probability < 0.20:
            return RiskLevel.LOW, DecisionType.APPROVED
        elif probability < 0.35:
            return RiskLevel.MEDIUM, DecisionType.APPROVED_WITH_CONDITIONS
        elif probability < 0.50:
            return RiskLevel.HIGH, DecisionType.MANUAL_REVIEW
        else:
            return RiskLevel.VERY_HIGH, DecisionType.REJECTED
    
    @staticmethod
    def calculate_confidence_interval(
        probability: float,
        n_samples: int = 1000
    ) -> Tuple[float, float]:
        """Calcula intervalo de confianza 95%"""
        # Aproximación usando distribución binomial
        std_error = np.sqrt(probability * (1 - probability) / n_samples)
        margin = 1.96 * std_error  # 95% CI
        
        lower = max(0.0, probability - margin)
        upper = min(1.0, probability + margin)
        
        return (round(lower, 4), round(upper, 4))
    
    @staticmethod
    def create_explanation(
        features: np.ndarray,
        feature_names: List[str],
        probability: float,
        risk_level: RiskLevel
    ) -> RiskExplanation:
        """Crea explicación de la predicción"""
        
        # Calcular importancias (simplificado)
        # En producción usar SHAP o feature_importances_ del modelo
        feature_values = features[0]
        
        # Identificar factores de riesgo y protectores
        risk_factors = []
        protective_factors = []
        top_features = []
        
        # Análisis de features clave
        if feature_values[5] > 0.2:  # num_defaults
            risk_factors.append(f"⚠️ Historial de {int(feature_values[5] * 5)} impagos previos")
        
        if feature_values[9] > 0.5:  # debt_to_income
            risk_factors.append(f"⚠️ Ratio deuda/ingresos alto ({feature_values[9]:.1%})")
        
        if feature_values[15] > 0.3:  # risk_clauses
            risk_factors.append(f"⚠️ {int(feature_values[15] * 10)} cláusulas de riesgo en documentos")
        
        if feature_values[17] > 0.2:  # payment_delays
            risk_factors.append("⚠️ Menciones de retrasos de pago en documentos")
        
        if feature_values[6] > 0.7:  # external_score
            protective_factors.append("✅ Excelente score crediticio externo")
        
        if feature_values[11] > 0.5:  # customer_tenure
            protective_factors.append("✅ Cliente de larga antigüedad")
        
        if feature_values[14] > 0.6:  # doc_sentiment
            protective_factors.append("✅ Sentimiento positivo en documentos")
        
        if feature_values[20] > 0.8:  # doc_completeness
            protective_factors.append("✅ Documentación completa y de calidad")
        
        # Top features por importancia
        for i, (name, value) in enumerate(zip(feature_names[:10], feature_values[:10])):
            importance = abs(value - 0.5)  # Simplificado
            impact = "positive" if value < 0.5 else "negative"
            top_features.append(FeatureImportance(
                feature_name=name,
                importance=round(importance, 3),
                impact=impact
            ))
        
        top_features.sort(key=lambda x: x.importance, reverse=True)
        
        # Confianza basada en calidad de datos
        confidence = 0.7 + (feature_values[20] * 0.3)  # Basado en doc_completeness
        
        return RiskExplanation(
            main_risk_factors=risk_factors if risk_factors else ["Sin factores de riesgo significativos"],
            protective_factors=protective_factors if protective_factors else ["Perfil estándar"],
            top_features=top_features[:5],
            risk_level=risk_level,
            confidence=round(confidence, 3)
        )


class FraudAnalyzer:
    """Analizador de fraude"""
    
    @staticmethod
    def analyze_fraud(
        features: np.ndarray,
        detector: IsolationForest,
        structured: StructuredFeatures,
        unstructured: Optional[UnstructuredFeatures]
    ) -> FraudAnalysis:
        """Analiza posible fraude"""
        
        # Predicción de anomalía
        prediction = detector.predict(features)
        anomaly_score = detector.score_samples(features)[0]
        
        is_suspicious = prediction[0] == -1
        
        # Normalizar score a [0,1]
        normalized_score = 1 / (1 + np.exp(anomaly_score))
        
        # Identificar patrones sospechosos
        suspicious_patterns = []
        
        # Patrón 1: Solicitud muy alta vs ingresos
        if structured.loan_amount > structured.income * 3:
            suspicious_patterns.append("Monto solicitado muy alto respecto a ingresos")
        
        # Patrón 2: Cliente nuevo con préstamo grande
        if structured.customer_tenure_months < 6 and structured.loan_amount > 50000:
            suspicious_patterns.append("Cliente nuevo solicitando monto elevado")
        
        # Patrón 3: Inconsistencias documentales
        if unstructured and unstructured.inconsistencies_detected > 2:
            suspicious_patterns.append(f"{unstructured.inconsistencies_detected} inconsistencias en documentos")
        
        # Patrón 4: Múltiples reestructuraciones
        if unstructured and unstructured.restructuring_mentions > 1:
            suspicious_patterns.append("Múltiples reestructuraciones mencionadas")
        
        # Patrón 5: Documentación incompleta
        if unstructured and unstructured.document_completeness < 0.5:
            suspicious_patterns.append("Documentación significativamente incompleta")
        
        confidence = min(0.95, normalized_score + 0.1 * len(suspicious_patterns))
        
        if is_suspicious:
            fraud_detections.inc()
        
        return FraudAnalysis(
            is_suspicious=is_suspicious,
            anomaly_score=round(normalized_score, 4),
            suspicious_patterns=suspicious_patterns if suspicious_patterns else ["Sin patrones sospechosos detectados"],
            confidence=round(confidence, 3)
        )


# Global instances
credit_risk_model = None
fraud_detector = None
scaler = None


# ============================================
# ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sklearn-credit-risk",
        "version": "1.0.0",
        "models_loaded": {
            "credit_risk": credit_risk_model is not None,
            "fraud_detector": fraud_detector is not None
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(REGISTRY)


@app.post("/predict", response_model=PredictionResponse)
async def predict_risk(request: PredictionRequest):
    """
    Predice riesgo de impago y detecta fraude
    """
    prediction_requests.inc()
    start_time = datetime.utcnow()
    
    try:
        with prediction_duration.time():
            # 1. Feature engineering
            features = FeatureEngineer.create_features(
                request.structured_features,
                request.unstructured_features
            )
            feature_names = FeatureEngineer.get_feature_names()
            
            # 2. Predicción de riesgo
            probability = credit_risk_model.predict_proba(features)[0][1]
            calibrated_prob = probability  # Ya está calibrado
            
            # 3. Score de riesgo (0-100)
            risk_score = round(calibrated_prob * 100, 2)
            risk_scores.observe(risk_score)
            
            # 4. Nivel de riesgo y decisión
            risk_level, decision = RiskAssessor.assess_risk(calibrated_prob)
            
            default_predictions.labels(prediction=str(int(calibrated_prob > 0.5))).inc()
            
            # 5. Intervalo de confianza
            conf_interval = RiskAssessor.calculate_confidence_interval(calibrated_prob)
            
            # 6. Explicación
            explanation = None
            if request.explain:
                explanation = RiskAssessor.create_explanation(
                    features,
                    feature_names,
                    calibrated_prob,
                    risk_level
                )
            
            # 7. Análisis de fraude
            fraud_analysis = None
            if request.check_fraud:
                fraud_analysis = FraudAnalyzer.analyze_fraud(
                    features,
                    fraud_detector,
                    request.structured_features,
                    request.unstructured_features
                )
            
            # 8. Calcular tiempo de procesamiento
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            response = PredictionResponse(
                customer_id=request.customer_id,
                default_probability=round(probability, 4),
                risk_score=risk_score,
                risk_level=risk_level,
                decision=decision,
                fraud_analysis=fraud_analysis,
                explanation=explanation,
                calibrated_probability=round(calibrated_prob, 4),
                confidence_interval=conf_interval,
                model_version="1.0.0",
                prediction_timestamp=datetime.utcnow().isoformat(),
                processing_time_ms=round(processing_time, 2)
            )
            
            logger.info(f"✅ Prediction for {request.customer_id}: Risk={risk_score}, Decision={decision}")
            return response
            
    except Exception as e:
        logger.error(f"❌ Error in prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model-info")
async def get_model_info():
    """Información del modelo"""
    return {
        "service": "sklearn-credit-risk",
        "version": "1.0.0",
        "models": {
            "credit_risk": {
                "type": "GradientBoostingClassifier",
                "calibrated": True,
                "features": len(FeatureEngineer.get_feature_names())
            },
            "fraud_detector": {
                "type": "IsolationForest",
                "contamination": 0.05
            }
        },
        "capabilities": [
            "default_probability_prediction",
            "risk_scoring",
            "fraud_detection",
            "feature_importance",
            "calibrated_probabilities",
            "confidence_intervals"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/stats")
async def get_stats():
    """Estadísticas del servicio"""
    return {
        "service": "sklearn-credit-risk",
        "version": "1.0.0",
        "status": "operational",
        "features_used": {
            "structured": 14,
            "unstructured": 8,
            "total": 22
        },
        "risk_levels": [level.value for level in RiskLevel],
        "decisions": [decision.value for decision in DecisionType],
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8011))
    logger.info(f"🚀 Starting Scikit-Learn Credit Risk ML on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
