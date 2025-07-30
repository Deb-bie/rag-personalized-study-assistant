from typing import List, Dict, Any
import re
from app.core.config import settings


class TextChunker:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    def chunk_text(self, text: str, document_id: int = None) -> List[Dict[str, Any]]:
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_length = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "text": current_chunk.strip(),
                    "chunk_index": chunk_index,
                    "document_id": document_id
                })
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + " " + sentence
                current_length = len(current_chunk)
                chunk_index += 1
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_length += sentence_length
        
        # Add final chunk if it has content
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_index": chunk_index,
                "document_id": document_id
            })
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        # Simple sentence splitting - can be improved with nltk or spacy
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str) -> str:
        if len(text) <= self.chunk_overlap:
            return text
        return text[-self.chunk_overlap:]