"""
Quantum D-Wave Deduplication Service
Servicio de deduplicación usando D-Wave Ocean SDK y Simulated Annealing
NO AFECTA AL SISTEMA ACTUAL - Servicio opcional y modular
"""
import os
import logging
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

import numpy as np
import networkx as nx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response

# D-Wave imports
import dimod
from neal import SimulatedAnnealingSampler
from dwave.preprocessing import ScaleComposite

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus Metrics
dedupe_requests = Counter('dedupe_requests_total', 'Total deduplication requests')
dedupe_duration = Histogram('dedupe_duration_seconds', 'Time to deduplicate')
qubo_size = Gauge('qubo_problem_size', 'Size of QUBO problem')
solutions_found = Counter('solutions_found_total', 'Total solutions found')

# Global sampler
sampler: Optional[SimulatedAnnealingSampler] = None


# Pydantic Models
class Document(BaseModel):
    """Document model"""
    id: str
    text: str
    metadata: Optional[Dict] = {}


class DeduplicationRequest(BaseModel):
    """Request model for deduplication"""
    documents: List[Document] = Field(..., min_items=2, max_items=1000)
    similarity_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    use_quantum: bool = Field(default=True, description="Use quantum annealing or classical")


class DeduplicationResponse(BaseModel):
    """Response model for deduplication"""
    duplicates: List[List[str]]  # Groups of duplicate document IDs
    unique_documents: List[str]
    total_documents: int
    duplicate_groups: int
    method_used: str
    energy: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    sampler_ready: bool
    method: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    global sampler
    
    logger.info("🚀 Starting Quantum D-Wave Service...")
    
    # Initialize sampler
    try:
        sampler = SimulatedAnnealingSampler()
        logger.info("✅ Simulated Annealing Sampler initialized")
        logger.info("💡 Using classical simulation (no real quantum hardware)")
    except Exception as e:
        logger.error(f"❌ Error initializing sampler: {e}")
        raise
    
    logger.info("✅ Quantum D-Wave Service ready!")
    
    yield
    
    logger.info("🛑 Shutting down Quantum D-Wave Service...")


# Create FastAPI app
app = FastAPI(
    title="Quantum D-Wave Deduplication Service",
    description="Servicio de deduplicación cuántica con D-Wave Ocean SDK - Componente modular v2.0",
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


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity (Jaccard similarity)
    En producción, usar embeddings del GPU service
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def build_similarity_graph(documents: List[Document], threshold: float) -> nx.Graph:
    """Build similarity graph from documents"""
    G = nx.Graph()
    
    # Add nodes
    for doc in documents:
        G.add_node(doc.id)
    
    # Add edges for similar documents
    for i, doc1 in enumerate(documents):
        for doc2 in documents[i+1:]:
            similarity = calculate_similarity(doc1.text, doc2.text)
            if similarity >= threshold:
                G.add_edge(doc1.id, doc2.id, weight=similarity)
    
    return G


def graph_to_qubo(G: nx.Graph) -> Dict:
    """
    Convert graph to QUBO problem
    Objetivo: Minimizar número de documentos manteniendo cobertura
    """
    nodes = list(G.nodes())
    n = len(nodes)
    
    # QUBO matrix
    Q = {}
    
    # Penalizar seleccionar ambos documentos si son similares
    for edge in G.edges():
        i, j = nodes.index(edge[0]), nodes.index(edge[1])
        weight = G[edge[0]][edge[1]]['weight']
        Q[(i, j)] = 2 * weight  # Penalización por duplicados
    
    # Recompensar seleccionar documentos únicos
    for i in range(n):
        Q[(i, i)] = -1  # Queremos minimizar, así que negativo
    
    return Q


def solve_qubo_simulated_annealing(Q: Dict, num_reads: int = 100) -> dimod.SampleSet:
    """Solve QUBO using Simulated Annealing"""
    bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
    
    # Scale for better performance
    composite = ScaleComposite(sampler)
    
    # Solve
    sampleset = composite.sample(bqm, num_reads=num_reads)
    
    return sampleset


def extract_duplicates(solution: Dict, documents: List[Document]) -> tuple:
    """Extract duplicate groups from solution"""
    doc_ids = [doc.id for doc in documents]
    
    # Documents to keep (value = 1 in solution)
    keep_docs = [doc_ids[i] for i, val in solution.items() if val == 1]
    
    # Documents to remove (value = 0 in solution)
    remove_docs = [doc_ids[i] for i, val in solution.items() if val == 0]
    
    # Group duplicates (simplified - en producción usar clustering)
    duplicate_groups = []
    if remove_docs:
        duplicate_groups.append(remove_docs)
    
    return keep_docs, duplicate_groups


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if sampler is not None else "unhealthy",
        sampler_ready=sampler is not None,
        method="Simulated Annealing (Classical)"
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")


@app.post("/api/v1/dedupe/analyze", response_model=DeduplicationResponse)
async def analyze_duplicates(request: DeduplicationRequest):
    """
    Analyze documents for duplicates using quantum-inspired optimization
    
    **Method:**
    1. Build similarity graph
    2. Formulate as QUBO problem
    3. Solve with Simulated Annealing
    4. Extract duplicate groups
    """
    if sampler is None:
        raise HTTPException(status_code=503, detail="Sampler not initialized")
    
    dedupe_requests.inc()
    
    try:
        with dedupe_duration.time():
            # Build similarity graph
            logger.info(f"Building similarity graph for {len(request.documents)} documents")
            G = build_similarity_graph(request.documents, request.similarity_threshold)
            
            if G.number_of_edges() == 0:
                # No similarities found
                return DeduplicationResponse(
                    duplicates=[],
                    unique_documents=[doc.id for doc in request.documents],
                    total_documents=len(request.documents),
                    duplicate_groups=0,
                    method_used="graph_analysis",
                    energy=0.0
                )
            
            # Convert to QUBO
            logger.info(f"Converting to QUBO (nodes={G.number_of_nodes()}, edges={G.number_of_edges()})")
            Q = graph_to_qubo(G)
            qubo_size.set(len(Q))
            
            # Solve with Simulated Annealing
            logger.info("Solving QUBO with Simulated Annealing")
            sampleset = solve_qubo_simulated_annealing(Q, num_reads=100)
            
            # Get best solution
            best_solution = sampleset.first.sample
            best_energy = sampleset.first.energy
            
            solutions_found.inc()
            
            # Extract duplicates
            unique_docs, duplicate_groups = extract_duplicates(best_solution, request.documents)
            
            logger.info(f"Found {len(duplicate_groups)} duplicate groups")
            logger.info(f"Unique documents: {len(unique_docs)}")
            
            return DeduplicationResponse(
                duplicates=duplicate_groups,
                unique_documents=unique_docs,
                total_documents=len(request.documents),
                duplicate_groups=len(duplicate_groups),
                method_used="simulated_annealing_qubo",
                energy=float(best_energy)
            )
    
    except Exception as e:
        logger.error(f"Error in deduplication: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/dedupe/optimize")
async def optimize_document_set(
    documents: List[Document],
    target_reduction: float = 0.3
):
    """
    Optimize document set to reduce duplicates by target percentage
    
    **Use case:** Reduce document collection size while maintaining coverage
    """
    if sampler is None:
        raise HTTPException(status_code=503, detail="Sampler not initialized")
    
    try:
        # Build graph
        G = build_similarity_graph(documents, threshold=0.7)
        
        # Convert to QUBO
        Q = graph_to_qubo(G)
        
        # Solve
        sampleset = solve_qubo_simulated_annealing(Q, num_reads=200)
        
        # Get solution
        solution = sampleset.first.sample
        energy = sampleset.first.energy
        
        # Extract results
        doc_ids = [doc.id for doc in documents]
        optimized_docs = [doc_ids[i] for i, val in solution.items() if val == 1]
        removed_docs = [doc_ids[i] for i, val in solution.items() if val == 0]
        
        reduction_achieved = len(removed_docs) / len(documents)
        
        return {
            "original_count": len(documents),
            "optimized_count": len(optimized_docs),
            "removed_count": len(removed_docs),
            "reduction_percentage": reduction_achieved * 100,
            "target_reduction": target_reduction * 100,
            "energy": float(energy),
            "optimized_documents": optimized_docs,
            "removed_documents": removed_docs
        }
    
    except Exception as e:
        logger.error(f"Error in optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Quantum D-Wave Deduplication Service",
        "version": "2.0.0",
        "status": "running",
        "method": "Simulated Annealing (Classical)",
        "framework": "D-Wave Ocean SDK",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "analyze": "/api/v1/dedupe/analyze",
            "optimize": "/api/v1/dedupe/optimize"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        log_level="info"
    )
