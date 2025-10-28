"""
Document Feature Extractor Service
Extrae features de documentos no estructurados para scoring de clientes
Puerto: 8009
"""

import os
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager

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

extraction_requests = Counter('extraction_requests_total', 'Total feature extraction requests')
extraction_duration = Histogram('extraction_duration_seconds', 'Time to extract features')
features_extracted = Counter('features_extracted_total', 'Total features extracted', ['feature_type'])

# Configuration
ASTRA_SERVICE_URL = os.getenv("ASTRA_SERVICE_URL", "http://astra-vector-db-service:8006")
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://rag-enhanced-service:8005")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    logger.info("🚀 Starting Document Feature Extractor Service...")
    logger.info(f"📊 Astra Service: {ASTRA_SERVICE_URL}")
    logger.info(f"📖 RAG Service: {RAG_SERVICE_URL}")
    yield
    logger.info("👋 Shutting down Document Feature Extractor Service")


app = FastAPI(
    title="Document Feature Extractor API",
    description="Extrae features de documentos no estructurados para scoring",
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

class DocumentInput(BaseModel):
    customer_id: str = Field(..., description="ID del cliente")
    document_texts: List[str] = Field(..., description="Textos de documentos del cliente")
    document_types: Optional[List[str]] = Field(None, description="Tipos de documentos (contract, invoice, email, etc)")


class DocumentFeatures(BaseModel):
    customer_id: str
    
    # Features de sentimiento
    sentiment_score: float = Field(..., description="Score de sentimiento general (-1 a 1)")
    sentiment_positive_ratio: float = Field(..., description="Ratio de sentimiento positivo")
    
    # Features de entidades
    num_monetary_amounts: int = Field(..., description="Número de montos monetarios mencionados")
    total_amount_mentioned: float = Field(..., description="Suma total de montos mencionados")
    num_dates_mentioned: int = Field(..., description="Número de fechas mencionadas")
    num_identifiers: int = Field(..., description="Número de identificadores (NIF, CIF, etc)")
    
    # Features de riesgo
    risk_keywords_count: int = Field(..., description="Palabras clave de riesgo detectadas")
    payment_delay_mentions: int = Field(..., description="Menciones de retrasos de pago")
    legal_issues_mentions: int = Field(..., description="Menciones de problemas legales")
    
    # Features de completitud
    document_completeness: float = Field(..., description="Score de completitud documental (0-1)")
    num_documents: int = Field(..., description="Número de documentos analizados")
    avg_document_length: float = Field(..., description="Longitud promedio de documentos")
    
    # Features de calidad
    text_quality_score: float = Field(..., description="Score de calidad del texto (0-1)")
    has_structured_data: bool = Field(..., description="Contiene datos estructurados")
    
    # Metadata
    extraction_timestamp: str = Field(..., description="Timestamp de extracción")
    confidence: float = Field(..., description="Confianza general de la extracción")


# ============================================
# FEATURE EXTRACTION LOGIC
# ============================================

class FeatureExtractor:
    """Extractor de features de documentos"""
    
    # Keywords de riesgo
    RISK_KEYWORDS = [
        'impago', 'mora', 'retraso', 'incumplimiento', 'deuda', 'reclamación',
        'demanda', 'judicial', 'embargo', 'insolvencia', 'quiebra', 'concurso',
        'default', 'delay', 'overdue', 'debt', 'lawsuit', 'bankruptcy'
    ]
    
    # Keywords de pago
    PAYMENT_KEYWORDS = [
        'retraso de pago', 'pago atrasado', 'pago pendiente', 'impago',
        'payment delay', 'late payment', 'overdue payment'
    ]
    
    # Keywords legales
    LEGAL_KEYWORDS = [
        'demanda', 'juicio', 'tribunal', 'sentencia', 'litigio', 'recurso',
        'lawsuit', 'court', 'legal action', 'litigation'
    ]
    
    @staticmethod
    def extract_sentiment(texts: List[str]) -> Dict[str, float]:
        """Extrae sentiment score básico"""
        positive_words = ['bueno', 'excelente', 'satisfecho', 'correcto', 'positivo', 'good', 'excellent', 'satisfied']
        negative_words = ['malo', 'problema', 'insatisfecho', 'incorrecto', 'negativo', 'bad', 'problem', 'unsatisfied']
        
        total_positive = 0
        total_negative = 0
        
        for text in texts:
            text_lower = text.lower()
            total_positive += sum(1 for word in positive_words if word in text_lower)
            total_negative += sum(1 for word in negative_words if word in text_lower)
        
        total_words = total_positive + total_negative
        if total_words == 0:
            return {"score": 0.0, "positive_ratio": 0.5}
        
        sentiment_score = (total_positive - total_negative) / max(total_words, 1)
        positive_ratio = total_positive / total_words if total_words > 0 else 0.5
        
        return {
            "score": max(-1.0, min(1.0, sentiment_score)),
            "positive_ratio": positive_ratio
        }
    
    @staticmethod
    def extract_monetary_amounts(texts: List[str]) -> Dict[str, Any]:
        """Extrae montos monetarios"""
        # Patrones para detectar montos: 1.000€, $1,000, 1000 EUR, etc
        patterns = [
            r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s*(?:€|EUR|USD|\$|euros?|dólares?)',
            r'(?:€|USD|\$)\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?'
        ]
        
        amounts = []
        for text in texts:
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Extraer solo números
                    numbers = re.findall(r'\d+(?:[.,]\d+)?', match)
                    if numbers:
                        try:
                            amount = float(numbers[0].replace(',', '.'))
                            amounts.append(amount)
                        except ValueError:
                            continue
        
        return {
            "count": len(amounts),
            "total": sum(amounts) if amounts else 0.0
        }
    
    @staticmethod
    def extract_dates(texts: List[str]) -> int:
        """Extrae fechas mencionadas"""
        # Patrones de fecha: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, etc
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        ]
        
        count = 0
        for text in texts:
            for pattern in date_patterns:
                count += len(re.findall(pattern, text))
        
        return count
    
    @staticmethod
    def extract_identifiers(texts: List[str]) -> int:
        """Extrae identificadores (NIF, CIF, etc)"""
        # Patrones para NIF/CIF español y otros identificadores
        patterns = [
            r'\b[A-Z]\d{7}[A-Z0-9]\b',  # NIF/CIF español
            r'\b\d{8}[A-Z]\b',  # DNI español
            r'\bNIF[:\s]*[A-Z0-9-]+\b',
            r'\bCIF[:\s]*[A-Z0-9-]+\b'
        ]
        
        count = 0
        for text in texts:
            for pattern in patterns:
                count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return count
    
    @staticmethod
    def extract_risk_indicators(texts: List[str]) -> Dict[str, int]:
        """Extrae indicadores de riesgo"""
        risk_count = 0
        payment_delay_count = 0
        legal_count = 0
        
        for text in texts:
            text_lower = text.lower()
            
            # Risk keywords
            risk_count += sum(1 for keyword in FeatureExtractor.RISK_KEYWORDS if keyword in text_lower)
            
            # Payment delays
            payment_delay_count += sum(1 for keyword in FeatureExtractor.PAYMENT_KEYWORDS if keyword in text_lower)
            
            # Legal issues
            legal_count += sum(1 for keyword in FeatureExtractor.LEGAL_KEYWORDS if keyword in text_lower)
        
        return {
            "risk_keywords": risk_count,
            "payment_delays": payment_delay_count,
            "legal_issues": legal_count
        }
    
    @staticmethod
    def calculate_document_quality(texts: List[str]) -> Dict[str, Any]:
        """Calcula métricas de calidad documental"""
        if not texts:
            return {
                "completeness": 0.0,
                "quality_score": 0.0,
                "avg_length": 0.0,
                "has_structured": False
            }
        
        total_length = sum(len(text) for text in texts)
        avg_length = total_length / len(texts)
        
        # Completeness basado en número y longitud de docs
        completeness = min(1.0, (len(texts) / 5.0) * (avg_length / 1000.0))
        
        # Quality score basado en presencia de estructura
        has_structured = any(
            any(indicator in text for indicator in [':', '|', '\t', '  '])
            for text in texts
        )
        
        quality_score = 0.5
        if avg_length > 100:
            quality_score += 0.2
        if has_structured:
            quality_score += 0.3
        
        return {
            "completeness": min(1.0, completeness),
            "quality_score": min(1.0, quality_score),
            "avg_length": avg_length,
            "has_structured": has_structured
        }


# ============================================
# ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "document-feature-extractor",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(REGISTRY)


@app.post("/extract-features", response_model=DocumentFeatures)
async def extract_features(input_data: DocumentInput):
    """
    Extrae features de documentos para scoring
    """
    extraction_requests.inc()
    
    try:
        with extraction_duration.time():
            extractor = FeatureExtractor()
            
            # Extraer sentiment
            sentiment = extractor.extract_sentiment(input_data.document_texts)
            features_extracted.labels(feature_type='sentiment').inc()
            
            # Extraer montos
            monetary = extractor.extract_monetary_amounts(input_data.document_texts)
            features_extracted.labels(feature_type='monetary').inc()
            
            # Extraer fechas
            num_dates = extractor.extract_dates(input_data.document_texts)
            features_extracted.labels(feature_type='dates').inc()
            
            # Extraer identificadores
            num_ids = extractor.extract_identifiers(input_data.document_texts)
            features_extracted.labels(feature_type='identifiers').inc()
            
            # Extraer indicadores de riesgo
            risk_indicators = extractor.extract_risk_indicators(input_data.document_texts)
            features_extracted.labels(feature_type='risk').inc()
            
            # Calcular calidad documental
            quality = extractor.calculate_document_quality(input_data.document_texts)
            features_extracted.labels(feature_type='quality').inc()
            
            # Calcular confianza general
            confidence = (
                0.3 * quality['quality_score'] +
                0.3 * quality['completeness'] +
                0.2 * (1.0 if num_ids > 0 else 0.5) +
                0.2 * (1.0 if monetary['count'] > 0 else 0.5)
            )
            
            features = DocumentFeatures(
                customer_id=input_data.customer_id,
                sentiment_score=sentiment['score'],
                sentiment_positive_ratio=sentiment['positive_ratio'],
                num_monetary_amounts=monetary['count'],
                total_amount_mentioned=monetary['total'],
                num_dates_mentioned=num_dates,
                num_identifiers=num_ids,
                risk_keywords_count=risk_indicators['risk_keywords'],
                payment_delay_mentions=risk_indicators['payment_delays'],
                legal_issues_mentions=risk_indicators['legal_issues'],
                document_completeness=quality['completeness'],
                num_documents=len(input_data.document_texts),
                avg_document_length=quality['avg_length'],
                text_quality_score=quality['quality_score'],
                has_structured_data=quality['has_structured'],
                extraction_timestamp=datetime.utcnow().isoformat(),
                confidence=confidence
            )
            
            logger.info(f"✅ Features extracted for customer {input_data.customer_id}")
            return features
            
    except Exception as e:
        logger.error(f"❌ Error extracting features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Estadísticas del servicio"""
    return {
        "service": "document-feature-extractor",
        "version": "1.0.0",
        "status": "operational",
        "features_supported": [
            "sentiment_analysis",
            "monetary_extraction",
            "date_extraction",
            "identifier_extraction",
            "risk_indicators",
            "document_quality"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8009))
    logger.info(f"🚀 Starting Document Feature Extractor on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
