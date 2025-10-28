"""
Quantum Machine Learning Service with PennyLane
Hybrid Quantum-Classical Neural Networks for Document Classification
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pennylane as qml
from pennylane import numpy as np
import logging
from datetime import datetime
import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from starlette.responses import Response
import json

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8007"))
N_QUBITS = int(os.getenv("N_QUBITS", "4"))
N_LAYERS = int(os.getenv("N_LAYERS", "3"))

# Prometheus metrics
qml_requests = Counter('qml_requests_total', 'Total QML requests', ['endpoint', 'status'])
qml_latency = Histogram('qml_latency_seconds', 'QML request latency', ['endpoint'])
quantum_advantage = Gauge('quantum_advantage_ratio', 'Quantum advantage vs classical')
circuit_depth = Gauge('quantum_circuit_depth', 'Current quantum circuit depth')

# FastAPI app
app = FastAPI(
    title="Quantum ML Service - PennyLane",
    description="Hybrid Quantum-Classical Machine Learning for Document Classification",
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

# Quantum device
dev = qml.device('default.qubit', wires=N_QUBITS)

# Pydantic models
class EmbeddingInput(BaseModel):
    embedding: List[float] = Field(..., description="Document embedding vector")
    document_id: Optional[str] = Field(None, description="Document ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ClassificationResult(BaseModel):
    predicted_class: int
    confidence: float
    quantum_output: List[float]
    probabilities: List[float]
    circuit_depth: int
    execution_time: float
    document_id: Optional[str] = None

class OptimizationRequest(BaseModel):
    embeddings: List[List[float]] = Field(..., description="List of embeddings to optimize")
    target_dimension: int = Field(default=4, description="Target dimension for compression")

class OptimizationResult(BaseModel):
    optimized_embeddings: List[List[float]]
    compression_ratio: float
    reconstruction_error: float
    execution_time: float

class AnomalyDetectionRequest(BaseModel):
    embeddings: List[List[float]] = Field(..., description="Embeddings to analyze")
    threshold: float = Field(default=0.8, description="Anomaly threshold")

class AnomalyResult(BaseModel):
    anomalies: List[int]
    scores: List[float]
    threshold: float
    execution_time: float

# Quantum Neural Network
@qml.qnode(dev, interface='autograd')
def quantum_neural_network(inputs, weights):
    """
    Variational Quantum Circuit for classification
    
    Args:
        inputs: Input features (normalized to [0, 2π])
        weights: Trainable parameters
    
    Returns:
        Expectation values of Pauli-Z operators
    """
    # Encode classical data into quantum state
    qml.AngleEmbedding(inputs, wires=range(N_QUBITS), rotation='Y')
    
    # Variational layers with entanglement
    qml.StronglyEntanglingLayers(weights, wires=range(N_QUBITS))
    
    # Measurement
    return [qml.expval(qml.PauliZ(i)) for i in range(N_QUBITS)]

# Quantum Autoencoder
@qml.qnode(dev, interface='autograd')
def quantum_autoencoder(inputs, encoder_weights, decoder_weights):
    """
    Quantum Autoencoder for dimensionality reduction
    
    Args:
        inputs: Input features
        encoder_weights: Encoder parameters
        decoder_weights: Decoder parameters
    
    Returns:
        Reconstructed state
    """
    # Encoding
    qml.AngleEmbedding(inputs, wires=range(N_QUBITS), rotation='Y')
    qml.StronglyEntanglingLayers(encoder_weights, wires=range(N_QUBITS))
    
    # Latent space (measure and discard some qubits)
    # Keep only first 2 qubits as compressed representation
    
    # Decoding
    qml.StronglyEntanglingLayers(decoder_weights, wires=range(N_QUBITS))
    
    return [qml.expval(qml.PauliZ(i)) for i in range(N_QUBITS)]

# Quantum k-Means helper
@qml.qnode(dev)
def quantum_distance(x1, x2, weights):
    """
    Quantum circuit to compute distance between two points
    
    Args:
        x1, x2: Two data points
        weights: Circuit parameters
    
    Returns:
        Quantum distance metric
    """
    # Encode both points
    qml.AngleEmbedding(x1, wires=range(N_QUBITS//2), rotation='Y')
    qml.AngleEmbedding(x2, wires=range(N_QUBITS//2, N_QUBITS), rotation='Y')
    
    # Entangle and measure
    qml.StronglyEntanglingLayers(weights, wires=range(N_QUBITS))
    
    return qml.expval(qml.PauliZ(0))

class QuantumClassifier:
    """Quantum Neural Network Classifier"""
    
    def __init__(self, n_qubits=N_QUBITS, n_layers=N_LAYERS):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.weights = self._init_weights()
        self.trained = False
        
        # Update circuit depth metric
        depth = n_layers * 3  # Approximate depth
        circuit_depth.set(depth)
        
    def _init_weights(self):
        """Initialize random weights for the quantum circuit"""
        shape = qml.StronglyEntanglingLayers.shape(n_layers=self.n_layers, n_wires=self.n_qubits)
        return np.random.random(shape) * 2 * np.pi
    
    def preprocess_input(self, embedding: List[float]) -> np.ndarray:
        """
        Preprocess embedding to fit quantum circuit
        
        Args:
            embedding: Input embedding vector
        
        Returns:
            Normalized array of size n_qubits
        """
        # Truncate or pad to n_qubits
        if len(embedding) > self.n_qubits:
            processed = np.array(embedding[:self.n_qubits])
        else:
            processed = np.array(embedding + [0.0] * (self.n_qubits - len(embedding)))
        
        # Normalize to [0, 2π] for angle encoding
        processed = (processed - processed.min()) / (processed.max() - processed.min() + 1e-8)
        processed = processed * 2 * np.pi
        
        return processed
    
    def classify(self, embedding: List[float]) -> Dict[str, Any]:
        """
        Classify a document using quantum neural network
        
        Args:
            embedding: Document embedding
        
        Returns:
            Classification results
        """
        start_time = datetime.now()
        
        # Preprocess input
        inputs = self.preprocess_input(embedding)
        
        # Execute quantum circuit
        quantum_output = quantum_neural_network(inputs, self.weights)
        quantum_output = np.array(quantum_output)
        
        # Convert to probabilities using softmax
        exp_output = np.exp(quantum_output - np.max(quantum_output))
        probabilities = exp_output / exp_output.sum()
        
        # Get prediction
        predicted_class = int(np.argmax(probabilities))
        confidence = float(probabilities[predicted_class])
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "quantum_output": quantum_output.tolist(),
            "probabilities": probabilities.tolist(),
            "circuit_depth": self.n_layers * 3,
            "execution_time": execution_time
        }

class QuantumAutoEncoder:
    """Quantum Autoencoder for embedding optimization"""
    
    def __init__(self, n_qubits=N_QUBITS, n_layers=N_LAYERS):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.encoder_weights = self._init_weights()
        self.decoder_weights = self._init_weights()
    
    def _init_weights(self):
        shape = qml.StronglyEntanglingLayers.shape(n_layers=self.n_layers, n_wires=self.n_qubits)
        return np.random.random(shape) * 2 * np.pi
    
    def optimize_embeddings(self, embeddings: List[List[float]]) -> Dict[str, Any]:
        """
        Optimize embeddings using quantum autoencoder
        
        Args:
            embeddings: List of embeddings to compress
        
        Returns:
            Optimized embeddings and metrics
        """
        start_time = datetime.now()
        
        optimized = []
        reconstruction_errors = []
        
        for emb in embeddings:
            # Preprocess
            if len(emb) > self.n_qubits:
                processed = np.array(emb[:self.n_qubits])
            else:
                processed = np.array(emb + [0.0] * (self.n_qubits - len(emb)))
            
            # Normalize
            processed = (processed - processed.min()) / (processed.max() - processed.min() + 1e-8)
            processed = processed * 2 * np.pi
            
            # Apply quantum autoencoder
            reconstructed = quantum_autoencoder(processed, self.encoder_weights, self.decoder_weights)
            reconstructed = np.array(reconstructed)
            
            # Calculate reconstruction error
            error = np.mean((processed - reconstructed) ** 2)
            reconstruction_errors.append(float(error))
            
            optimized.append(reconstructed.tolist())
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate compression ratio
        original_size = sum(len(e) for e in embeddings)
        compressed_size = len(optimized) * self.n_qubits
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        
        return {
            "optimized_embeddings": optimized,
            "compression_ratio": compression_ratio,
            "reconstruction_error": float(np.mean(reconstruction_errors)),
            "execution_time": execution_time
        }

class QuantumAnomalyDetector:
    """Quantum-based anomaly detection"""
    
    def __init__(self, n_qubits=N_QUBITS, n_layers=N_LAYERS):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.weights = self._init_weights()
    
    def _init_weights(self):
        shape = qml.StronglyEntanglingLayers.shape(n_layers=self.n_layers, n_wires=self.n_qubits)
        return np.random.random(shape) * 2 * np.pi
    
    def detect_anomalies(self, embeddings: List[List[float]], threshold: float) -> Dict[str, Any]:
        """
        Detect anomalies using quantum distance metrics
        
        Args:
            embeddings: List of embeddings to analyze
            threshold: Anomaly threshold
        
        Returns:
            Anomaly detection results
        """
        start_time = datetime.now()
        
        anomalies = []
        scores = []
        
        # Calculate quantum distances from mean
        mean_embedding = np.mean(embeddings, axis=0)
        
        for idx, emb in enumerate(embeddings):
            # Preprocess
            if len(emb) > self.n_qubits:
                processed = np.array(emb[:self.n_qubits])
                mean_proc = np.array(mean_embedding[:self.n_qubits])
            else:
                processed = np.array(emb + [0.0] * (self.n_qubits - len(emb)))
                mean_proc = np.array(list(mean_embedding) + [0.0] * (self.n_qubits - len(mean_embedding)))
            
            # Normalize
            processed = (processed - processed.min()) / (processed.max() - processed.min() + 1e-8) * 2 * np.pi
            mean_proc = (mean_proc - mean_proc.min()) / (mean_proc.max() - mean_proc.min() + 1e-8) * 2 * np.pi
            
            # Calculate quantum distance
            distance = quantum_distance(processed, mean_proc, self.weights)
            score = float(abs(distance))
            scores.append(score)
            
            # Check if anomaly
            if score > threshold:
                anomalies.append(idx)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "anomalies": anomalies,
            "scores": scores,
            "threshold": threshold,
            "execution_time": execution_time
        }

# Initialize models
qml_classifier = QuantumClassifier()
qml_autoencoder = QuantumAutoEncoder()
qml_anomaly_detector = QuantumAnomalyDetector()

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Quantum ML Service - PennyLane",
        "version": "1.0.0",
        "status": "operational",
        "quantum_backend": "default.qubit",
        "n_qubits": N_QUBITS,
        "n_layers": N_LAYERS,
        "endpoints": {
            "classify": "/qml/classify",
            "optimize": "/qml/optimize-embeddings",
            "anomalies": "/qml/detect-anomalies",
            "circuit": "/qml/circuit-info",
            "health": "/health",
            "metrics": "/metrics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "quantum-ml-pennylane",
        "timestamp": datetime.now().isoformat(),
        "quantum_device": str(dev),
        "n_qubits": N_QUBITS
    }

@app.post("/qml/classify", response_model=ClassificationResult)
async def classify_document(request: EmbeddingInput):
    """
    Classify document using Quantum Neural Network
    
    Args:
        request: Document embedding and metadata
    
    Returns:
        Classification results with quantum metrics
    """
    try:
        with qml_latency.labels(endpoint='classify').time():
            result = qml_classifier.classify(request.embedding)
            
            if request.document_id:
                result["document_id"] = request.document_id
            
            qml_requests.labels(endpoint='classify', status='success').inc()
            
            return ClassificationResult(**result)
    
    except Exception as e:
        qml_requests.labels(endpoint='classify', status='error').inc()
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/qml/optimize-embeddings", response_model=OptimizationResult)
async def optimize_embeddings(request: OptimizationRequest):
    """
    Optimize embeddings using Quantum Autoencoder
    
    Args:
        request: List of embeddings to optimize
    
    Returns:
        Optimized embeddings and compression metrics
    """
    try:
        with qml_latency.labels(endpoint='optimize').time():
            result = qml_autoencoder.optimize_embeddings(request.embeddings)
            
            qml_requests.labels(endpoint='optimize', status='success').inc()
            
            return OptimizationResult(**result)
    
    except Exception as e:
        qml_requests.labels(endpoint='optimize', status='error').inc()
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/qml/detect-anomalies", response_model=AnomalyResult)
async def detect_anomalies(request: AnomalyDetectionRequest):
    """
    Detect anomalies using Quantum Distance Metrics
    
    Args:
        request: Embeddings and threshold
    
    Returns:
        Anomaly detection results
    """
    try:
        with qml_latency.labels(endpoint='anomalies').time():
            result = qml_anomaly_detector.detect_anomalies(
                request.embeddings,
                request.threshold
            )
            
            qml_requests.labels(endpoint='anomalies', status='success').inc()
            
            return AnomalyResult(**result)
    
    except Exception as e:
        qml_requests.labels(endpoint='anomalies', status='error').inc()
        logger.error(f"Anomaly detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/qml/circuit-info")
async def get_circuit_info():
    """Get quantum circuit information and visualization"""
    try:
        # Get circuit drawer
        dummy_input = np.random.random(N_QUBITS) * 2 * np.pi
        dummy_weights = qml_classifier.weights
        
        # Draw circuit
        fig, ax = qml.draw_mpl(quantum_neural_network)(dummy_input, dummy_weights)
        
        return {
            "n_qubits": N_QUBITS,
            "n_layers": N_LAYERS,
            "circuit_depth": N_LAYERS * 3,
            "total_gates": N_LAYERS * N_QUBITS * 3,
            "device": str(dev),
            "backend": "default.qubit",
            "circuit_description": "Variational Quantum Circuit with StronglyEntanglingLayers"
        }
    
    except Exception as e:
        logger.error(f"Circuit info error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")

@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    return {
        "service": "quantum-ml-pennylane",
        "quantum_device": str(dev),
        "configuration": {
            "n_qubits": N_QUBITS,
            "n_layers": N_LAYERS,
            "circuit_depth": N_LAYERS * 3
        },
        "models": {
            "classifier": {
                "type": "Variational Quantum Classifier",
                "trained": qml_classifier.trained,
                "parameters": qml_classifier.weights.size
            },
            "autoencoder": {
                "type": "Quantum Autoencoder",
                "compression_target": 4
            },
            "anomaly_detector": {
                "type": "Quantum Distance-based Detector"
            }
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting Quantum ML Service on port {SERVICE_PORT}")
    logger.info(f"⚛️ Quantum Device: {dev}")
    logger.info(f"🔢 Qubits: {N_QUBITS}, Layers: {N_LAYERS}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=SERVICE_PORT,
        log_level="info"
    )
