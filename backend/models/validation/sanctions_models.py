"""
Modelos SQLAlchemy para validación de sanciones.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Text,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SanctionsList(Base):
    """
    Caché local de listas de sanciones.
    
    Se actualiza diariamente desde las APIs oficiales.
    """
    __tablename__ = "sanctions_list"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # OFAC, EU_SANCTIONS, WORLD_BANK
    entity_name = Column(String(500), nullable=False, index=True)
    entity_type = Column(String(50))  # PERSON, COMPANY, VESSEL, etc.
    list_id = Column(String(100), unique=True)  # ID en la lista original
    country = Column(String(100))
    program = Column(String(200))  # Programa de sanciones
    addresses = Column(JSON)  # Lista de direcciones
    remarks = Column(Text)
    raw_data = Column(JSON)  # Datos completos del API
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SanctionsList(source={self.source}, entity={self.entity_name})>"


class ValidationHistory(Base):
    """
    Historial de validaciones realizadas sobre documentos.
    """
    __tablename__ = "validation_history"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    entities_validated = Column(Integer, default=0)
    entities_flagged = Column(Integer, default=0)  # Entidades sancionadas encontradas
    validated_at = Column(DateTime, default=datetime.utcnow, index=True)
    validated_by = Column(String(100))  # Usuario o sistema que realizó la validación
    notes = Column(Text)

    # Relación con documento
    # document = relationship("Document", back_populates="validation_history")

    def __repr__(self):
        return f"<ValidationHistory(doc_id={self.document_id}, flagged={self.entities_flagged})>"


class ValidationResult(Base):
    """
    Resultados individuales de validación de entidades.
    """
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String(500), nullable=False, index=True)
    entity_type = Column(String(50))
    is_sanctioned = Column(Boolean, default=False, index=True)
    confidence = Column(Float)  # 0.0 a 1.0
    matches_count = Column(Integer, default=0)
    sources_checked = Column(JSON)  # Lista de fuentes consultadas
    match_details = Column(JSON)  # Detalles de los matches encontrados
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Opcional: relacionar con documento específico
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)

    def __repr__(self):
        return f"<ValidationResult(entity={self.entity_name}, sanctioned={self.is_sanctioned})>"
