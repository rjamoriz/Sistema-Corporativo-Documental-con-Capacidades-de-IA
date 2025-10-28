"""
Scoring Orchestrator Service
Orquesta múltiples modelos ML para generar scoring híbrido de clientes
Puerto: 8010
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import uvicorn

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus Metrics - with duplicate protection
for collector in list(REGISTRY._collector_to_names.keys()):
    try:
        REGISTRY.unregister(collector)
    except Exception:
        pass

scoring_requests = Counter('scoring_requests_total', 'Total scoring requests')
scoring_duration = Histogram('scoring_duration_seconds', 'Time to compute score')
model_calls = Counter('model_calls_total', 'Model API calls', ['model', 'status'])
ensemble_scores = Histogram('ensemble_scores', 'Distribution of ensemble scores')

# Configuration
DOCUMENT_EXTRACTOR_URL = os.getenv("DOCUMENT_EXTRACTOR_URL", "http://document-feature-extractor:8009")
SAGEMAKER_URL = os.getenv("SAGEMAKER_URL", "http://sagemaker-predictor:8008")
QUANTUM_ML_URL = os.getenv("QUANTUM_ML_URL", "http://quantum-ml-pennylane:8007")
ASTRA_DB_URL = os.getenv("ASTRA_DB_URL", "http://astra-vector-db-service:8006")

# Timeouts
HTTP_TIMEOUT = 30.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    logger.info("🚀 Starting Scoring Orchestrator Service...")
    logger.info(f"📄 Document Extractor: {DOCUMENT_EXTRACTOR_URL}")
    logger.info(f"🤖 SageMaker: {SAGEMAKER_URL}")
    logger.info(f"⚛️ Quantum ML: {QUANTUM_ML_URL}")
    logger.info(f"🗄️ Astra DB: {ASTRA_DB_URL}")
    yield
    logger.info("👋 Shutting down Scoring Orchestrator Service")


app = FastAPI(
    title="Scoring Orchestrator API",
    description="Orquesta múltiples modelos ML para scoring híbrido",
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

class ScoringDecision(str, Enum):
    APPROVED = "APPROVED"
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REJECTED = "REJECTED"


class StructuredData(BaseModel):
    """Datos estructurados del cliente"""
    age: int = Field(..., description="Edad del cliente")
    income: float = Field(..., description="Ingresos anuales")
    credit_history_months: int = Field(..., description="Meses de historial crediticio")
    num_operations: int = Field(..., description="Número de operaciones previas")
    amount: Optional[float] = Field(None, description="Monto solicitado")
    duration: Optional[int] = Field(None, description="Duración en meses")


class ScoringRequest(BaseModel):
    customer_id: str = Field(..., description="ID del cliente")
    structured_data: StructuredData = Field(..., description="Datos estructurados")
    document_texts: Optional[List[str]] = Field(None, description="Textos de documentos")
    use_quantum: bool = Field(True, description="Usar modelo cuántico")
    use_sagemaker: bool = Field(True, description="Usar SageMaker")
    explain: bool = Field(True, description="Incluir explicaciones")


class ModelPrediction(BaseModel):
    model_name: str
    prediction: Optional[int] = None
    probability: Optional[float] = None
    score: Optional[float] = None
    confidence: Optional[float] = None
    execution_time_ms: float
    success: bool
    error: Optional[str] = None


class ScoringExplanation(BaseModel):
    main_factors: List[str]
    structured_contribution: float
    unstructured_contribution: float
    quantum_contribution: Optional[float] = None
    top_positive_features: List[Dict[str, float]]
    top_negative_features: List[Dict[str, float]]


class ScoringResponse(BaseModel):
    customer_id: str
    final_score: float = Field(..., description="Score final (0-100)")
    decision: ScoringDecision
    confidence: float = Field(..., description="Confianza de la decisión (0-1)")
    
    # Predicciones individuales
    sagemaker_prediction: Optional[ModelPrediction] = None
    quantum_prediction: Optional[ModelPrediction] = None
    document_features: Optional[Dict[str, Any]] = None
    
    # Explicación
    explanation: Optional[ScoringExplanation] = None
    
    # Metadata
    timestamp: str
    processing_time_ms: float
    models_used: List[str]


# ============================================
# ORCHESTRATION LOGIC
# ============================================

class ScoringOrchestrator:
    """Orquestador de scoring híbrido"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=HTTP_TIMEOUT)
    
    async def close(self):
        """Cerrar cliente HTTP"""
        await self.http_client.aclose()
    
    async def extract_document_features(
        self,
        customer_id: str,
        document_texts: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Extrae features de documentos"""
        if not document_texts:
            return None
        
        try:
            start_time = datetime.utcnow()
            
            response = await self.http_client.post(
                f"{DOCUMENT_EXTRACTOR_URL}/extract-features",
                json={
                    "customer_id": customer_id,
                    "document_texts": document_texts
                }
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                model_calls.labels(model='document_extractor', status='success').inc()
                features = response.json()
                features['execution_time_ms'] = execution_time
                return features
            else:
                model_calls.labels(model='document_extractor', status='error').inc()
                logger.error(f"Document extractor error: {response.status_code}")
                return None
                
        except Exception as e:
            model_calls.labels(model='document_extractor', status='error').inc()
            logger.error(f"Error calling document extractor: {e}")
            return None
    
    async def call_sagemaker(
        self,
        structured_data: Dict[str, Any],
        document_features: Optional[Dict[str, Any]],
        explain: bool
    ) -> ModelPrediction:
        """Llama a SageMaker predictor"""
        try:
            start_time = datetime.utcnow()
            
            # Combinar features estructuradas + documentales
            features = structured_data.copy()
            
            if document_features:
                features.update({
                    "doc_sentiment": document_features.get("sentiment_score", 0.0),
                    "doc_risk_score": document_features.get("risk_keywords_count", 0) / 10.0,
                    "doc_completeness": document_features.get("document_completeness", 0.5)
                })
            
            response = await self.http_client.post(
                f"{SAGEMAKER_URL}/predict",
                json={
                    "features": features,
                    "explain": explain
                }
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                model_calls.labels(model='sagemaker', status='success').inc()
                result = response.json()
                
                return ModelPrediction(
                    model_name="SageMaker LightGBM",
                    prediction=result.get("prediction"),
                    probability=result.get("probability"),
                    score=result.get("risk_score"),
                    confidence=result.get("probability"),
                    execution_time_ms=execution_time,
                    success=True
                )
            else:
                model_calls.labels(model='sagemaker', status='error').inc()
                return ModelPrediction(
                    model_name="SageMaker LightGBM",
                    execution_time_ms=execution_time,
                    success=False,
                    error=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            model_calls.labels(model='sagemaker', status='error').inc()
            logger.error(f"Error calling SageMaker: {e}")
            return ModelPrediction(
                model_name="SageMaker LightGBM",
                execution_time_ms=0,
                success=False,
                error=str(e)
            )
    
    async def call_quantum_ml(
        self,
        embedding: List[float],
        explain: bool
    ) -> ModelPrediction:
        """Llama a Quantum ML"""
        try:
            start_time = datetime.utcnow()
            
            response = await self.http_client.post(
                f"{QUANTUM_ML_URL}/qml/classify",
                json={
                    "embedding": embedding,
                    "explain": explain
                }
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                model_calls.labels(model='quantum_ml', status='success').inc()
                result = response.json()
                
                return ModelPrediction(
                    model_name="Quantum VQC",
                    prediction=result.get("predicted_class"),
                    confidence=result.get("confidence"),
                    score=result.get("confidence", 0.5) * 100,
                    execution_time_ms=execution_time,
                    success=True
                )
            else:
                model_calls.labels(model='quantum_ml', status='error').inc()
                return ModelPrediction(
                    model_name="Quantum VQC",
                    execution_time_ms=execution_time,
                    success=False,
                    error=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            model_calls.labels(model='quantum_ml', status='error').inc()
            logger.error(f"Error calling Quantum ML: {e}")
            return ModelPrediction(
                model_name="Quantum VQC",
                execution_time_ms=0,
                success=False,
                error=str(e)
            )
    
    def create_embedding_from_data(
        self,
        structured_data: Dict[str, Any],
        document_features: Optional[Dict[str, Any]]
    ) -> List[float]:
        """Crea embedding simple para Quantum ML"""
        # Normalizar datos estructurados
        embedding = [
            structured_data.get("age", 35) / 100.0,
            structured_data.get("income", 30000) / 100000.0,
            structured_data.get("credit_history_months", 12) / 120.0,
            structured_data.get("num_operations", 5) / 50.0
        ]
        
        # Añadir features documentales si existen
        if document_features:
            embedding.extend([
                document_features.get("sentiment_score", 0.0),
                document_features.get("document_completeness", 0.5),
                document_features.get("risk_keywords_count", 0) / 10.0,
                document_features.get("text_quality_score", 0.5)
            ])
        else:
            embedding.extend([0.0, 0.5, 0.0, 0.5])
        
        return embedding
    
    def compute_ensemble_score(
        self,
        sagemaker_pred: Optional[ModelPrediction],
        quantum_pred: Optional[ModelPrediction],
        document_features: Optional[Dict[str, Any]]
    ) -> tuple[float, ScoringDecision, float]:
        """Calcula score final mediante ensemble"""
        
        scores = []
        weights = []
        
        # SageMaker score
        if sagemaker_pred and sagemaker_pred.success and sagemaker_pred.score:
            scores.append(sagemaker_pred.score)
            weights.append(0.5)  # 50% peso
        
        # Quantum ML score
        if quantum_pred and quantum_pred.success and quantum_pred.score:
            scores.append(quantum_pred.score)
            weights.append(0.3)  # 30% peso
        
        # Document quality score
        if document_features:
            doc_score = (
                document_features.get("sentiment_score", 0.0) * 30 +
                document_features.get("document_completeness", 0.5) * 40 +
                (1.0 - document_features.get("risk_keywords_count", 0) / 10.0) * 30
            )
            scores.append(max(0, min(100, doc_score)))
            weights.append(0.2)  # 20% peso
        
        # Calcular weighted average
        if not scores:
            return 50.0, ScoringDecision.REVIEW_REQUIRED, 0.3
        
        total_weight = sum(weights)
        final_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        # Determinar decisión
        if final_score >= 75:
            decision = ScoringDecision.APPROVED
            confidence = 0.9
        elif final_score >= 60:
            decision = ScoringDecision.APPROVED_WITH_CONDITIONS
            confidence = 0.75
        elif final_score >= 40:
            decision = ScoringDecision.REVIEW_REQUIRED
            confidence = 0.6
        else:
            decision = ScoringDecision.REJECTED
            confidence = 0.85
        
        ensemble_scores.observe(final_score)
        
        return final_score, decision, confidence
    
    def create_explanation(
        self,
        sagemaker_pred: Optional[ModelPrediction],
        quantum_pred: Optional[ModelPrediction],
        document_features: Optional[Dict[str, Any]]
    ) -> ScoringExplanation:
        """Crea explicación del scoring"""
        
        main_factors = []
        
        # Factores de SageMaker
        if sagemaker_pred and sagemaker_pred.success:
            if sagemaker_pred.probability and sagemaker_pred.probability > 0.7:
                main_factors.append(f"✅ Alta probabilidad de aprobación ML clásico ({sagemaker_pred.probability:.2%})")
            elif sagemaker_pred.probability and sagemaker_pred.probability < 0.4:
                main_factors.append(f"⚠️ Baja probabilidad según ML clásico ({sagemaker_pred.probability:.2%})")
        
        # Factores de Quantum
        if quantum_pred and quantum_pred.success:
            if quantum_pred.confidence and quantum_pred.confidence > 0.8:
                main_factors.append(f"✅ Alta confianza en modelo cuántico ({quantum_pred.confidence:.2%})")
        
        # Factores documentales
        if document_features:
            sentiment = document_features.get("sentiment_score", 0.0)
            if sentiment > 0.3:
                main_factors.append(f"✅ Sentimiento positivo en documentos ({sentiment:.2f})")
            elif sentiment < -0.3:
                main_factors.append(f"⚠️ Sentimiento negativo en documentos ({sentiment:.2f})")
            
            risk_count = document_features.get("risk_keywords_count", 0)
            if risk_count > 3:
                main_factors.append(f"⚠️ {risk_count} indicadores de riesgo en documentos")
            
            completeness = document_features.get("document_completeness", 0.0)
            if completeness > 0.8:
                main_factors.append(f"✅ Documentación completa ({completeness:.1%})")
            elif completeness < 0.5:
                main_factors.append(f"⚠️ Documentación incompleta ({completeness:.1%})")
        
        # Calcular contribuciones
        structured_contrib = 0.5 if sagemaker_pred and sagemaker_pred.success else 0.0
        unstructured_contrib = 0.2 if document_features else 0.0
        quantum_contrib = 0.3 if quantum_pred and quantum_pred.success else 0.0
        
        return ScoringExplanation(
            main_factors=main_factors if main_factors else ["Análisis basado en datos disponibles"],
            structured_contribution=structured_contrib,
            unstructured_contribution=unstructured_contrib,
            quantum_contribution=quantum_contrib,
            top_positive_features=[
                {"feature": "income", "impact": 0.15},
                {"feature": "credit_history", "impact": 0.12}
            ],
            top_negative_features=[
                {"feature": "risk_indicators", "impact": -0.08}
            ]
        )


# Global orchestrator instance
orchestrator: Optional[ScoringOrchestrator] = None


# ============================================
# ENDPOINTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator"""
    global orchestrator
    orchestrator = ScoringOrchestrator()
    logger.info("✅ Orchestrator initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup"""
    global orchestrator
    if orchestrator:
        await orchestrator.close()
    logger.info("✅ Orchestrator closed")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "scoring-orchestrator",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(REGISTRY)


@app.post("/score", response_model=ScoringResponse)
async def compute_score(request: ScoringRequest):
    """
    Calcula score híbrido de cliente
    """
    scoring_requests.inc()
    start_time = datetime.utcnow()
    
    try:
        with scoring_duration.time():
            models_used = []
            
            # 1. Extraer features de documentos
            document_features = None
            if request.document_texts:
                document_features = await orchestrator.extract_document_features(
                    request.customer_id,
                    request.document_texts
                )
                if document_features:
                    models_used.append("document_extractor")
            
            # 2. Llamar a SageMaker
            sagemaker_pred = None
            if request.use_sagemaker:
                sagemaker_pred = await orchestrator.call_sagemaker(
                    request.structured_data.dict(),
                    document_features,
                    request.explain
                )
                if sagemaker_pred.success:
                    models_used.append("sagemaker")
            
            # 3. Llamar a Quantum ML
            quantum_pred = None
            if request.use_quantum:
                embedding = orchestrator.create_embedding_from_data(
                    request.structured_data.dict(),
                    document_features
                )
                quantum_pred = await orchestrator.call_quantum_ml(
                    embedding,
                    request.explain
                )
                if quantum_pred.success:
                    models_used.append("quantum_ml")
            
            # 4. Ensemble scoring
            final_score, decision, confidence = orchestrator.compute_ensemble_score(
                sagemaker_pred,
                quantum_pred,
                document_features
            )
            
            # 5. Crear explicación
            explanation = None
            if request.explain:
                explanation = orchestrator.create_explanation(
                    sagemaker_pred,
                    quantum_pred,
                    document_features
                )
            
            # Calcular tiempo total
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            response = ScoringResponse(
                customer_id=request.customer_id,
                final_score=round(final_score, 2),
                decision=decision,
                confidence=round(confidence, 3),
                sagemaker_prediction=sagemaker_pred,
                quantum_prediction=quantum_pred,
                document_features=document_features,
                explanation=explanation,
                timestamp=datetime.utcnow().isoformat(),
                processing_time_ms=round(processing_time, 2),
                models_used=models_used
            )
            
            logger.info(f"✅ Score computed for {request.customer_id}: {final_score:.2f} ({decision})")
            return response
            
    except Exception as e:
        logger.error(f"❌ Error computing score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Estadísticas del servicio"""
    return {
        "service": "scoring-orchestrator",
        "version": "1.0.0",
        "status": "operational",
        "models_integrated": [
            "document_feature_extractor",
            "sagemaker_predictor",
            "quantum_ml_pennylane"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8010))
    logger.info(f"🚀 Starting Scoring Orchestrator on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
