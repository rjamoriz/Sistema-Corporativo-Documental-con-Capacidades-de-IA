"""
Wrapper para modelo NER con spaCy
Maneja Named Entity Recognition en español
"""
from typing import List, Dict, Tuple
import spacy
from spacy.tokens import Doc

from backend.core.logging_config import logger
from backend.core.config import settings


class NERModel:
    """Modelo de Named Entity Recognition"""
    
    def __init__(self):
        self.model_name = settings.SPACY_MODEL
        self.nlp = None
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo de spaCy"""
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy NER model: {self.model_name}")
        except OSError:
            logger.warning(f"Model {self.model_name} not found, downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", self.model_name])
            self.nlp = spacy.load(self.model_name)
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extrae entidades nombradas del texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            List[Dict]: Lista de entidades con tipo, texto, posición y confianza
        """
        doc = self.nlp(text[:1000000])  # Limitar a 1M caracteres
        
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "label_description": spacy.explain(ent.label_)
            })
        
        return entities
    
    def extract_entities_with_context(self, text: str, context_window: int = 50) -> List[Dict]:
        """
        Extrae entidades con contexto alrededor
        
        Args:
            text: Texto a analizar
            context_window: Caracteres de contexto a cada lado
            
        Returns:
            List[Dict]: Lista de entidades con contexto
        """
        doc = self.nlp(text[:1000000])
        
        entities = []
        for ent in doc.ents:
            start = max(0, ent.start_char - context_window)
            end = min(len(text), ent.end_char + context_window)
            context = text[start:end]
            
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "context": context,
                "label_description": spacy.explain(ent.label_)
            })
        
        return entities
    
    def get_entity_counts(self, text: str) -> Dict[str, int]:
        """
        Cuenta entidades por tipo
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict[str, int]: Contador de entidades por tipo
        """
        doc = self.nlp(text[:1000000])
        
        counts = {}
        for ent in doc.ents:
            counts[ent.label_] = counts.get(ent.label_, 0) + 1
        
        return counts
    
    def get_model_info(self) -> Dict:
        """
        Obtiene información del modelo
        
        Returns:
            Dict: Información del modelo
        """
        return {
            "model_name": self.model_name,
            "language": self.nlp.lang,
            "pipeline": self.nlp.pipe_names,
            "entity_labels": list(self.nlp.get_pipe("ner").labels)
        }


# Instancia singleton del modelo
ner_model = NERModel()
