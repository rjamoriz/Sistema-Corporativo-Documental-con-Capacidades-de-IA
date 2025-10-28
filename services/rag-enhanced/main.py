"""
RAG Enhanced Service
Servicio RAG optimizado con GPU embeddings y LLMs
NO AFECTA AL SISTEMA ACTUAL - Servicio opcional y modular
"""
import os
import logging
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus Metrics
rag_requests = Counter('rag_requests_total', 'Total RAG requests')
rag_duration = Histogram('rag_duration_seconds', 'Time to generate response')
context_size = Gauge('context_size_tokens', 'Size of context in tokens')
llm_calls = Counter('llm_calls_total', 'Total LLM API calls')

# Global configuration
GPU_EMBEDDING_URL = os.getenv("GPU_EMBEDDING_URL", "http://gpu-embedding-service:8001")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


# Pydantic Models
class Document(BaseModel):
    """Document model"""
    id: str
    text: str
    metadata: Optional[Dict] = {}


class RAGRequest(BaseModel):
    """Request model for RAG"""
    query: str = Field(..., min_length=1, max_length=1000)
    documents: List[Document] = Field(..., min_items=1, max_items=100)
    top_k: int = Field(default=5, ge=1, le=20)
    llm_provider: str = Field(default="openai", description="openai or anthropic")
    model: str = Field(default="gpt-4", description="Model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class RAGResponse(BaseModel):
    """Response model for RAG"""
    answer: str
    sources: List[Dict]
    context_used: List[str]
    num_sources: int
    model_used: str
    tokens_used: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    gpu_embedding_available: bool
    openai_configured: bool
    anthropic_configured: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    logger.info("🚀 Starting RAG Enhanced Service...")
    
    # Check GPU embedding service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GPU_EMBEDDING_URL}/health", timeout=5.0)
            if response.status_code == 200:
                logger.info("✅ GPU Embedding Service connected")
            else:
                logger.warning("⚠️ GPU Embedding Service not responding")
    except:
        logger.warning("⚠️ GPU Embedding Service not available")
    
    # Check API keys
    if OPENAI_API_KEY:
        logger.info("✅ OpenAI API key configured")
    else:
        logger.warning("⚠️ OpenAI API key not configured")
    
    if ANTHROPIC_API_KEY:
        logger.info("✅ Anthropic API key configured")
    else:
        logger.warning("⚠️ Anthropic API key not configured")
    
    logger.info("✅ RAG Enhanced Service ready!")
    
    yield
    
    logger.info("🛑 Shutting down RAG Enhanced Service...")


# Create FastAPI app
app = FastAPI(
    title="RAG Enhanced Service",
    description="Servicio RAG optimizado con GPU embeddings y LLMs - Componente modular v2.0",
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


async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings from GPU service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GPU_EMBEDDING_URL}/api/v1/embeddings/generate",
                json={"texts": texts, "normalize": True},
                timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
                return data["embeddings"]
            else:
                raise Exception(f"GPU service error: {response.status_code}")
    except Exception as e:
        logger.error(f"Error getting embeddings: {e}")
        raise


def calculate_similarity(emb1: List[float], emb2: List[float]) -> float:
    """Calculate cosine similarity"""
    import numpy as np
    a = np.array(emb1)
    b = np.array(emb2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


async def retrieve_relevant_docs(query: str, documents: List[Document], top_k: int) -> List[tuple]:
    """Retrieve most relevant documents"""
    # Get embeddings
    all_texts = [query] + [doc.text for doc in documents]
    embeddings = await get_embeddings(all_texts)
    
    query_emb = embeddings[0]
    doc_embs = embeddings[1:]
    
    # Calculate similarities
    similarities = []
    for i, doc_emb in enumerate(doc_embs):
        sim = calculate_similarity(query_emb, doc_emb)
        similarities.append((i, sim, documents[i]))
    
    # Sort and get top-k
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]


async def call_openai(prompt: str, model: str, temperature: float) -> tuple:
    """Call OpenAI API"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        llm_calls.inc()
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un asistente experto que responde preguntas basándose en documentos proporcionados. Siempre cita las fuentes."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        answer = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else None
        
        return answer, tokens
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise


async def call_anthropic(prompt: str, model: str, temperature: float) -> tuple:
    """Call Anthropic API"""
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        
        llm_calls.inc()
        
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        answer = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens if response.usage else None
        
        return answer, tokens
    except Exception as e:
        logger.error(f"Anthropic API error: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Check GPU embedding service
    gpu_available = False
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GPU_EMBEDDING_URL}/health", timeout=5.0)
            gpu_available = response.status_code == 200
    except:
        pass
    
    return HealthResponse(
        status="healthy",
        gpu_embedding_available=gpu_available,
        openai_configured=bool(OPENAI_API_KEY),
        anthropic_configured=bool(ANTHROPIC_API_KEY)
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")


@app.post("/api/v1/rag/query", response_model=RAGResponse)
async def rag_query(request: RAGRequest):
    """
    RAG query with GPU embeddings and LLM
    
    **Features:**
    - GPU-accelerated embeddings
    - Semantic search
    - LLM generation (OpenAI/Anthropic)
    - Source citation
    - 100% trazabilidad
    """
    rag_requests.inc()
    
    try:
        with rag_duration.time():
            # Retrieve relevant documents
            logger.info(f"Retrieving top-{request.top_k} documents for query")
            relevant_docs = await retrieve_relevant_docs(
                request.query,
                request.documents,
                request.top_k
            )
            
            # Build context
            context_parts = []
            sources = []
            for idx, similarity, doc in relevant_docs:
                context_parts.append(f"[Documento {idx+1}]: {doc.text}")
                sources.append({
                    "document_id": doc.id,
                    "similarity": float(similarity),
                    "text_preview": doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
                    "metadata": doc.metadata
                })
            
            context = "\n\n".join(context_parts)
            context_size.set(len(context))
            
            # Build prompt
            prompt = f"""Basándote ÚNICAMENTE en los siguientes documentos, responde la pregunta del usuario.
Si la información no está en los documentos, di que no tienes suficiente información.
SIEMPRE cita qué documento(s) usaste para tu respuesta.

DOCUMENTOS:
{context}

PREGUNTA: {request.query}

RESPUESTA (con citas):"""
            
            # Call LLM
            logger.info(f"Calling {request.llm_provider} LLM")
            if request.llm_provider == "openai":
                if not OPENAI_API_KEY:
                    raise HTTPException(status_code=400, detail="OpenAI API key not configured")
                answer, tokens = await call_openai(prompt, request.model, request.temperature)
            elif request.llm_provider == "anthropic":
                if not ANTHROPIC_API_KEY:
                    raise HTTPException(status_code=400, detail="Anthropic API key not configured")
                answer, tokens = await call_anthropic(prompt, request.model, request.temperature)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown LLM provider: {request.llm_provider}")
            
            logger.info("RAG query completed successfully")
            
            return RAGResponse(
                answer=answer,
                sources=sources,
                context_used=[doc.text for _, _, doc in relevant_docs],
                num_sources=len(sources),
                model_used=f"{request.llm_provider}/{request.model}",
                tokens_used=tokens
            )
    
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/rag/simple")
async def simple_rag(query: str, context: str, llm_provider: str = "openai"):
    """
    Simple RAG without document retrieval
    
    **Use case:** When you already have the context
    """
    try:
        prompt = f"""Contexto: {context}

Pregunta: {query}

Respuesta:"""
        
        if llm_provider == "openai":
            answer, tokens = await call_openai(prompt, "gpt-3.5-turbo", 0.7)
        else:
            answer, tokens = await call_anthropic(prompt, "claude-3-haiku-20240307", 0.7)
        
        return {
            "answer": answer,
            "tokens_used": tokens,
            "model_used": llm_provider
        }
    
    except Exception as e:
        logger.error(f"Error in simple RAG: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "RAG Enhanced Service",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "GPU-accelerated embeddings",
            "Semantic search",
            "Multiple LLM providers",
            "Source citation",
            "100% trazabilidad"
        ],
        "llm_providers": ["openai", "anthropic"],
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "rag_query": "/api/v1/rag/query",
            "simple_rag": "/api/v1/rag/simple"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=False,
        log_level="info"
    )
