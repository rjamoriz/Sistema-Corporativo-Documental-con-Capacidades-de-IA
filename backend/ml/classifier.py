"""
Wrapper para modelo de clasificación con transformers (BETO/RoBERTa)
"""
from typing import List, Dict, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

from core.logging_config import logger
from core.config import settings


class ClassifierModel:
    """Modelo de clasificación de documentos"""
    
    def __init__(self):
        self.model_name = settings.CLASSIFICATION_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        # OPTIMIZACIÓN: Lazy loading
        # self._load_model()  # Comentado
        logger.info(f"ClassifierModel initialized (lazy loading enabled)")
    
    def _load_model(self):
        """Carga el modelo de clasificación (lazy loading)"""
        if self.model is not None or self.pipeline is not None:
            return  # Ya está cargado
            
        try:
            logger.info(f"Loading classification model: {self.model_name} (first use)")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Classification model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.warning(f"Could not load custom model, using default: {e}")
            # Fallback a un modelo general
            self.pipeline = pipeline(
                "text-classification",
                model="dccuchile/bert-base-spanish-wwm-uncased",
                device=0 if self.device == "cuda" else -1
            )
    
    def classify(self, text: str, max_length: int = 512) -> Dict:
        """
        Clasifica un texto
        
        Args:
            text: Texto a clasificar
            max_length: Longitud máxima de tokens
            
        Returns:
            Dict: Resultado con categoría y confianza
        """
        # LAZY LOADING: Cargar modelo solo cuando se usa
        if self.model is None and self.pipeline is None:
            self._load_model()
        
        if self.pipeline:
            result = self.pipeline(text[:2000])[0]
            return {
                "category": result["label"],
                "confidence": result["score"],
                "method": "pipeline"
            }
        
        # Tokenizar
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,
            padding=True
        ).to(self.device)
        
        # Inferencia
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Obtener predicción
        confidence, predicted_class = torch.max(predictions, dim=1)
        
        return {
            "category": self._get_category_name(predicted_class.item()),
            "confidence": confidence.item(),
            "method": "transformer"
        }
    
    def classify_batch(self, texts: List[str], max_length: int = 512) -> List[Dict]:
        """
        Clasifica múltiples textos en batch
        
        Args:
            texts: Lista de textos
            max_length: Longitud máxima de tokens
            
        Returns:
            List[Dict]: Lista de resultados
        """
        if self.pipeline:
            results = self.pipeline(texts)
            return [
                {
                    "category": r["label"],
                    "confidence": r["score"],
                    "method": "pipeline"
                }
                for r in results
            ]
        
        # Tokenizar batch
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,
            padding=True
        ).to(self.device)
        
        # Inferencia batch
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Procesar resultados
        results = []
        for i in range(len(texts)):
            confidence, predicted_class = torch.max(predictions[i], dim=0)
            results.append({
                "category": self._get_category_name(predicted_class.item()),
                "confidence": confidence.item(),
                "method": "transformer"
            })
        
        return results
    
    def _get_category_name(self, class_id: int) -> str:
        """Mapea ID de clase a nombre de categoría"""
        categories = [
            "LEGAL", "FINANCIAL", "HR", "TECHNICAL",
            "MARKETING", "OPERATIONS", "COMPLIANCE", "SENSITIVE"
        ]
        return categories[class_id] if class_id < len(categories) else "UNCLASSIFIED"
    
    def get_model_info(self) -> Dict:
        """
        Obtiene información del modelo
        
        Returns:
            Dict: Información del modelo
        """
        if self.model:
            return {
                "model_name": self.model_name,
                "device": self.device,
                "num_labels": self.model.config.num_labels if hasattr(self.model, 'config') else None,
                "max_length": self.tokenizer.model_max_length if self.tokenizer else None
            }
        return {
            "model_name": "default_pipeline",
            "device": self.device
        }
    
    def fine_tune(self, train_texts: List[str], train_labels: List[int], epochs: int = 3):
        """
        Fine-tuning del modelo (para futuro entrenamiento)
        
        Args:
            train_texts: Textos de entrenamiento
            train_labels: Etiquetas correspondientes
            epochs: Número de épocas
        """
        logger.info("Fine-tuning not yet implemented")
        # TODO: Implementar fine-tuning con Trainer de transformers
        pass


# Instancia singleton del modelo
classifier_model = ClassifierModel()
