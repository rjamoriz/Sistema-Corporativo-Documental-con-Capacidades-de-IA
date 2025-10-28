"""
GPU Embedding Service Client
Cliente para integrar el GPU Embedding Service con el backend actual
"""
import os
import logging
from typing import List, Optional
import httpx

logger = logging.getLogger(__name__)

# Configuración
USE_GPU_EMBEDDINGS = os.getenv("USE_GPU_EMBEDDINGS", "false").lower() == "true"
GPU_EMBEDDING_URL = os.getenv("GPU_EMBEDDING_URL", "http://localhost:8001")
GPU_TIMEOUT = int(os.getenv("GPU_EMBEDDING_TIMEOUT", "30"))


class GPUEmbeddingClient:
    """Cliente para el GPU Embedding Service"""
    
    def __init__(self):
        self.base_url = GPU_EMBEDDING_URL
        self.timeout = GPU_TIMEOUT
        self.enabled = USE_GPU_EMBEDDINGS
        
        if self.enabled:
            logger.info(f"✅ GPU Embedding Client enabled: {self.base_url}")
        else:
            logger.info("ℹ️ GPU Embedding Client disabled (using fallback)")
    
    async def is_available(self) -> bool:
        """Check if GPU service is available"""
        if not self.enabled:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"GPU service not available: {e}")
            return False
    
    async def generate_embeddings(
        self,
        texts: List[str],
        normalize: bool = True
    ) -> Optional[List[List[float]]]:
        """
        Generate embeddings using GPU service
        
        Returns:
            List of embeddings or None if service unavailable
        """
        if not self.enabled:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/embeddings/generate",
                    json={
                        "texts": texts,
                        "normalize": normalize
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ GPU embeddings generated: {len(texts)} texts")
                    return data["embeddings"]
                else:
                    logger.error(f"GPU service error: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Error calling GPU service: {e}")
            return None
    
    async def batch_embeddings(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> Optional[List[List[float]]]:
        """
        Generate embeddings in batches (for large datasets)
        """
        if not self.enabled:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/embeddings/batch",
                    json={
                        "texts": texts,
                        "batch_size": batch_size
                    },
                    timeout=self.timeout * 2  # More time for batches
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ GPU batch embeddings: {len(texts)} texts")
                    return data["embeddings"]
                else:
                    return None
        
        except Exception as e:
            logger.error(f"Error in batch embeddings: {e}")
            return None


# Singleton instance
_gpu_client: Optional[GPUEmbeddingClient] = None


def get_gpu_client() -> GPUEmbeddingClient:
    """Get GPU client singleton"""
    global _gpu_client
    if _gpu_client is None:
        _gpu_client = GPUEmbeddingClient()
    return _gpu_client
