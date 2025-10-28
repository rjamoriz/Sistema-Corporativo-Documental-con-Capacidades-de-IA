"""
DataStax Astra DB Vector Search Service
Complete FastAPI service for vector search with Astra DB
"""
import os
import logging
import time
import uuid
from typing import List, Optional
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response

# Local imports
from models import (
    DocumentIngest, VectorSearchRequest, DocumentUpdate,
    DocumentResponse, VectorSearchResponse, SearchResult,
    DocumentListResponse, HealthResponse, StatsResponse,
    DocumentMetadata, DocumentType, EmbeddingModel
)
from astra_client import AstraVectorClient
from embedding_service import get_embedding_service
from document_processor import get_document_processor
from cache_service import get_cache_service

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus Metrics
ingest_requests = Counter('ingest_requests_total', 'Total document ingestion requests')
search_requests = Counter('search_requests_total', 'Total search requests')
ingest_duration = Histogram('ingest_duration_seconds', 'Time to ingest document')
search_duration = Histogram('search_duration_seconds', 'Time to search')
documents_count = Gauge('documents_total', 'Total documents in Astra DB')
cache_hits = Counter('cache_hits_total', 'Total cache hits')
cache_misses = Counter('cache_misses_total', 'Total cache misses')

# Global instances
astra_client: Optional[AstraVectorClient] = None
embedding_service = None
document_processor = None
cache_service = None

# Configuration
ASTRA_TOKEN = os.getenv("ASTRA_DB_TOKEN")
ASTRA_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace")
ASTRA_COLLECTION = os.getenv("ASTRA_DB_COLLECTION", "documents")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    global astra_client, embedding_service, document_processor, cache_service
    
    logger.info("🚀 Starting Astra DB Vector Search Service...")
    
    # Validate configuration
    if not ASTRA_TOKEN or not ASTRA_ENDPOINT:
        logger.error("❌ ASTRA_DB_TOKEN and ASTRA_DB_API_ENDPOINT are required!")
        raise ValueError("Missing Astra DB configuration")
    
    # Initialize Astra DB client
    try:
        astra_client = AstraVectorClient(
            token=ASTRA_TOKEN,
            api_endpoint=ASTRA_ENDPOINT,
            namespace=ASTRA_KEYSPACE,
            collection_name=ASTRA_COLLECTION
        )
        logger.info("✅ Astra DB client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Astra DB: {e}")
        raise
    
    # Initialize services
    embedding_service = get_embedding_service()
    document_processor = get_document_processor()
    cache_service = get_cache_service()
    
    logger.info("✅ All services initialized")
    logger.info("✅ Astra DB Vector Search Service ready!")
    
    yield
    
    logger.info("🛑 Shutting down Astra DB Vector Search Service...")


# Create FastAPI app
app = FastAPI(
    title="DataStax Astra DB Vector Search Service",
    description="Vector search service with DataStax Astra DB - Componente modular v2.0",
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


# ========================================
# Health & Metrics Endpoints
# ========================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check Astra DB
        astra_health = astra_client.health_check()
        doc_count = await astra_client.count_documents()
        
        # Check cache
        cache_health = cache_service.health_check()
        
        return HealthResponse(
            status="healthy" if astra_health["connected"] else "unhealthy",
            astra_connected=astra_health["connected"],
            collection_name=ASTRA_COLLECTION,
            total_documents=doc_count,
            embedding_models_available=[
                "text-embedding-ada-002",
                "text-embedding-3-small",
                "text-embedding-3-large",
                "embed-english-v3.0",
                "all-MiniLM-L6-v2"
            ]
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get service statistics"""
    try:
        doc_count = await astra_client.count_documents()
        embedding_stats = embedding_service.get_stats()
        cache_stats = cache_service.get_stats()
        
        return StatsResponse(
            total_documents=doc_count,
            total_searches=search_requests._value.get(),
            avg_search_time_ms=0.0,  # Calculate from histogram
            cache_hit_rate=cache_stats["hit_rate_percentage"],
            storage_used_mb=0.0,  # Astra DB handles this
            embedding_models_used={
                "gpu": embedding_stats["gpu_calls"],
                "openai": embedding_stats["openai_calls"],
                "cohere": embedding_stats["cohere_calls"],
                "local": embedding_stats["local_calls"]
            }
        )
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# Document Ingestion Endpoints
# ========================================

@app.post("/api/v1/documents/ingest", response_model=DocumentResponse)
async def ingest_document(request: DocumentIngest):
    """
    Ingest a document into Astra DB
    
    Process:
    1. Generate embeddings for content
    2. Optionally chunk text
    3. Store in Astra DB with metadata
    """
    ingest_requests.inc()
    
    try:
        with ingest_duration.time():
            # Generate chunks if requested
            if request.generate_chunks:
                chunks = document_processor.chunk_text(
                    request.content,
                    request.chunk_size,
                    request.chunk_overlap
                )
                logger.info(f"Created {len(chunks)} chunks")
            else:
                chunks = [request.content]
            
            # Generate embeddings
            embeddings = await embedding_service.generate_embeddings(
                chunks,
                request.embedding_model.value
            )
            
            # Store first chunk (or full document if no chunking)
            doc_id = str(uuid.uuid4())
            await astra_client.insert_document(
                document_id=doc_id,
                vector=embeddings[0],
                content=chunks[0],
                metadata=request.metadata.dict()
            )
            
            # Store additional chunks if any
            if len(chunks) > 1:
                for i, (chunk, embedding) in enumerate(zip(chunks[1:], embeddings[1:]), 1):
                    chunk_id = f"{doc_id}_chunk_{i}"
                    chunk_metadata = request.metadata.dict()
                    chunk_metadata["parent_id"] = doc_id
                    chunk_metadata["chunk_index"] = i
                    
                    await astra_client.insert_document(
                        document_id=chunk_id,
                        vector=embedding,
                        content=chunk,
                        metadata=chunk_metadata
                    )
            
            logger.info(f"✅ Document ingested: {doc_id} ({len(chunks)} chunks)")
            
            # Update count
            documents_count.set(await astra_client.count_documents())
            
            return DocumentResponse(
                id=doc_id,
                content=chunks[0],
                metadata=request.metadata,
                vector_dimension=len(embeddings[0]),
                created_at=datetime.utcnow()
            )
    
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/documents/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    tags: Optional[str] = None,
    user_id: Optional[str] = None,
    embedding_model: str = "text-embedding-ada-002"
):
    """
    Ingest a document file (PDF, DOCX, TXT)
    
    Extracts text and ingests into Astra DB
    """
    ingest_requests.inc()
    
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract text based on file type
        filename_lower = file.filename.lower()
        if filename_lower.endswith('.pdf'):
            text = document_processor.extract_text_from_pdf(temp_path)
            doc_type = DocumentType.PDF
        elif filename_lower.endswith('.docx'):
            text = document_processor.extract_text_from_docx(temp_path)
            doc_type = DocumentType.DOCX
        elif filename_lower.endswith('.txt'):
            text = document_processor.extract_text_from_txt(temp_path)
            doc_type = DocumentType.TXT
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Create metadata
        metadata = DocumentMetadata(
            filename=file.filename,
            document_type=doc_type,
            upload_date=datetime.utcnow(),
            user_id=user_id,
            tags=tags.split(",") if tags else [],
            custom_fields={}
        )
        
        # Create ingest request
        ingest_req = DocumentIngest(
            content=text,
            metadata=metadata,
            embedding_model=EmbeddingModel(embedding_model),
            generate_chunks=True
        )
        
        # Ingest
        result = await ingest_document(ingest_req)
        
        # Clean up
        import os as os_module
        os_module.remove(temp_path)
        
        return result
    
    except Exception as e:
        logger.error(f"File ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# Vector Search Endpoints
# ========================================

@app.post("/api/v1/search/semantic", response_model=VectorSearchResponse)
async def semantic_search(request: VectorSearchRequest):
    """
    Perform semantic vector search
    
    Process:
    1. Check cache
    2. Generate query embedding
    3. Search in Astra DB using HNSW
    4. Return ranked results
    5. Cache results
    """
    search_requests.inc()
    
    try:
        start_time = time.time()
        
        with search_duration.time():
            # Check cache
            cached_results = await cache_service.get(
                request.query,
                request.metadata_filter
            )
            
            if cached_results:
                cache_hits.inc()
                search_time = (time.time() - start_time) * 1000
                
                return VectorSearchResponse(
                    query=request.query,
                    results=[SearchResult(**r) for r in cached_results],
                    total_results=len(cached_results),
                    search_time_ms=search_time,
                    embedding_model=request.embedding_model.value
                )
            
            cache_misses.inc()
            
            # Generate query embedding
            query_embeddings = await embedding_service.generate_embeddings(
                [request.query],
                request.embedding_model.value
            )
            query_vector = query_embeddings[0]
            
            # Search in Astra DB
            results = await astra_client.vector_search(
                query_vector=query_vector,
                top_k=request.top_k,
                metadata_filter=request.metadata_filter
            )
            
            # Filter by min_score
            filtered_results = [
                r for r in results
                if r["similarity_score"] >= request.min_score
            ]
            
            # Convert to response format
            search_results = [
                SearchResult(
                    id=r["id"],
                    content=r["content"],
                    metadata=DocumentMetadata(**r["metadata"]),
                    similarity_score=r["similarity_score"],
                    rank=r["rank"]
                )
                for r in filtered_results
            ]
            
            search_time = (time.time() - start_time) * 1000
            
            # Cache results
            await cache_service.set(
                request.query,
                [r.dict() for r in search_results],
                request.metadata_filter
            )
            
            logger.info(f"✅ Search completed: {len(search_results)} results in {search_time:.2f}ms")
            
            return VectorSearchResponse(
                query=request.query,
                results=search_results,
                total_results=len(search_results),
                search_time_ms=search_time,
                embedding_model=request.embedding_model.value
            )
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# CRUD Endpoints
# ========================================

@app.get("/api/v1/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document by ID"""
    try:
        doc = await astra_client.get_document(document_id)
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            id=doc["_id"],
            content=doc["content"],
            metadata=DocumentMetadata(**doc["metadata"]),
            vector_dimension=len(doc.get("$vector", [])),
            created_at=datetime.fromisoformat(doc["created_at"]),
            updated_at=datetime.fromisoformat(doc["updated_at"]) if doc.get("updated_at") else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/documents", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    document_type: Optional[str] = None
):
    """List documents with pagination"""
    try:
        # Build filter
        metadata_filter = {}
        if document_type:
            metadata_filter["metadata.document_type"] = document_type
        
        # Get documents
        docs, total = await astra_client.list_documents(
            skip=skip,
            limit=limit,
            metadata_filter=metadata_filter if metadata_filter else None
        )
        
        # Convert to response format
        doc_responses = [
            DocumentResponse(
                id=doc["_id"],
                content=doc["content"],
                metadata=DocumentMetadata(**doc["metadata"]),
                vector_dimension=len(doc.get("$vector", [])),
                created_at=datetime.fromisoformat(doc["created_at"]),
                updated_at=datetime.fromisoformat(doc["updated_at"]) if doc.get("updated_at") else None
            )
            for doc in docs
        ]
        
        return DocumentListResponse(
            documents=doc_responses,
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            has_more=(skip + limit) < total
        )
    
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/documents/{document_id}")
async def update_document(document_id: str, update: DocumentUpdate):
    """Update document"""
    try:
        updates = {}
        
        if update.content:
            updates["content"] = update.content
            
            # Regenerate embedding if requested
            if update.regenerate_embedding:
                embeddings = await embedding_service.generate_embeddings(
                    [update.content],
                    "text-embedding-ada-002"
                )
                updates["$vector"] = embeddings[0]
        
        if update.metadata:
            updates["metadata"] = update.metadata.dict()
        
        success = await astra_client.update_document(document_id, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Invalidate cache
        await cache_service.invalidate()
        
        return {"message": "Document updated successfully", "id": document_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete document"""
    try:
        success = await astra_client.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update count
        documents_count.set(await astra_client.count_documents())
        
        # Invalidate cache
        await cache_service.invalidate()
        
        return {"message": "Document deleted successfully", "id": document_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# Root Endpoint
# ========================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "DataStax Astra DB Vector Search Service",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Vector similarity search (HNSW)",
            "Document ingestion (PDF, DOCX, TXT)",
            "GPU-accelerated embeddings",
            "Redis caching",
            "Metadata filtering",
            "CRUD operations"
        ],
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "stats": "/stats",
            "docs": "/docs",
            "ingest": "/api/v1/documents/ingest",
            "ingest_file": "/api/v1/documents/ingest/file",
            "search": "/api/v1/search/semantic",
            "list": "/api/v1/documents",
            "get": "/api/v1/documents/{id}",
            "update": "/api/v1/documents/{id}",
            "delete": "/api/v1/documents/{id}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8006,
        reload=False,
        log_level="info"
    )
