"""
API Endpoints para Machine Learning y GPU Monitoring
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import torch

from core.auth import get_current_active_user
from models.database_models import User
from ml.embeddings import EmbeddingModel
from ml.ner_model import NERModel
from ml.classifier import ClassifierModel
from core.logging_config import logger


router = APIRouter(prefix="/ml", tags=["Machine Learning"])


# ===== Schemas =====

class GPUInfoResponse(BaseModel):
    """Información de GPU"""
    gpu_available: bool
    device: str
    default_batch_size: int
    gpu_name: Optional[str] = None
    gpu_memory_total: Optional[str] = None
    gpu_memory_allocated: Optional[str] = None
    gpu_memory_reserved: Optional[str] = None
    cuda_version: Optional[str] = None


class BenchmarkRequest(BaseModel):
    """Request para benchmark de rendimiento"""
    num_texts: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Número de textos para el benchmark"
    )


class BenchmarkResponse(BaseModel):
    """Respuesta del benchmark"""
    num_texts: int
    total_time: str
    texts_per_second: str
    device: str
    batch_size_used: int
    embedding_dimension: int
    gpu_memory_peak: Optional[str] = None


class EmbeddingRequest(BaseModel):
    """Request para generar embeddings"""
    texts: List[str] = Field(..., min_items=1, max_items=100)
    normalize: bool = Field(default=True)


class EmbeddingResponse(BaseModel):
    """Respuesta con embeddings"""
    embeddings: List[List[float]]
    dimension: int
    device_used: str
    processing_time: str


# ===== Inicializar modelos (lazy loading) =====

embedding_model = EmbeddingModel()
ner_model = NERModel()  # Asumiendo que existe
classifier_model = ClassifierModel()  # Asumiendo que existe


# ===== Endpoints =====

@router.get("/gpu-info", response_model=GPUInfoResponse)
async def get_gpu_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene información del estado de la GPU
    """
    try:
        gpu_info = embedding_model.get_gpu_info()
        return GPUInfoResponse(**gpu_info)
    except Exception as e:
        logger.error(f"Error getting GPU info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting GPU info: {str(e)}"
        )


@router.post("/benchmark", response_model=BenchmarkResponse)
async def run_benchmark(
    request: BenchmarkRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Ejecuta un benchmark de rendimiento de embeddings
    """
    try:
        logger.info(f"Running benchmark with {request.num_texts} texts for user {current_user.username}")
        
        benchmark_results = embedding_model.benchmark_performance(request.num_texts)
        
        return BenchmarkResponse(**benchmark_results)
    except Exception as e:
        logger.error(f"Error running benchmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running benchmark: {str(e)}"
        )


@router.post("/embeddings", response_model=EmbeddingResponse)
async def generate_embeddings(
    request: EmbeddingRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Genera embeddings para una lista de textos
    """
    try:
        import time
        
        start_time = time.time()
        
        # Generar embeddings
        embeddings = embedding_model.encode(
            request.texts,
            normalize=request.normalize
        )
        
        end_time = time.time()
        processing_time = f"{end_time - start_time:.2f}s"
        
        # Convertir numpy array a lista para JSON
        embeddings_list = [embedding.tolist() for embedding in embeddings]
        
        logger.info(f"Generated embeddings for {len(request.texts)} texts in {processing_time}")
        
        return EmbeddingResponse(
            embeddings=embeddings_list,
            dimension=embedding_model.dimension,
            device_used=embedding_model.device,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embeddings: {str(e)}"
        )


@router.get("/system-info")
async def get_system_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene información completa del sistema ML
    """
    try:
        system_info = {
            "gpu": embedding_model.get_gpu_info(),
            "torch": {
                "version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
                "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
            },
            "models": {
                "embedding_model": {
                    "name": embedding_model.model_name,
                    "dimension": embedding_model.dimension,
                    "loaded": embedding_model.model is not None
                }
            }
        }
        
        return system_info
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting system info: {str(e)}"
        )


@router.post("/warmup")
async def warmup_models(
    current_user: User = Depends(get_current_active_user)
):
    """
    Precarga todos los modelos ML para optimizar rendimiento
    """
    try:
        logger.info(f"Warming up ML models for user {current_user.username}")
        
        results = {}
        
        # Warmup embedding model
        try:
            embedding_model._load_model()
            results["embedding_model"] = "loaded"
        except Exception as e:
            results["embedding_model"] = f"error: {str(e)}"
        
        # TODO: Agregar warmup para otros modelos cuando estén implementados
        # ner_model._load_model()
        # classifier_model._load_model()
        
        logger.info("ML models warmup completed")
        
        return {
            "message": "Models warmup completed",
            "results": results,
            "gpu_info": embedding_model.get_gpu_info()
        }
        
    except Exception as e:
        logger.error(f"Error warming up models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error warming up models: {str(e)}"
        )
