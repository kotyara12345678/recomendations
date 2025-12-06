from sentence_transformers import SentenceTransformer
import os
from typing import List
import numpy as np

class Embedder:
    def __init__(self, model_name: str = None):
        model_name = model_name or os.getenv('EMBED_MODEL','all-MiniLM-L6-v2')
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]):
        if not texts:
            return []
        embs = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return [e.astype('float32') for e in embs]