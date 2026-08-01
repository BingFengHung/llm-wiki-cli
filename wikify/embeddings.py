from typing import List
from sentence_transformers import SentenceTransformer

class EmbeddingEngine:
    """Generates 384-dimensional vector embeddings using local HuggingFace models."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Encodes input text string into a float vector embedding."""
        if not text or not text.strip():
            return [0.0] * 384
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
