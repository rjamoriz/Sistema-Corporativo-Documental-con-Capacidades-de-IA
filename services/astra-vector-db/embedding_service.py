"""
Embedding Service
Integrates with GPU Embedding Service and provides fallback options
"""
import os
import logging
from typing import List, Optional
import httpx
import numpy as np

logger = logging.getLogger(__name__)

# Configuration
GPU_EMBEDDING_URL = os.getenv("GPU_EMBEDDING_URL", "http://localhost:8001")
USE_GPU_SERVICE = os.getenv("USE_GPU_EMBEDDINGS", "true").lower() == "true"


class EmbeddingService:
    """
    Unified embedding service with multiple providers
    
    Providers:
    - GPU Service (fastest, 10-20x speedup)
    - OpenAI (high quality)
    - Cohere (multilingual)
    - Sentence-BERT (local, free)
    """
    
    def __init__(self):
        self.gpu_url = GPU_EMBEDDING_URL
        self.use_gpu = USE_GPU_SERVICE
        
        # Stats
        self.stats = {
            "gpu_calls": 0,
            "openai_calls": 0,
            "cohere_calls": 0,
            "local_calls": 0,
            "errors": 0
        }
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-ada-002"
    ) -> List[List[float]]:
        """
        Generate embeddings using best available method
        
        Args:
            texts: List of texts to embed
            model: Model name
        
        Returns:
            List of embedding vectors
        """
        # Try GPU service first if enabled
        if self.use_gpu and "ada" in model.lower():
            try:
                embeddings = await self._gpu_embeddings(texts)
                if embeddings:
                    self.stats["gpu_calls"] += 1
                    return embeddings
            except Exception as e:
                logger.warning(f"GPU service failed: {e}, using fallback")
                self.stats["errors"] += 1
        
        # Fallback to specific provider
        if "ada" in model.lower() or "openai" in model.lower():
            return await self._openai_embeddings(texts, model)
        elif "cohere" in model.lower():
            return await self._cohere_embeddings(texts, model)
        else:
            return await self._local_embeddings(texts, model)
    
    async def _gpu_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Call GPU embedding service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.gpu_url}/api/v1/embeddings/generate",
                    json={"texts": texts, "normalize": True},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ GPU embeddings: {len(texts)} texts")
                    return data["embeddings"]
                
                return None
        
        except Exception as e:
            logger.error(f"GPU service error: {e}")
            return None
    
    async def _openai_embeddings(
        self,
        texts: List[str],
        model: str
    ) -> List[List[float]]:
        """Generate embeddings using OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # OpenAI has a limit of ~8000 texts per request
            batch_size = 2000
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = client.embeddings.create(
                    input=batch,
                    model=model
                )
                embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(embeddings)
            
            self.stats["openai_calls"] += 1
            logger.info(f"✅ OpenAI embeddings: {len(texts)} texts")
            return all_embeddings
        
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            self.stats["errors"] += 1
            raise
    
    async def _cohere_embeddings(
        self,
        texts: List[str],
        model: str
    ) -> List[List[float]]:
        """Generate embeddings using Cohere"""
        try:
            import cohere
            co = cohere.Client(os.getenv("COHERE_API_KEY"))
            
            response = co.embed(
                texts=texts,
                model=model,
                input_type="search_document"
            )
            
            self.stats["cohere_calls"] += 1
            logger.info(f"✅ Cohere embeddings: {len(texts)} texts")
            return response.embeddings
        
        except Exception as e:
            logger.error(f"Cohere error: {e}")
            self.stats["errors"] += 1
            raise
    
    async def _local_embeddings(
        self,
        texts: List[str],
        model: str
    ) -> List[List[float]]:
        """Generate embeddings using local Sentence-BERT"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Load model (cached after first load)
            encoder = SentenceTransformer(model)
            
            # Generate embeddings
            embeddings = encoder.encode(texts, convert_to_numpy=True)
            
            self.stats["local_calls"] += 1
            logger.info(f"✅ Local embeddings: {len(texts)} texts")
            return embeddings.tolist()
        
        except Exception as e:
            logger.error(f"Local embedding error: {e}")
            self.stats["errors"] += 1
            raise
    
    def get_stats(self) -> dict:
        """Get usage statistics"""
        total = sum([
            self.stats["gpu_calls"],
            self.stats["openai_calls"],
            self.stats["cohere_calls"],
            self.stats["local_calls"]
        ])
        
        return {
            **self.stats,
            "total_calls": total,
            "gpu_percentage": (self.stats["gpu_calls"] / total * 100) if total > 0 else 0
        }


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
