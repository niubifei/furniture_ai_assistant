from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, EMBEDDING_DIM

class M3EEmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.embedding_dim = EMBEDDING_DIM
    
    def encode(self, texts, batch_size=32, show_progress=False):
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings
    
    def encode_single(self, text):
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()