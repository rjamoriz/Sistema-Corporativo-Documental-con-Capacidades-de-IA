"""
Configuration Management
Loads settings from environment variables
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application Settings"""
    
    # Application
    APP_NAME: str = "FinancIA 2030"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:5173"]
    
    # Database (PostgreSQL)
    DATABASE_URL: str = "postgresql+asyncpg://financia:financia2030@localhost:5432/financia_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Vector Store (pgvector)
    VECTOR_DIMENSION: int = 768  # sentence-transformers mpnet dimension
    EMBEDDING_DIMENSION: int = 768  # Alias for VECTOR_DIMENSION (used by ml/embeddings.py)
    
    # OpenSearch
    OPENSEARCH_HOST: str = "localhost"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASSWORD: str = "admin"
    OPENSEARCH_INDEX: str = "documents"
    OPENSEARCH_USE_SSL: bool = False  # For local development
    OPENSEARCH_VERIFY_CERTS: bool = False  # For local development
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: List[str] = ["localhost:9092"]
    KAFKA_TOPIC_PREFIX: str = "financia"
    
    # MinIO (S3-compatible)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "documents"
    MINIO_BUCKET_NAME: str = "documents"
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Keycloak (SSO)
    KEYCLOAK_SERVER_URL: Optional[str] = None
    KEYCLOAK_REALM: Optional[str] = None
    KEYCLOAK_CLIENT_ID: Optional[str] = None
    KEYCLOAK_CLIENT_SECRET: Optional[str] = None
    
    # OpenAI API
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 2000
    
    # Anthropic API
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # LLM Configuration
    LLM_PROVIDER: str = "openai"  # openai, anthropic, local
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 2000
    
    # LLM (Local)
    LOCAL_LLM_ENABLED: bool = False
    LOCAL_LLM_MODEL: str = "llama-3-8b"
    LOCAL_LLM_ENDPOINT: Optional[str] = None
    
    # Arize Phoenix - LLM Observability
    PHOENIX_ENABLE_SERVER: bool = True
    PHOENIX_ENABLE_INSTRUMENTATION: bool = True
    PHOENIX_HOST: str = "http://localhost"
    PHOENIX_PORT: int = 6006
    PHOENIX_PROJECT_NAME: str = "financia-2030-rag"
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    EMBEDDING_BATCH_SIZE: int = 32
    
    # NER Model
    SPACY_MODEL: str = "es_core_news_lg"
    
    # Classification Model
    CLASSIFICATION_MODEL: str = "dccuchile/bert-base-spanish-wwm-cased"
    CLASSIFICATION_THRESHOLD: float = 0.8
    
    # OCR
    TESSERACT_PATH: Optional[str] = None
    TESSERACT_LANGUAGES: List[str] = ["spa", "eng", "fra", "por", "cat", "eus", "glg"]
    OCR_DPI: int = 300
    
    # Document Processing
    MAX_FILE_SIZE_MB: int = 100
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # RAG
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.5
    RAG_ENABLE_RERANKER: bool = False
    RAG_CITATION_REQUIRED: bool = True
    
    # Risk Scoring Weights
    RISK_WEIGHT_LEGAL: float = 0.25
    RISK_WEIGHT_FINANCIAL: float = 0.30
    RISK_WEIGHT_OPERATIONAL: float = 0.20
    RISK_WEIGHT_ESG: float = 0.10
    RISK_WEIGHT_PRIVACY: float = 0.10
    RISK_WEIGHT_CYBER: float = 0.05
    
    # Compliance
    COMPLIANCE_RULES_PATH: str = "config/compliance_rules.yaml"
    
    # Audit
    AUDIT_LOG_RETENTION_DAYS: int = 730  # 2 years
    AUDIT_LOG_EXPORT_ENABLED: bool = True
    
    # Observability
    PROMETHEUS_ENABLED: bool = True
    OPENTELEMETRY_ENABLED: bool = False
    OPENTELEMETRY_ENDPOINT: Optional[str] = None
    
    # MLOps
    MLFLOW_TRACKING_URI: Optional[str] = None
    MLFLOW_EXPERIMENT_NAME: str = "financia-2030"
    
    # Security
    ENABLE_MFA: bool = False
    PASSWORD_MIN_LENGTH: int = 12
    SESSION_TIMEOUT_MINUTES: int = 60
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        protected_namespaces=(),
        arbitrary_types_allowed=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
