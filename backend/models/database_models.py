"""
Database Models
SQLAlchemy ORM models for PostgreSQL
"""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, JSON, BigInteger, Date, ARRAY, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
import enum

from core.database import Base


class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class DocumentClassification(str, enum.Enum):
    """Document classification types"""
    CONTRATO_PRESTAMO_PERSONAL = "contrato_prestamo_personal"
    CONTRATO_PROVEEDOR = "contrato_proveedor"
    DOCUMENTO_IDENTIDAD = "documento_identidad"
    RECIBO_FACTURA = "recibo_factura"
    POLIZA_SEGURO = "poliza_seguro"
    TRANSCRIPCION_LLAMADA = "transcripcion_llamada"
    INFORME_INTERNO = "informe_interno"
    OTRO = "otro"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    role = Column(String(50), nullable=False)
    department = Column(String(100))
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    documents = relationship("Document", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="user")


class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    checksum_sha256 = Column(String(64), nullable=False, unique=True, index=True)
    storage_path = Column(Text, nullable=False)
    classification = Column(SQLEnum(DocumentClassification))
    classification_confidence = Column(Float)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    department = Column(String(100), index=True)
    retention_until = Column(Date)
    metadata_json = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="document", cascade="all, delete-orphan")
    compliance_checks = relationship("ComplianceCheck", back_populates="document", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Document chunks with embeddings for semantic search"""
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_num = Column(Integer)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # pgvector for semantic search
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")


class Entity(Base):
    """Extracted named entities (NER)"""
    __tablename__ = "entities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_value = Column(Text, nullable=False)
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    page_num = Column(Integer)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="entities")


class ComplianceCheck(Base):
    """Compliance rule checks"""
    __tablename__ = "compliance_checks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(String(100), nullable=False, index=True)
    rule_description = Column(Text)
    status = Column(String(20), nullable=False)  # pass, fail, warning
    evidence = Column(JSONB)
    recommendation = Column(Text)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="compliance_checks")


class RiskAssessment(Base):
    """Risk assessment scoring"""
    __tablename__ = "risk_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    legal_score = Column(Float)
    financial_score = Column(Float)
    operational_score = Column(Float)
    esg_score = Column(Float)
    privacy_score = Column(Float)
    cyber_score = Column(Float)
    findings = Column(JSONB, nullable=False)
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())
    model_version = Column(String(50))
    
    # Relationships
    document = relationship("Document", back_populates="risk_assessments")


class AuditLog(Base):
    """Audit logs (append-only, immutable)"""
    __tablename__ = "audit_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(UUID(as_uuid=True), index=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    result = Column(String(20), nullable=False)  # success, failure
    metadata_json = Column(JSONB)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class ModelRegistry(Base):
    """ML/AI Model registry (Model Cards)"""
    __tablename__ = "model_registry"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # ner, classification, embedding, llm
    training_date = Column(Date)
    dataset_version = Column(String(50))
    metrics = Column(JSONB)
    limitations = Column(Text)
    ethical_considerations = Column(Text)
    drift_status = Column(String(20))
    last_evaluated = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )


class DataSubjectRequest(Base):
    """GDPR Data Subject Requests (ARSOPL)"""
    __tablename__ = "data_subject_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_type = Column(String(50), nullable=False)  # access, rectification, erasure, etc.
    requester_email = Column(String(255), nullable=False, index=True)
    requester_name = Column(String(255))
    status = Column(String(50), default="pending")  # pending, in_progress, completed, rejected
    description = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    handled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))


class DSRType(str, enum.Enum):
    """Data Subject Request Types (GDPR/LOPDGDD)"""
    ACCESS = "access"           # Right to access
    RECTIFICATION = "rectification"  # Right to rectification
    ERASURE = "erasure"         # Right to be forgotten
    PORTABILITY = "portability"  # Right to data portability
    OBJECT = "object"           # Right to object
    RESTRICT = "restrict"       # Right to restrict processing
    LODGE = "lodge"             # Right to lodge complaint
