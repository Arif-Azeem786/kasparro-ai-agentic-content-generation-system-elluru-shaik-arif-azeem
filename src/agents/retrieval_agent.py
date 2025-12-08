# src/agents/retrieval_agent.py
from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except Exception as e:
    # If these libs aren't installed, keep agent importable but non-functional.
    SentenceTransformer = None
    faiss = None

class RetrievalAgent:
    """
    Build an in-memory FAISS index over given texts and support semantic queries.
    If sentence-transformers / faiss not installed, this agent raises descriptive errors.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if SentenceTransformer is None or faiss is None:
            raise RuntimeError("RetrievalAgent requires 'sentence-transformers' and 'faiss-cpu' installed.")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.corpus: List[str] = []

    def build_index(self, texts: List[str]):
        """
        texts: list of strings to index
        """
        if not texts:
            self.index = None
            self.corpus = []
            return

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        dim = embeddings.shape[1]
        # use IndexFlatL2 for simplicity
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype(np.float32))
        self.index = index
        self.corpus = texts.copy()

    def query(self, query: str, top_k: int = 3) -> List[str]:
        """Return the top_k most similar texts (strings)."""
        if self.index is None:
            return []
        vec = self.model.encode([query], convert_to_numpy=True).astype(np.float32)
        D, I = self.index.search(vec, top_k)
        results = []
        for idx in I[0]:
            if idx < 0 or idx >= len(self.corpus):
                continue
            results.append(self.corpus[idx])
        return results
