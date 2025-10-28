"""
Data Models for Astra DB Vector Search Service
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class DocumentType(str, Enum):
    """Document types"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    JSON = "json"
    OTHER = "other"


class EmbeddingModel(str, Enum):
    """Supported embedding models"""
    OPENAI_ADA = "text-embedding-ada-002"
    OPENAI_3_SMALL = "text-embedding-3-small"
    OPENAI_3_LARGE = "text-embedding-3-large"
    COHERE_EMBED = "embed-english-v3.0"
    SENTENCE_BERT = "all-MiniLM-L6-v2"


# ========================================
# Request Models
# ========================================

class DocumentMetadata(BaseModel):
    """Document metadata"""
    filename: str
    document_type: DocumentType
    upload_date: Optional[datetime] = None
    user_id: Optional[str] = None
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}


class DocumentIngest(BaseModel):
    """Document ingestion request"""
    content: str = Field(..., description="Document text content")
    metadata: DocumentMetadata
    embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_ADA
    generate_chunks: bool = Field(default=True, description="Split into chunks")
    chunk_size: int = Field(default=500, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)


class VectorSearchRequest(BaseModel):
    """Vector search request"""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=100)
    embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_ADA
    metadata_filter: Optional[Dict[str, Any]] = None
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)


class DocumentUpdate(BaseModel):
    """Document update request"""
    content: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    regenerate_embedding: bool = False


class MetadataFilter(BaseModel):
    """Metadata filtering"""
    tags: Optional[List[str]] = None
    document_type: Optional[DocumentType] = None
    user_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    custom_filters: Optional[Dict[str, Any]] = None


# ========================================
# Response Models
# ========================================

class DocumentResponse(BaseModel):
    """Document response"""
    id: str
    content: str
    metadata: DocumentMetadata
    vector_dimension: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class SearchResult(BaseModel):
    """Single search result"""
    id: str
    content: str
    metadata: DocumentMetadata
    similarity_score: float
    rank: int


class VectorSearchResponse(BaseModel):
    """Vector search response"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    embedding_model: str


class DocumentListResponse(BaseModel):
    """Paginated document list"""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    astra_connected: bool
    collection_name: str
    total_documents: int
    embedding_models_available: List[str]


class StatsResponse(BaseModel):
    """Service statistics"""
    total_documents: int
    total_searches: int
    avg_search_time_ms: float
    cache_hit_rate: float
    storage_used_mb: float
    embedding_models_used: Dict[str, int]


# ========================================
# Internal Models
# ========================================

class VectorDocument(BaseModel):
    """Internal vector document structure"""
    id: str
    vector: List[float]
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None


class CachedQuery(BaseModel):
    """Cached search query"""
    query_hash: str
    results: List[SearchResult]
    timestamp: datetime
    ttl_seconds: int = 3600
