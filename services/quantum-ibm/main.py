"""
Quantum IBM Qiskit Service
Servicio de optimización cuántica usando IBM Qiskit con QAOA
NO AFECTA AL SISTEMA ACTUAL - Servicio opcional y modular
"""
import os
import logging
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response

# Qiskit imports
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit.primitives import Sampler

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus Metrics
optimization_requests = Counter('optimization_requests_total', 'Total optimization requests')
optimization_duration = Histogram('optimization_duration_seconds', 'Time to optimize')
circuit_depth = Gauge('circuit_depth', 'Quantum circuit depth')
qubits_used = Gauge('qubits_used', 'Number of qubits used')

# Global backend
backend = None


# Pydantic Models
class Document(BaseModel):
    """Document model"""
    id: str
    text: str
    similarity_score: Optional[float] = 0.0


class OptimizationRequest(BaseModel):
    """Request model for optimization"""
    documents: List[Document] = Field(..., min_items=2, max_items=100)
    max_iterations: int = Field(default=100, ge=10, le=1000)
    use_simulator: bool = Field(default=True)


class OptimizationResponse(BaseModel):
    """Response model for optimization"""
    selected_documents: List[str]
    removed_documents: List[str]
    total_documents: int
    reduction_percentage: float
    optimal_value: float
    iterations: int
    method_used: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    backend_ready: bool
    backend_name: str
    max_qubits: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    global backend
    
    logger.info("🚀 Starting Quantum IBM Qiskit Service...")
    
    # Initialize backend
    try:
        backend = Aer.get_backend('qasm_simulator')
        logger.info(f"✅ Qiskit Aer Simulator initialized")
        logger.info(f"📊 Max qubits: {backend.configuration().n_qubits}")
        logger.info("💡 Using local simulator (no IBM Quantum hardware)")
    except Exception as e:
        logger.error(f"❌ Error initializing backend: {e}")
        raise
    
    logger.info("✅ Quantum IBM Qiskit Service ready!")
    
    yield
    
    logger.info("🛑 Shutting down Quantum IBM Qiskit Service...")


# Create FastAPI app
app = FastAPI(
    title="Quantum IBM Qiskit Service",
    description="Servicio de optimización cuántica con IBM Qiskit y QAOA - Componente modular v2.0",
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


def create_optimization_problem(documents: List[Document]) -> QuadraticProgram:
    """
    Create QUBO optimization problem
    Objetivo: Minimizar documentos manteniendo diversidad
    """
    n = len(documents)
    qp = QuadraticProgram()
    
    # Variables binarias (seleccionar o no cada documento)
    for i, doc in enumerate(documents):
        qp.binary_var(f'x{i}')
    
    # Función objetivo: minimizar número de documentos
    linear = {f'x{i}': -1 for i in range(n)}
    
    # Penalización por documentos similares seleccionados juntos
    quadratic = {}
    for i in range(n):
        for j in range(i+1, n):
            # Si los documentos son similares, penalizar seleccionarlos juntos
            sim = documents[i].similarity_score if hasattr(documents[i], 'similarity_score') else 0.5
            quadratic[(f'x{i}', f'x{j}')] = 2 * sim
    
    qp.minimize(linear=linear, quadratic=quadratic)
    
    # Constraint: al menos mantener 50% de documentos
    constraint_linear = {f'x{i}': 1 for i in range(n)}
    qp.linear_constraint(constraint_linear, '>=', n // 2, name='min_docs')
    
    return qp


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    max_qubits = backend.configuration().n_qubits if backend else 0
    return HealthResponse(
        status="healthy" if backend is not None else "unhealthy",
        backend_ready=backend is not None,
        backend_name="qasm_simulator" if backend else "none",
        max_qubits=max_qubits
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")


@app.post("/api/v1/optimize/qaoa", response_model=OptimizationResponse)
async def optimize_with_qaoa(request: OptimizationRequest):
    """
    Optimize document selection using QAOA (Quantum Approximate Optimization Algorithm)
    
    **Method:**
    1. Formulate as QUBO problem
    2. Solve with QAOA
    3. Extract optimal solution
    """
    if backend is None:
        raise HTTPException(status_code=503, detail="Backend not initialized")
    
    optimization_requests.inc()
    
    try:
        with optimization_duration.time():
            # Create optimization problem
            logger.info(f"Creating QUBO for {len(request.documents)} documents")
            qp = create_optimization_problem(request.documents)
            
            # Set up QAOA
            logger.info("Setting up QAOA algorithm")
            optimizer = COBYLA(maxiter=request.max_iterations)
            qaoa = QAOA(sampler=Sampler(), optimizer=optimizer, reps=2)
            
            # Solve
            logger.info("Solving with QAOA...")
            algorithm = MinimumEigenOptimizer(qaoa)
            result = algorithm.solve(qp)
            
            # Update metrics
            qubits_used.set(len(request.documents))
            
            # Extract solution
            solution = result.x
            selected_indices = [i for i, val in enumerate(solution) if val > 0.5]
            removed_indices = [i for i, val in enumerate(solution) if val <= 0.5]
            
            selected_docs = [request.documents[i].id for i in selected_indices]
            removed_docs = [request.documents[i].id for i in removed_indices]
            
            reduction = len(removed_docs) / len(request.documents) * 100
            
            logger.info(f"Optimization complete: {len(selected_docs)} selected, {len(removed_docs)} removed")
            
            return OptimizationResponse(
                selected_documents=selected_docs,
                removed_documents=removed_docs,
                total_documents=len(request.documents),
                reduction_percentage=reduction,
                optimal_value=float(result.fval),
                iterations=request.max_iterations,
                method_used="QAOA"
            )
    
    except Exception as e:
        logger.error(f"Error in QAOA optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/optimize/classical")
async def optimize_classical(documents: List[Document]):
    """
    Classical optimization baseline for comparison
    Simple greedy algorithm
    """
    try:
        # Sort by similarity score
        sorted_docs = sorted(documents, key=lambda x: x.similarity_score, reverse=True)
        
        # Keep top 70%
        keep_count = int(len(documents) * 0.7)
        selected = sorted_docs[:keep_count]
        removed = sorted_docs[keep_count:]
        
        return {
            "selected_documents": [doc.id for doc in selected],
            "removed_documents": [doc.id for doc in removed],
            "total_documents": len(documents),
            "reduction_percentage": (len(removed) / len(documents)) * 100,
            "method_used": "classical_greedy"
        }
    
    except Exception as e:
        logger.error(f"Error in classical optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/circuit/create")
async def create_quantum_circuit(num_qubits: int = 3, depth: int = 2):
    """
    Create and visualize a quantum circuit
    
    **Educational endpoint** - Shows quantum circuit structure
    """
    try:
        # Create circuit
        qc = QuantumCircuit(num_qubits)
        
        # Add layers
        for layer in range(depth):
            # Hadamard gates
            for qubit in range(num_qubits):
                qc.h(qubit)
            
            # Entanglement
            for qubit in range(num_qubits - 1):
                qc.cx(qubit, qubit + 1)
            
            # Rotation
            for qubit in range(num_qubits):
                qc.rz(np.pi / 4, qubit)
        
        # Measurement
        qc.measure_all()
        
        circuit_depth.set(qc.depth())
        
        return {
            "num_qubits": num_qubits,
            "depth": qc.depth(),
            "num_gates": len(qc.data),
            "circuit_diagram": str(qc.draw(output='text')),
            "operations": [op.operation.name for op in qc.data]
        }
    
    except Exception as e:
        logger.error(f"Error creating circuit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Quantum IBM Qiskit Service",
        "version": "2.0.0",
        "status": "running",
        "backend": "qasm_simulator",
        "framework": "IBM Qiskit",
        "algorithms": ["QAOA", "VQE", "Grover"],
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "optimize_qaoa": "/api/v1/optimize/qaoa",
            "optimize_classical": "/api/v1/optimize/classical",
            "create_circuit": "/api/v1/circuit/create"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=False,
        log_level="info"
    )
