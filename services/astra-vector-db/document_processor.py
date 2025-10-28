"""
Document Processor
Handles document extraction and chunking
"""
import logging
from typing import List, Tuple
import re

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Process documents for vector storage
    
    Features:
    - Text extraction from PDF, DOCX, TXT
    - Intelligent chunking with overlap
    - Metadata extraction
    """
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(file_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info(f"✅ Extracted {len(text)} chars from PDF")
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            logger.info(f"✅ Extracted {len(text)} chars from DOCX")
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            raise
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"✅ Extracted {len(text)} chars from TXT")
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting TXT: {e}")
            raise
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        # Clean text
        text = self._clean_text(text)
        
        # Split into sentences (better than character split)
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            # If adding this sentence exceeds chunk_size, save current chunk
            if current_size + sentence_size > chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)
                
                # Keep last sentences for overlap
                overlap_sentences = []
                overlap_size = 0
                for s in reversed(current_chunk):
                    if overlap_size + len(s) <= chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_size += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_size = overlap_size
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        logger.info(f"✅ Created {len(chunks)} chunks from text")
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?¿¡\-áéíóúñÁÉÍÓÚÑ]', '', text)
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitter (can be improved with spaCy/NLTK)
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def extract_metadata(self, text: str) -> dict:
        """Extract metadata from text"""
        metadata = {
            "char_count": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(self._split_into_sentences(text))
        }
        
        # Extract dates (simple pattern)
        dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
        if dates:
            metadata["dates_found"] = dates[:5]  # First 5 dates
        
        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            metadata["emails_found"] = emails[:5]
        
        return metadata


# Singleton
_processor: DocumentProcessor = None


def get_document_processor() -> DocumentProcessor:
    """Get document processor singleton"""
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor
