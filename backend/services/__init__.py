"""
Servicios de Backend - FinancIA 2030

Importing the real ML/AI services now that dependencies are fixed
"""

try:
    from services.ingest_service import ingest_service
    from services.transform_service import transform_service
    from services.extract_service import extract_service
    from services.classification_service import classification_service
    from services.search_service import search_service
    from services.rag_service import rag_service
    from services.risk_service import risk_service
    from services.compliance_service import compliance_service
    print("✅ All ML/AI services loaded successfully!")
except ImportError as e:
    print(f"⚠️ Some services failed to load: {e}")
    # Fallback to lightweight services
    class LightweightService:
        """Lightweight service placeholder"""
        def __init__(self, name):
            self.name = name

    ingest_service = LightweightService("ingest")
    transform_service = LightweightService("transform")
    extract_service = LightweightService("extract")
    classification_service = LightweightService("classification")
    search_service = LightweightService("search")
    rag_service = LightweightService("rag")
    risk_service = LightweightService("risk")
    compliance_service = LightweightService("compliance")

__all__ = [
    "ingest_service",
    "transform_service",
    "extract_service",
    "classification_service",
    "search_service",
    "rag_service",
    "risk_service",
    "compliance_service",
]
