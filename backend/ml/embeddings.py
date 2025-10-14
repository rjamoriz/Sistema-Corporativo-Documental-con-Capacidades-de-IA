"""
Wrapper para modelo de embeddings con sentence-transformers
"""
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

from core.logging_config import logger
from core.config import settings


class EmbeddingModel:
    """Modelo para generación de embeddings de documentos con optimización GPU"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        
        # GPU Detection y configuración
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.gpu_available = torch.cuda.is_available()
        
        if self.gpu_available:
            self.gpu_name = torch.cuda.get_device_name(0)
            self.gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            logger.info(f"GPU detected: {self.gpu_name} ({self.gpu_memory:.1f}GB)")
        else:
            logger.info("No GPU detected, using CPU")
        
        self.model = None
        # Ajustar batch size según device
        self.default_batch_size = 64 if self.gpu_available else 16
        logger.info(f"EmbeddingModel initialized - Device: {self.device}, Batch size: {self.default_batch_size}")
    
    def _load_model(self):
        """Carga el modelo de embeddings (lazy loading) con optimización GPU"""
        if self.model is not None:
            return  # Ya está cargado
            
        try:
            logger.info(f"Loading embedding model: {self.model_name} on {self.device}")
            
            # Cargar modelo con device específico
            self.model = SentenceTransformer(self.model_name, device=self.device)
            
            # Si usamos GPU, optimizar para rendimiento
            if self.gpu_available:
                # Configurar modelo para evaluación (no entrenamiento)
                self.model.eval()
                # Usar half precision en GPU si es soportado (RTX 4070 lo soporta)
                try:
                    self.model.half()
                    logger.info("Half precision (FP16) enabled for GPU")
                except Exception as e:
                    logger.warning(f"Could not enable FP16: {e}")
                    
                # Warming up GPU
                logger.info("Warming up GPU...")
                dummy_text = ["This is a dummy text for GPU warmup"]
                _ = self.model.encode(dummy_text, convert_to_numpy=True)
                logger.info("GPU warmup completed")
            
            # Verificar dimensión
            test_embedding = self.model.encode(["test"])[0]
            if len(test_embedding) != self.dimension:
                logger.warning(
                    f"Expected embedding dimension {self.dimension}, "
                    f"got {len(test_embedding)}"
                )
                self.dimension = len(test_embedding)
                
            logger.info(f"Embedding model loaded successfully - Dim: {self.dimension}")
            
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = None,
        show_progress: bool = False,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Genera embeddings para texto(s) con optimización GPU
        
        Args:
            texts: Texto o lista de textos
            batch_size: Tamaño de batch (None = usar default optimizado)
            show_progress: Mostrar barra de progreso
            normalize: Normalizar vectores
            
        Returns:
            np.ndarray: Vector(es) de embeddings
        """
        # LAZY LOADING: Cargar modelo solo cuando se usa
        if self.model is None:
            self._load_model()
        
        if isinstance(texts, str):
            texts = [texts]
        
        # Usar batch size optimizado para GPU/CPU
        if batch_size is None:
            batch_size = self.default_batch_size
            
        # Para GPU, usar batch size más grande si hay muchos textos
        if self.gpu_available and len(texts) > 100:
            batch_size = min(128, batch_size * 2)
        
        logger.debug(f"Encoding {len(texts)} texts with batch_size={batch_size} on {self.device}")
        
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
    
    def get_gpu_info(self) -> dict:
        """
        Obtiene información del estado de la GPU
        
        Returns:
            dict: Información de GPU
        """
        gpu_info = {
            "gpu_available": self.gpu_available,
            "device": self.device,
            "default_batch_size": self.default_batch_size
        }
        
        if self.gpu_available:
            gpu_info.update({
                "gpu_name": self.gpu_name,
                "gpu_memory_total": f"{self.gpu_memory:.1f}GB",
                "gpu_memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f}GB",
                "gpu_memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**3:.2f}GB",
                "cuda_version": torch.version.cuda
            })
        
        return gpu_info
    
    def benchmark_performance(self, num_texts: int = 100) -> dict:
        """
        Realiza un benchmark de rendimiento
        
        Args:
            num_texts: Número de textos para el benchmark
            
        Returns:
            dict: Métricas de rendimiento
        """
        import time
        
        # Asegurar que el modelo esté cargado
        if self.model is None:
            self._load_model()
        
        # Generar textos de prueba
        test_texts = [f"Este es un texto de prueba número {i} para benchmark." for i in range(num_texts)]
        
        # Benchmark
        start_time = time.time()
        embeddings = self.encode(test_texts, show_progress=False)
        end_time = time.time()
        
        total_time = end_time - start_time
        texts_per_second = num_texts / total_time
        
        benchmark_results = {
            "num_texts": num_texts,
            "total_time": f"{total_time:.2f}s",
            "texts_per_second": f"{texts_per_second:.1f}",
            "device": self.device,
            "batch_size_used": self.default_batch_size,
            "embedding_dimension": embeddings.shape[1] if len(embeddings.shape) > 1 else len(embeddings)
        }
        
        if self.gpu_available:
            benchmark_results["gpu_memory_peak"] = f"{torch.cuda.max_memory_allocated(0) / 1024**3:.2f}GB"
            torch.cuda.reset_peak_memory_stats(0)  # Reset para próximo benchmark
        
        logger.info(f"Benchmark completed: {texts_per_second:.1f} texts/sec on {self.device}")
        
        return benchmark_results
    
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
