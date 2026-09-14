import re
from typing import List
from ingestion.config import settings

def chunk_text(text: str, chunk_size: int = settings.CHUNK_SIZE, overlap: int = settings.CHUNK_OVERLAP) -> List[str]:
    target_words = int(chunk_size / 1.3)
    overlap_words = int(overlap / 1.3)
    
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for p in paragraphs:
        p_words = len(p.split())
        if current_length + p_words > target_words and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            
            overlap_chunk = []
            overlap_length = 0
            for prev_p in reversed(current_chunk):
                prev_words = len(prev_p.split())
                if overlap_length + prev_words <= overlap_words:
                    overlap_chunk.insert(0, prev_p)
                    overlap_length += prev_words
                else:
                    break
                    
            current_chunk = overlap_chunk + [p]
            current_length = overlap_length + p_words
        else:
            current_chunk.append(p)
            current_length += p_words
            
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
        
    return chunks
