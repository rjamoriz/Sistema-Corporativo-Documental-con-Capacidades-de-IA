"""
Servicio de Extracción de Información
Maneja NER, generación de embeddings y extracción de metadata
"""
import re
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import spacy
from sentence_transformers import SentenceTransformer
import numpy as np

from backend.core.logging_config import logger
from backend.core.config import settings
from backend.models.database_models import Document, DocumentChunk, Entity, DocumentStatus


class ExtractService:
    """Servicio para extracción de información"""
    
    def __init__(self):
        # Cargar modelo de spaCy para NER
        try:
            self.nlp = spacy.load(settings.SPACY_MODEL)
            logger.info(f"Loaded spaCy model: {settings.SPACY_MODEL}")
        except OSError:
            logger.warning(f"spaCy model {settings.SPACY_MODEL} not found, downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", settings.SPACY_MODEL])
            self.nlp = spacy.load(settings.SPACY_MODEL)
        
        # Cargar modelo de embeddings
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
        
        # Configuración de chunking
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    async def extract_information(
        self,
        document: Document,
        text: str,
        db: AsyncSession
    ) -> Dict:
        """
        Extrae información completa de un documento
        
        Args:
            document: Documento del que extraer información
            text: Texto del documento
            db: Sesión de base de datos
            
        Returns:
            Dict: Resultado con chunks, entities y metadata
        """
        try:
            # 1. Dividir en chunks
            chunks = self._create_chunks(text)
            logger.info(f"Created {len(chunks)} chunks for document {document.id}")
            
            # 2. Generar embeddings para cada chunk
            chunk_embeddings = self._generate_embeddings(chunks)
            
            # 3. Guardar chunks en BD
            chunk_objects = []
            for i, (chunk_text, embedding) in enumerate(zip(chunks, chunk_embeddings)):
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=i,
                    content=chunk_text,
                    embedding=embedding.tolist(),
                    token_count=len(chunk_text.split())
                )
                chunk_objects.append(chunk)
                db.add(chunk)
            
            # 4. Extraer entidades (NER)
            entities = await self._extract_entities(document.id, text, db)
            logger.info(f"Extracted {len(entities)} entities from document {document.id}")
            
            # 5. Extraer metadata adicional
            metadata = self._extract_metadata(text)
            
            # 6. Actualizar metadata del documento
            document.metadata_.update(metadata)
            document.status = DocumentStatus.PROCESSED
            document.processed_at = datetime.utcnow()
            
            await db.commit()
            
            return {
                "chunk_count": len(chunks),
                "entity_count": len(entities),
                "metadata": metadata,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error extracting information from document {document.id}: {e}", exc_info=True)
            document.status = DocumentStatus.FAILED
            await db.commit()
            return {
                "chunk_count": 0,
                "entity_count": 0,
                "metadata": {},
                "status": "failed",
                "error": str(e)
            }
    
    def _create_chunks(self, text: str) -> List[str]:
        """
        Divide el texto en chunks con solapamiento
        
        Args:
            text: Texto a dividir
            
        Returns:
            List[str]: Lista de chunks
        """
        # Limpiar texto
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenizar por palabras
        words = text.split()
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunks.append(' '.join(chunk_words))
            
            # Avanzar con solapamiento
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def _generate_embeddings(self, chunks: List[str]) -> List[np.ndarray]:
        """
        Genera embeddings para una lista de chunks
        
        Args:
            chunks: Lista de textos
            
        Returns:
            List[np.ndarray]: Lista de vectores de embeddings
        """
        try:
            embeddings = self.embedding_model.encode(
                chunks,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}", exc_info=True)
            # Devolver embeddings cero en caso de error
            return [np.zeros(settings.EMBEDDING_DIMENSION) for _ in chunks]
    
    async def _extract_entities(
        self,
        document_id: UUID,
        text: str,
        db: AsyncSession
    ) -> List[Entity]:
        """
        Extrae entidades nombradas del texto
        
        Args:
            document_id: ID del documento
            text: Texto del que extraer entidades
            db: Sesión de base de datos
            
        Returns:
            List[Entity]: Lista de entidades extraídas
        """
        entities = []
        
        try:
            # Procesar con spaCy
            doc = self.nlp(text[:1000000])  # Limitar a 1M caracteres por performance
            
            # Diccionario para contar ocurrencias
            entity_counts = {}
            
            for ent in doc.ents:
                key = (ent.text, ent.label_)
                if key not in entity_counts:
                    entity_counts[key] = {
                        "text": ent.text,
                        "label": ent.label_,
                        "count": 0,
                        "positions": []
                    }
                entity_counts[key]["count"] += 1
                entity_counts[key]["positions"].append(ent.start_char)
            
            # Crear objetos Entity
            for (text, label), data in entity_counts.items():
                entity = Entity(
                    document_id=document_id,
                    entity_type=label,
                    entity_value=text,
                    confidence=data["count"] / len(doc.ents) if len(doc.ents) > 0 else 1.0,
                    metadata_={
                        "count": data["count"],
                        "positions": data["positions"][:10]  # Limitar a 10 posiciones
                    }
                )
                entities.append(entity)
                db.add(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}", exc_info=True)
            return []
    
    def _extract_metadata(self, text: str) -> Dict:
        """
        Extrae metadata adicional del texto
        
        Args:
            text: Texto del documento
            
        Returns:
            Dict: Metadata extraída
        """
        metadata = {}
        
        try:
            # Longitud y estadísticas básicas
            metadata["char_count"] = len(text)
            metadata["word_count"] = len(text.split())
            metadata["line_count"] = text.count('\n') + 1
            
            # Detección de idioma principal
            from langdetect import detect, detect_langs
            try:
                metadata["language"] = detect(text[:10000])  # Muestra de 10k chars
                lang_probs = detect_langs(text[:10000])
                metadata["language_confidence"] = max([lp.prob for lp in lang_probs])
            except:
                metadata["language"] = "unknown"
                metadata["language_confidence"] = 0.0
            
            # Extraer fechas
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
            dates = re.findall(date_pattern, text)
            if dates:
                metadata["dates_found"] = list(set(dates[:10]))  # Primeras 10 únicas
            
            # Extraer emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            if emails:
                metadata["emails_found"] = list(set(emails[:10]))
            
            # Extraer teléfonos (formato español e internacional)
            phone_pattern = r'\b(?:\+34|0034)?[\s\-]?[6789]\d{2}[\s\-]?\d{3}[\s\-]?\d{3}\b'
            phones = re.findall(phone_pattern, text)
            if phones:
                metadata["phones_found"] = list(set(phones[:10]))
            
            # Extraer URLs
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            urls = re.findall(url_pattern, text)
            if urls:
                metadata["urls_found"] = list(set(urls[:10]))
            
            # Extraer referencias a artículos legales (formato español)
            legal_pattern = r'\b(?:artículo|art\.|Art\.|ARTÍCULO)\s+\d+(?:\.\d+)?(?:\s+[a-z])?'
            legal_refs = re.findall(legal_pattern, text, re.IGNORECASE)
            if legal_refs:
                metadata["legal_references"] = list(set(legal_refs[:10]))
            
            # Extraer importes monetarios
            amount_pattern = r'(?:€|EUR|USD|\$)\s*[\d.,]+(?:\.\d{2})?|[\d.,]+(?:\.\d{2})?\s*(?:€|EUR|USD|\$|euros?|dólares?)'
            amounts = re.findall(amount_pattern, text, re.IGNORECASE)
            if amounts:
                metadata["amounts_found"] = list(set(amounts[:10]))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}", exc_info=True)
            return metadata
    
    async def generate_document_embedding(self, document: Document, db: AsyncSession) -> Optional[np.ndarray]:
        """
        Genera embedding agregado para el documento completo
        
        Args:
            document: Documento
            db: Sesión de base de datos
            
        Returns:
            Optional[np.ndarray]: Vector de embedding o None
        """
        try:
            # Obtener todos los chunks del documento
            result = await db.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document.id)
                .order_by(DocumentChunk.chunk_index)
            )
            chunks = result.scalars().all()
            
            if not chunks:
                return None
            
            # Agregar embeddings (promedio)
            embeddings = np.array([chunk.embedding for chunk in chunks])
            document_embedding = np.mean(embeddings, axis=0)
            
            return document_embedding
            
        except Exception as e:
            logger.error(f"Error generating document embedding: {e}", exc_info=True)
            return None


# Instancia singleton del servicio
extract_service = ExtractService()
