"""
GPU Embedding Service
Servicio independiente para generación de embeddings acelerada por GPU
NO AFECTA AL SISTEMA ACTUAL - Servicio opcional y modular
"""
import os
import logging
from typing import List, Optional
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus Metrics
embeddings_generated = Counter('embeddings_generated_total', 'Total embeddings generated')
embedding_duration = Histogram('embedding_duration_seconds', 'Time to generate embeddings')
gpu_memory_used = Gauge('gpu_memory_used_bytes', 'GPU memory used')
active_requests = Gauge('active_requests', 'Number of active requests')

# Global variables
model: Optional[SentenceTransformer] = None
faiss_index: Optional[faiss.IndexFlatIP] = None
device: str = "cpu"


# Pydantic Models
class EmbeddingRequest(BaseModel):
    """Request model for embedding generation"""
    texts: List[str] = Field(..., description="List of texts to embed", min_items=1, max_items=1000)
    model_name: Optional[str] = Field(default="paraphrase-multilingual-mpnet-base-v2", description="Model to use")
    normalize: bool = Field(default=True, description="Normalize embeddings")


class EmbeddingResponse(BaseModel):
    """Response model for embeddings"""
    embeddings: List[List[float]]
    model_used: str
    device_used: str
    count: int
    dimensions: int


class SimilarityRequest(BaseModel):
    """Request model for similarity search"""
    query_text: str = Field(..., description="Query text")
    top_k: int = Field(default=10, description="Number of results", ge=1, le=100)
    threshold: Optional[float] = Field(default=None, description="Minimum similarity threshold", ge=0.0, le=1.0)


class SimilarityResponse(BaseModel):
    """Response model for similarity search"""
    results: List[dict]
    query: str
    count: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    gpu_available: bool
    device: str
    model_loaded: bool
    faiss_index_size: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    global model, device, faiss_index
    
    logger.info("🚀 Starting GPU Embedding Service...")
    
    # Check GPU availability
    if torch.cuda.is_available():
        device = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        logger.info(f"✅ GPU detected: {gpu_name}")
        logger.info(f"📊 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        device = "cpu"
        logger.warning("⚠️ No GPU detected, using CPU (slower)")
    
    # Load model
    try:
        model_name = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-mpnet-base-v2")
        logger.info(f"📥 Loading model: {model_name}")
        model = SentenceTransformer(model_name, device=device)
        logger.info(f"✅ Model loaded successfully on {device}")
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        raise
    
    # Initialize FAISS index
    embedding_dim = model.get_sentence_embedding_dimension()
    faiss_index = faiss.IndexFlatIP(embedding_dim)  # Inner product for cosine similarity
    logger.info(f"✅ FAISS index initialized (dim={embedding_dim})")
    
    logger.info("✅ GPU Embedding Service ready!")
    
    yield
    
    logger.info("🛑 Shutting down GPU Embedding Service...")
    if device == "cuda":
        torch.cuda.empty_cache()


# Create FastAPI app
app = FastAPI(
    title="GPU Embedding Service",
    description="Servicio de embeddings acelerado por GPU - Componente modular v2.0",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        gpu_available=torch.cuda.is_available(),
        device=device,
        model_loaded=model is not None,
        faiss_index_size=faiss_index.ntotal if faiss_index else 0
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if device == "cuda" and torch.cuda.is_available():
        gpu_memory_used.set(torch.cuda.memory_allocated(0))
    return Response(content=generate_latest(), media_type="text/plain")


@app.post("/api/v1/embeddings/generate", response_model=EmbeddingResponse)
async def generate_embeddings(request: EmbeddingRequest):
    """
    Generate embeddings for a list of texts
    
    **Features:**
    - GPU acceleration (if available)
    - Batch processing
    - Automatic normalization
    - Multiple model support
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    active_requests.inc()
    
    try:
        with embedding_duration.time():
            # Generate embeddings
            embeddings = model.encode(
                request.texts,
                convert_to_numpy=True,
                normalize_embeddings=request.normalize,
                show_progress_bar=False
            )
            
            embeddings_generated.inc(len(request.texts))
            
            # Convert to list for JSON serialization
            embeddings_list = embeddings.tolist()
            
            return EmbeddingResponse(
                embeddings=embeddings_list,
                model_used=request.model_name,
                device_used=device,
                count=len(embeddings_list),
                dimensions=len(embeddings_list[0]) if embeddings_list else 0
            )
    
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        active_requests.dec()


@app.post("/api/v1/embeddings/batch")
async def generate_embeddings_batch(
    texts: List[str],
    batch_size: int = 32,
    background_tasks: BackgroundTasks = None
):
    """
    Generate embeddings in batches (for large datasets)
    
    **Optimized for:**
    - Large document collections
    - Memory efficiency
    - GPU utilization
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = model.encode(
                batch,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            all_embeddings.extend(embeddings.tolist())
            embeddings_generated.inc(len(batch))
        
        return {
            "embeddings": all_embeddings,
            "count": len(all_embeddings),
            "batch_size": batch_size,
            "device": device
        }
    
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/similarity/search", response_model=SimilarityResponse)
async def similarity_search(request: SimilarityRequest):
    """
    Search for similar texts using FAISS
    
    **Features:**
    - Fast vector search
    - Configurable top-k
    - Similarity threshold filtering
    """
    if model is None or faiss_index is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    if faiss_index.ntotal == 0:
        raise HTTPException(status_code=400, detail="Index is empty. Add documents first.")
    
    try:
        # Generate query embedding
        query_embedding = model.encode([request.query_text], normalize_embeddings=True)
        
        # Search in FAISS
        distances, indices = faiss_index.search(query_embedding, request.top_k)
        
        # Format results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if request.threshold is None or dist >= request.threshold:
                results.append({
                    "index": int(idx),
                    "similarity": float(dist),
                    "distance": float(1 - dist)  # Convert to distance
                })
        
        return SimilarityResponse(
            results=results,
            query=request.query_text,
            count=len(results)
        )
    
    except Exception as e:
        logger.error(f"Error in similarity search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/index/add")
async def add_to_index(texts: List[str]):
    """
    Add texts to FAISS index
    
    **Use case:** Build searchable document index
    """
    if model is None or faiss_index is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Generate embeddings
        embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        
        # Add to FAISS index
        faiss_index.add(embeddings.astype('float32'))
        
        return {
            "added": len(texts),
            "total_in_index": faiss_index.ntotal,
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Error adding to index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/index/clear")
async def clear_index():
    """Clear FAISS index"""
    global faiss_index
    
    if model is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        embedding_dim = model.get_sentence_embedding_dimension()
        faiss_index = faiss.IndexFlatIP(embedding_dim)
        
        return {
            "status": "success",
            "message": "Index cleared",
            "size": 0
        }
    
    except Exception as e:
        logger.error(f"Error clearing index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "GPU Embedding Service",
        "version": "2.0.0",
        "status": "running",
        "gpu_available": torch.cuda.is_available(),
        "device": device,
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "generate": "/api/v1/embeddings/generate",
            "batch": "/api/v1/embeddings/batch",
            "search": "/api/v1/similarity/search",
            "add_to_index": "/api/v1/index/add",
            "clear_index": "/api/v1/index/clear"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
