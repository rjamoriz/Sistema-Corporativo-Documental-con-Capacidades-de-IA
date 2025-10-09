"""
Pydantic Models for API Request/Response
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from enum import Enum


# Enums
class DocumentStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class DocumentClassificationEnum(str, Enum):
    CONTRATO_PRESTAMO_PERSONAL = "contrato_prestamo_personal"
    CONTRATO_PROVEEDOR = "contrato_proveedor"
    DOCUMENTO_IDENTIDAD = "documento_identidad"
    RECIBO_FACTURA = "recibo_factura"
    POLIZA_SEGURO = "poliza_seguro"
    TRANSCRIPCION_LLAMADA = "transcripcion_llamada"
    INFORME_INTERNO = "informe_interno"
    OTRO = "otro"


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    LEGAL_REVIEWER = "legal_reviewer"
    COMPLIANCE_OFFICER = "compliance_officer"
    AGENT = "agent"
    AUDITOR = "auditor"


# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRoleEnum
    department: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=12)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    department: Optional[str] = None
    mfa_enabled: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    mfa_enabled: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: UUID
    email: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None


# Document Models
class DocumentBase(BaseModel):
    title: str = Field(..., max_length=500)
    mime_type: str
    department: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    retention_until: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    id: UUID
    file_size_bytes: int
    checksum_sha256: str
    classification: Optional[DocumentClassificationEnum] = None
    classification_confidence: Optional[float] = None
    status: DocumentStatusEnum
    owner_id: Optional[UUID] = None
    retention_until: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    message: str
    status: str


# Chunk Models
class ChunkBase(BaseModel):
    chunk_index: int
    page_num: Optional[int] = None
    text: str


class ChunkResponse(ChunkBase):
    id: UUID
    document_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Entity Models
class EntityBase(BaseModel):
    entity_type: str
    entity_value: str
    page_num: Optional[int] = None
    confidence: Optional[float] = None


class EntityResponse(EntityBase):
    id: UUID
    document_id: UUID
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Search Models
class SearchQuery(BaseModel):
    q: str = Field(..., description="Search query")
    filters: Optional[Dict[str, Any]] = None
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)
    search_type: str = Field("hybrid", pattern="^(lexical|semantic|hybrid)$")


class SearchResult(BaseModel):
    document_id: UUID
    title: str
    score: float
    snippet: str
    page_num: Optional[int] = None
    highlights: List[str] = []
    classification: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[SearchResult]
    took_ms: float


# RAG Models
class RAGQuery(BaseModel):
    question: str = Field(..., min_length=5, max_length=500)
    conversation_id: Optional[UUID] = None
    top_k: int = Field(5, ge=1, le=20)
    enable_citations: bool = True


class Citation(BaseModel):
    document_id: UUID
    document_title: str
    page_num: Optional[int] = None
    text_snippet: str
    score: float


class RAGResponse(BaseModel):
    question: str
    answer: str
    citations: List[Citation]
    confidence: float
    conversation_id: UUID
    processing_time_ms: float
    model_version: str


# Risk Assessment Models
class RiskDimensionFinding(BaseModel):
    issue: str
    severity: str = Field(..., pattern="^(low|medium|high)$")
    evidence: Dict[str, Any]
    recommendation: str


class RiskDimensionScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    weight: float
    findings: List[RiskDimensionFinding]


class RiskAssessmentResponse(BaseModel):
    document_id: UUID
    overall_score: float = Field(..., ge=0, le=100)
    legal: RiskDimensionScore
    financial: RiskDimensionScore
    operational: RiskDimensionScore
    esg: RiskDimensionScore
    privacy: RiskDimensionScore
    cyber: RiskDimensionScore
    assessed_at: datetime
    model_version: str
    
    class Config:
        from_attributes = True


# Compliance Models
class ComplianceCheckResponse(BaseModel):
    id: UUID
    document_id: UUID
    rule_id: str
    rule_description: Optional[str] = None
    status: str
    evidence: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None
    checked_at: datetime
    
    class Config:
        from_attributes = True


class ComplianceRuleExecution(BaseModel):
    document_id: UUID
    rule_ids: Optional[List[str]] = None  # None means all rules


# Audit Models
class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    user_id: Optional[UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    result: str
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class AuditLogQuery(BaseModel):
    user_id: Optional[UUID] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


# Data Subject Request Models
class DataSubjectRequestCreate(BaseModel):
    request_type: str = Field(..., pattern="^(access|rectification|erasure|portability|restriction|objection)$")
    requester_email: EmailStr
    requester_name: Optional[str] = None
    description: str


class DataSubjectRequestResponse(BaseModel):
    id: UUID
    request_type: str
    requester_email: str
    requester_name: Optional[str] = None
    status: str
    description: str
    response: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Health Check
class HealthCheck(BaseModel):
    status: str
    version: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    components: Optional[Dict[str, str]] = None


# Error Response
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
