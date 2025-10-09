"""
Wrapper para modelo de embeddings con sentence-transformers
"""
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

from backend.core.logging_config import logger
from backend.core.config import settings


class EmbeddingModel:
    """Modelo para generación de embeddings de documentos"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo de embeddings"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Embedding model loaded successfully on {self.device}")
            
            # Verificar dimensión
            test_embedding = self.model.encode(["test"])[0]
            if len(test_embedding) != self.dimension:
                logger.warning(
                    f"Expected embedding dimension {self.dimension}, "
                    f"got {len(test_embedding)}"
                )
                self.dimension = len(test_embedding)
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Genera embeddings para texto(s)
        
        Args:
            texts: Texto o lista de textos
            batch_size: Tamaño de batch para procesamiento
            show_progress: Mostrar barra de progreso
            normalize: Normalizar vectores
            
        Returns:
            np.ndarray: Vector(es) de embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        
        return embeddings
    
    def encode_queries(
        self,
        queries: Union[str, List[str]],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Genera embeddings optimizados para queries de búsqueda
        
        Args:
            queries: Query o lista de queries
            normalize: Normalizar vectores
            
        Returns:
            np.ndarray: Vector(es) de embeddings
        """
        if isinstance(queries, str):
            queries = [queries]
        
        # Algunos modelos tienen encoding específico para queries
        if hasattr(self.model, 'encode_queries'):
            embeddings = self.model.encode_queries(
                queries,
                convert_to_numpy=True,
                normalize_embeddings=normalize
            )
        else:
            embeddings = self.encode(queries, normalize=normalize)
        
        return embeddings
    
    def encode_documents(
        self,
        documents: List[str],
        batch_size: int = 32,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Genera embeddings optimizados para documentos
        
        Args:
            documents: Lista de documentos
            batch_size: Tamaño de batch
            normalize: Normalizar vectores
            
        Returns:
            np.ndarray: Matriz de embeddings
        """
        # Algunos modelos tienen encoding específico para documentos
        if hasattr(self.model, 'encode_corpus'):
            embeddings = self.model.encode_corpus(
                documents,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=normalize
            )
        else:
            embeddings = self.encode(documents, batch_size=batch_size, normalize=normalize)
        
        return embeddings
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcula similaridad coseno entre dos embeddings
        
        Args:
            embedding1: Primer embedding
            embedding2: Segundo embedding
            
        Returns:
            float: Similaridad (0-1)
        """
        # Normalizar si es necesario
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(embedding1, embedding2) / (norm1 * norm2)
    
    def similarity_matrix(
        self,
        embeddings1: np.ndarray,
        embeddings2: np.ndarray
    ) -> np.ndarray:
        """
        Calcula matriz de similaridades entre dos conjuntos de embeddings
        
        Args:
            embeddings1: Primera matriz de embeddings (N x D)
            embeddings2: Segunda matriz de embeddings (M x D)
            
        Returns:
            np.ndarray: Matriz de similaridades (N x M)
        """
        # Normalizar
        embeddings1_norm = embeddings1 / np.linalg.norm(embeddings1, axis=1, keepdims=True)
        embeddings2_norm = embeddings2 / np.linalg.norm(embeddings2, axis=1, keepdims=True)
        
        # Producto matricial
        return np.matmul(embeddings1_norm, embeddings2_norm.T)
    
    def get_model_info(self) -> dict:
        """
        Obtiene información del modelo
        
        Returns:
            dict: Información del modelo
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.dimension,
            "device": self.device,
            "max_seq_length": self.model.max_seq_length if hasattr(self.model, 'max_seq_length') else None,
            "pooling": str(self.model._modules.get('1')) if hasattr(self.model, '_modules') else None
        }


# Instancia singleton del modelo
embedding_model = EmbeddingModel()
