from typing import List

def chunk_text(text: str, max_chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits input text into chunks of maximum max_chunk_size characters,
    with sliding overlap to preserve context across boundaries.
    """
    if not text or not text.strip():
        return []
        
    lines = text.splitlines(keepends=True)
    chunks = []
    current_chunk = ""
    
    for line in lines:
        if len(current_chunk) + len(line) <= max_chunk_size:
            current_chunk += line
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Handle sliding overlap by taking trailing characters
            if overlap > 0 and len(current_chunk) > overlap:
                overlap_text = current_chunk[-overlap:]
                current_chunk = overlap_text + line
            else:
                current_chunk = line
                
    if current_chunk and current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    return chunks
