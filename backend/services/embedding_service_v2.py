"""
Embedding Service v2.0
Integra GPU Embedding Service con fallback al método actual
"""
import logging
from typing import List
from .gpu_embedding_client import get_gpu_client

logger = logging.getLogger(__name__)


class EmbeddingServiceV2:
    """
    Servicio de embeddings con soporte GPU y fallback
    
    Estrategia:
    1. Intenta usar GPU service si está habilitado
    2. Si falla o no está disponible, usa método actual
    3. Log de qué método se usó para métricas
    """
    
    def __init__(self, fallback_service):
        """
        Args:
            fallback_service: Tu servicio de embeddings actual
        """
        self.gpu_client = get_gpu_client()
        self.fallback_service = fallback_service
        self.stats = {
            "gpu_calls": 0,
            "fallback_calls": 0,
            "gpu_errors": 0
        }
    
    async def generate_embeddings(
        self,
        texts: List[str],
        normalize: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings with GPU acceleration and fallback
        
        Returns:
            List of embeddings (always returns, never fails)
        """
        # Try GPU service first
        if self.gpu_client.enabled:
            try:
                embeddings = await self.gpu_client.generate_embeddings(
                    texts=texts,
                    normalize=normalize
                )
                
                if embeddings is not None:
                    self.stats["gpu_calls"] += 1
                    logger.info(f"✅ Used GPU service for {len(texts)} embeddings")
                    return embeddings
                else:
                    self.stats["gpu_errors"] += 1
                    logger.warning("⚠️ GPU service returned None, using fallback")
            
            except Exception as e:
                self.stats["gpu_errors"] += 1
                logger.error(f"❌ GPU service error: {e}, using fallback")
        
        # Fallback to current method
        self.stats["fallback_calls"] += 1
        logger.info(f"ℹ️ Using fallback method for {len(texts)} embeddings")
        return await self.fallback_service.generate_embeddings(texts, normalize)
    
    async def batch_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[List[float]]:
        """
        Generate embeddings in batches
        """
        # Try GPU batch service
        if self.gpu_client.enabled:
            try:
                embeddings = await self.gpu_client.batch_embeddings(
                    texts=texts,
                    batch_size=batch_size
                )
                
                if embeddings is not None:
                    self.stats["gpu_calls"] += 1
                    logger.info(f"✅ Used GPU batch for {len(texts)} embeddings")
                    return embeddings
            
            except Exception as e:
                self.stats["gpu_errors"] += 1
                logger.error(f"❌ GPU batch error: {e}, using fallback")
        
        # Fallback
        self.stats["fallback_calls"] += 1
        return await self.fallback_service.batch_embeddings(texts, batch_size)
    
    def get_stats(self) -> dict:
        """Get usage statistics"""
        total = self.stats["gpu_calls"] + self.stats["fallback_calls"]
        gpu_percentage = (self.stats["gpu_calls"] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            "total_calls": total,
            "gpu_percentage": round(gpu_percentage, 2),
            "gpu_enabled": self.gpu_client.enabled
        }


# Example usage in your existing code:
"""
# En tu backend/main.py o donde inicialices servicios:

from services.embedding_service_v2 import EmbeddingServiceV2
from services.your_current_embedding_service import YourCurrentEmbeddingService

# Tu servicio actual
current_embedding_service = YourCurrentEmbeddingService()

# Nuevo servicio con GPU + fallback
embedding_service = EmbeddingServiceV2(
    fallback_service=current_embedding_service
)

# Usar igual que antes
embeddings = await embedding_service.generate_embeddings(["texto 1", "texto 2"])

# Ver estadísticas
stats = embedding_service.get_stats()
print(f"GPU usage: {stats['gpu_percentage']}%")
"""
