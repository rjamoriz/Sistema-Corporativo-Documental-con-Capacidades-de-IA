"""
FinancIA 2030 - Main Application Entry Point
Sistema Corporativo Documental con Capacidades de IA
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from api.v1 import documents, search, rag, risk, compliance, auth
from core.config import settings
from core.database import engine, Base
from core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting FinancIA 2030 Backend...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Database tables created/verified")
    logger.info("✅ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down FinancIA 2030 Backend...")
    await engine.dispose()
    logger.info("✅ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="FinancIA 2030 API",
    description="""
    Sistema Corporativo Documental con Capacidades de IA
    
    ## Características
    
    * **Procesamiento Documental**: OCR, NER, clasificación automática
    * **Búsqueda Híbrida**: Léxica (BM25) + Semántica (vectores)
    * **RAG**: Asistente conversacional con citación obligatoria
    * **Análisis de Riesgo**: Scoring multidimensional con explicabilidad
    * **Compliance**: Motor de reglas y auditoría completa
    
    ## Cumplimiento Normativo
    
    * EU AI Act 2024
    * GDPR/LOPDGDD
    * NIS2 Directive
    * ISO 27001/27701/42001
    """,
    version="1.0.0",
    contact={
        "name": "FinancIA 2030 Team",
        "email": "financia2030@tefinancia.es",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://www.tefinancia.es/license",
    },
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns the health status of the application
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "FinancIA 2030 Backend"
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    
    Returns basic API information
    """
    return {
        "message": "FinancIA 2030 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk Analysis"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["Compliance"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
