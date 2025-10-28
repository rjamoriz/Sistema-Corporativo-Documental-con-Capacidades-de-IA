"""
Quantum NVIDIA cuQuantum Service
Servicio de simulación cuántica acelerada por GPU
NO AFECTA AL SISTEMA ACTUAL - Servicio opcional y modular
"""
import os
import logging
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

import numpy as np
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response

# Qiskit imports
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus Metrics
simulation_requests = Counter('simulation_requests_total', 'Total simulation requests')
simulation_duration = Histogram('simulation_duration_seconds', 'Time to simulate')
circuit_qubits = Gauge('circuit_qubits', 'Number of qubits in circuit')
gpu_available_gauge = Gauge('gpu_available', 'GPU availability')

# Global simulator
simulator = None
device = "cpu"


# Pydantic Models
class CircuitRequest(BaseModel):
    """Request model for circuit simulation"""
    num_qubits: int = Field(..., ge=2, le=30, description="Number of qubits")
    depth: int = Field(default=5, ge=1, le=100, description="Circuit depth")
    shots: int = Field(default=1024, ge=1, le=10000, description="Number of shots")
    use_gpu: bool = Field(default=True, description="Use GPU if available")


class SimulationResponse(BaseModel):
    """Response model for simulation"""
    counts: Dict[str, int]
    num_qubits: int
    depth: int
    shots: int
    device_used: str
    execution_time: float


class ClassificationRequest(BaseModel):
    """Request model for quantum ML classification"""
    features: List[List[float]] = Field(..., min_items=2, max_items=100)
    labels: List[int] = Field(..., min_items=2, max_items=100)
    test_features: List[List[float]] = Field(..., min_items=1, max_items=10)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    simulator_ready: bool
    gpu_available: bool
    device: str
    max_qubits: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    global simulator, device
    
    logger.info("🚀 Starting Quantum NVIDIA cuQuantum Service...")
    
    # Check GPU availability
    if torch.cuda.is_available():
        device = "GPU"
        gpu_name = torch.cuda.get_device_name(0)
        logger.info(f"✅ GPU detected: {gpu_name}")
        gpu_available_gauge.set(1)
        
        # Try to use GPU simulator
        try:
            simulator = AerSimulator(method='statevector', device='GPU')
            logger.info("✅ Qiskit Aer GPU Simulator initialized")
        except:
            logger.warning("⚠️ GPU simulator not available, using CPU")
            simulator = AerSimulator(method='statevector')
            device = "CPU"
            gpu_available_gauge.set(0)
    else:
        device = "CPU"
        simulator = AerSimulator(method='statevector')
        gpu_available_gauge.set(0)
        logger.warning("⚠️ No GPU detected, using CPU simulator")
    
    logger.info(f"✅ Quantum NVIDIA Service ready on {device}!")
    
    yield
    
    logger.info("🛑 Shutting down Quantum NVIDIA Service...")
    if device == "GPU":
        torch.cuda.empty_cache()


# Create FastAPI app
app = FastAPI(
    title="Quantum NVIDIA cuQuantum Service",
    description="Servicio de simulación cuántica acelerada por GPU - Componente modular v2.0",
    version="2.0.0",
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


def create_random_circuit(num_qubits: int, depth: int) -> QuantumCircuit:
    """Create a random quantum circuit for testing"""
    qc = QuantumCircuit(num_qubits)
    
    for layer in range(depth):
        # Random single-qubit gates
        for qubit in range(num_qubits):
            gate_choice = np.random.randint(0, 3)
            if gate_choice == 0:
                qc.h(qubit)
            elif gate_choice == 1:
                qc.x(qubit)
            else:
                qc.rz(np.random.uniform(0, 2*np.pi), qubit)
        
        # Random entanglement
        for qubit in range(num_qubits - 1):
            if np.random.random() > 0.5:
                qc.cx(qubit, qubit + 1)
    
    qc.measure_all()
    return qc


def create_classification_circuit(features: List[float], num_qubits: int = 4) -> QuantumCircuit:
    """Create quantum circuit for classification"""
    qc = QuantumCircuit(num_qubits)
    
    # Encode features
    for i, feature in enumerate(features[:num_qubits]):
        qc.ry(feature * np.pi, i)
    
    # Entanglement layer
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    
    # Variational layer
    for i in range(num_qubits):
        qc.rz(np.random.uniform(0, 2*np.pi), i)
    
    qc.measure_all()
    return qc


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if simulator is not None else "unhealthy",
        simulator_ready=simulator is not None,
        gpu_available=torch.cuda.is_available(),
        device=device,
        max_qubits=30
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")


@app.post("/api/v1/simulate/circuit", response_model=SimulationResponse)
async def simulate_circuit(request: CircuitRequest):
    """
    Simulate a quantum circuit
    
    **Features:**
    - GPU acceleration (if available)
    - Up to 30 qubits
    - Configurable depth and shots
    """
    if simulator is None:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    simulation_requests.inc()
    
    try:
        import time
        start_time = time.time()
        
        with simulation_duration.time():
            # Create circuit
            logger.info(f"Creating circuit: {request.num_qubits} qubits, depth {request.depth}")
            qc = create_random_circuit(request.num_qubits, request.depth)
            
            circuit_qubits.set(request.num_qubits)
            
            # Transpile for simulator
            qc_transpiled = transpile(qc, simulator)
            
            # Run simulation
            logger.info(f"Running simulation on {device}")
            result = simulator.run(qc_transpiled, shots=request.shots).result()
            counts = result.get_counts()
            
            execution_time = time.time() - start_time
            
            logger.info(f"Simulation complete in {execution_time:.3f}s")
            
            return SimulationResponse(
                counts=counts,
                num_qubits=request.num_qubits,
                depth=request.depth,
                shots=request.shots,
                device_used=device,
                execution_time=execution_time
            )
    
    except Exception as e:
        logger.error(f"Error in simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ml/classify")
async def quantum_classify(request: ClassificationRequest):
    """
    Quantum Machine Learning classification
    
    **Method:**
    - Encode features in quantum states
    - Apply variational circuit
    - Measure and classify
    """
    if simulator is None:
        raise HTTPException(status_code=503, detail="Simulator not initialized")
    
    try:
        predictions = []
        
        for test_feature in request.test_features:
            # Create classification circuit
            qc = create_classification_circuit(test_feature)
            
            # Transpile and run
            qc_transpiled = transpile(qc, simulator)
            result = simulator.run(qc_transpiled, shots=1024).result()
            counts = result.get_counts()
            
            # Simple classification: most common measurement
            most_common = max(counts, key=counts.get)
            # Convert binary to class (0 or 1)
            prediction = 1 if most_common.count('1') > len(most_common) / 2 else 0
            predictions.append(prediction)
        
        return {
            "predictions": predictions,
            "num_test_samples": len(request.test_features),
            "method": "quantum_variational_classifier",
            "device": device
        }
    
    except Exception as e:
        logger.error(f"Error in quantum classification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/benchmark/compare")
async def benchmark_gpu_vs_cpu(num_qubits: int = 10, depth: int = 5, shots: int = 1024):
    """
    Benchmark GPU vs CPU performance
    
    **Use case:** Compare simulation speed
    """
    try:
        import time
        
        # Create circuit
        qc = create_random_circuit(num_qubits, depth)
        
        results = {}
        
        # CPU benchmark
        cpu_sim = AerSimulator(method='statevector')
        qc_cpu = transpile(qc, cpu_sim)
        
        start = time.time()
        cpu_sim.run(qc_cpu, shots=shots).result()
        cpu_time = time.time() - start
        results['cpu_time'] = cpu_time
        
        # GPU benchmark (if available)
        if torch.cuda.is_available():
            try:
                gpu_sim = AerSimulator(method='statevector', device='GPU')
                qc_gpu = transpile(qc, gpu_sim)
                
                start = time.time()
                gpu_sim.run(qc_gpu, shots=shots).result()
                gpu_time = time.time() - start
                results['gpu_time'] = gpu_time
                results['speedup'] = cpu_time / gpu_time
            except:
                results['gpu_time'] = None
                results['speedup'] = None
                results['gpu_error'] = "GPU simulator not available"
        else:
            results['gpu_time'] = None
            results['speedup'] = None
            results['gpu_available'] = False
        
        results['num_qubits'] = num_qubits
        results['depth'] = depth
        results['shots'] = shots
        
        return results
    
    except Exception as e:
        logger.error(f"Error in benchmark: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Quantum NVIDIA cuQuantum Service",
        "version": "2.0.0",
        "status": "running",
        "device": device,
        "gpu_available": torch.cuda.is_available(),
        "framework": "Qiskit Aer + NVIDIA cuQuantum",
        "max_qubits": 30,
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "simulate": "/api/v1/simulate/circuit",
            "classify": "/api/v1/ml/classify",
            "benchmark": "/api/v1/benchmark/compare"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=False,
        log_level="info"
    )
