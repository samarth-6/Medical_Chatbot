
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TextChunker:

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 800,
        overlap: int = 150
    ) -> List[str]:
   
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += (chunk_size - overlap)
        
        return chunks
    
    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
 
        text = document.get("text", "")
        metadata = document.get("metadata", {})
    
        text_chunks = self.chunk_text(text)
        
        chunks_with_metadata = []
        for i, chunk_text in enumerate(text_chunks):
            chunks_with_metadata.append({
                "text": chunk_text,
                "metadata": {
                    **metadata,  
                    "chunk_index": i,
                    "chunk_size": len(chunk_text)
                }
            })
        
        logger.debug(f"Created {len(chunks_with_metadata)} chunks from document")
        return chunks_with_metadata
    
    def chunk_batch(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
   
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} total chunks from {len(documents)} documents")
        return all_chunks


def chunk_document(document: Dict[str, Any], chunk_size: int = 800, overlap: int = 150) -> List[Dict[str, Any]]:
    chunker = TextChunker()
    return chunker.chunk_document(document)