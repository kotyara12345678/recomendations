from sentence_transformers import SentenceTransformer
import os
from typing import List

class Embedder:
    def __init__(self, model_name: str = None):
        model_name = model_name or os.getenv('EMBED_MODEL', 'all-MiniLM-L6-v2')
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embs = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        # Преобразуем numpy -> list[float]
        return [e.astype('float32').tolist() for e in embs]