"""
GraphQL Types
Defines all GraphQL types for the FinancIA document system.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import strawberry
from strawberry.types import Info


@strawberry.enum
class DocumentStatus(Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@strawberry.enum
class EntityType(Enum):
    """Entity types extracted from documents"""
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    MONEY = "MONEY"
    REGULATION = "REGULATION"
    CONTRACT = "CONTRACT"
    INVOICE = "INVOICE"
    OTHER = "OTHER"


@strawberry.enum
class AnnotationType(Enum):
    """Annotation types"""
    HIGHLIGHT = "highlight"
    STICKY_NOTE = "sticky_note"
    REDACTION = "redaction"
    COMMENT = "comment"


@strawberry.type
class User:
    """User type"""
    id: str
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = None
    created_at: datetime


@strawberry.type
class Entity:
    """Named entity extracted from document"""
    id: str
    document_id: str
    type: EntityType
    text: str
    confidence: float
    start_offset: int
    end_offset: int
    page_number: Optional[int] = None
    metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.type
class Chunk:
    """Document chunk for RAG"""
    id: str
    document_id: str
    content: str
    page_number: Optional[int] = None
    chunk_index: int
    embedding_vector: Optional[List[float]] = None
    metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.type
class Annotation:
    """Document annotation"""
    id: str
    document_id: str
    user_id: str
    type: AnnotationType
    content: Optional[str] = None
    page_number: int
    position: strawberry.scalars.JSON  # {x, y, width, height}
    color: Optional[str] = "#FFEB3B"
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    async def user(self, info: Info) -> Optional[User]:
        """Get annotation author"""
        # Use dataloader to avoid N+1 queries
        user_loader = info.context.get("user_loader")
        if user_loader:
            return await user_loader.load(self.user_id)
        return None


@strawberry.type
class ValidationResult:
    """Document validation result"""
    field: str
    rule: str
    passed: bool
    message: Optional[str] = None
    severity: str = "info"


@strawberry.type
class Document:
    """Document type with full metadata"""
    id: str
    filename: str
    mime_type: str
    size: int
    status: DocumentStatus
    uploaded_by: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
    confidence_score: Optional[float] = None
    version: int = 1
    metadata: Optional[strawberry.scalars.JSON] = None
    
    @strawberry.field
    async def entities(self, info: Info, type: Optional[EntityType] = None) -> List[Entity]:
        """Get entities extracted from document"""
        entity_service = info.context.get("entity_service")
        if entity_service:
            entities = await entity_service.get_by_document(self.id)
            if type:
                entities = [e for e in entities if e.type == type]
            return entities
        return []
    
    @strawberry.field
    async def chunks(self, info: Info, limit: Optional[int] = None) -> List[Chunk]:
        """Get document chunks for RAG"""
        chunk_service = info.context.get("chunk_service")
        if chunk_service:
            chunks = await chunk_service.get_by_document(self.id)
            if limit:
                chunks = chunks[:limit]
            return chunks
        return []
    
    @strawberry.field
    async def annotations(
        self, 
        info: Info, 
        type: Optional[AnnotationType] = None,
        page_number: Optional[int] = None
    ) -> List[Annotation]:
        """Get document annotations"""
        annotation_service = info.context.get("annotation_service")
        if annotation_service:
            annotations = await annotation_service.get_by_document(self.id)
            if type:
                annotations = [a for a in annotations if a.type == type]
            if page_number is not None:
                annotations = [a for a in annotations if a.page_number == page_number]
            return annotations
        return []
    
    @strawberry.field
    async def uploader(self, info: Info) -> Optional[User]:
        """Get user who uploaded the document"""
        user_loader = info.context.get("user_loader")
        if user_loader:
            return await user_loader.load(self.uploaded_by)
        return None
    
    @strawberry.field
    async def validation_results(self, info: Info) -> List[ValidationResult]:
        """Get validation results for document"""
        validation_service = info.context.get("validation_service")
        if validation_service:
            return await validation_service.get_results(self.id)
        return []


@strawberry.type
class PageInfo:
    """Pagination information"""
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None


@strawberry.type
class DocumentEdge:
    """Document edge for pagination"""
    cursor: str
    node: Document


@strawberry.type
class DocumentConnection:
    """Paginated document connection"""
    edges: List[DocumentEdge]
    page_info: PageInfo
    total_count: int


@strawberry.type
class SearchResult:
    """Search result with relevance score"""
    document: Document
    score: float
    highlights: List[str]
    matched_chunks: List[Chunk]


@strawberry.type
class RAGResponse:
    """Response from RAG query"""
    answer: str
    sources: List[Document]
    confidence: float
    chunks_used: List[Chunk]
    metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.type
class UploadResult:
    """Result of document upload"""
    document: Document
    success: bool
    message: Optional[str] = None


@strawberry.type
class DeleteResult:
    """Result of document deletion"""
    success: bool
    message: Optional[str] = None


@strawberry.type
class AnnotationResult:
    """Result of annotation operation"""
    annotation: Optional[Annotation] = None
    success: bool
    message: Optional[str] = None


# Input types for mutations

@strawberry.input
class DocumentFilter:
    """Filter for document queries"""
    status: Optional[DocumentStatus] = None
    mime_type: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_after: Optional[datetime] = None
    uploaded_before: Optional[datetime] = None
    min_confidence: Optional[float] = None
    search_query: Optional[str] = None


@strawberry.input
class AnnotationInput:
    """Input for creating annotation"""
    document_id: str
    type: AnnotationType
    content: Optional[str] = None
    page_number: int
    position: strawberry.scalars.JSON
    color: Optional[str] = "#FFEB3B"


@strawberry.input
class AnnotationUpdateInput:
    """Input for updating annotation"""
    content: Optional[str] = None
    position: Optional[strawberry.scalars.JSON] = None
    color: Optional[str] = None
