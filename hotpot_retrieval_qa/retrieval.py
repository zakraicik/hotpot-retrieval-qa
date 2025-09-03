import os
import logging
import pickle
import faiss
import time
import numpy as np
from sentence_transformers import SentenceTransformer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Retrieval:

    def __init__(
        self,
        cache_dir=os.path.join(os.getcwd(), "data", "cached"),
    ):
        self.cache_dir = cache_dir
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.documents = None
        self._load_index()

    def _load_index(self):
        try:

            start_time = time.time()

            self.index = faiss.read_index(f"{self.cache_dir}/faiss.index")
            with open(f"{self.cache_dir}/documents.pkl", "rb") as f:
                self.documents = pickle.load(f)
            elapsed = time.time() - start_time
            logging.info(
                f"Loaded index with {len(self.documents)} documents in {elapsed:.2f} seconds"
            )

        except FileNotFoundError as e:
            logging.error(f"Index files not found. Run build_index.py first.")
            raise

    def retrieve(self, query: str, k: int = 5):
        if self.index is None or self.documents is None:
            logging.error(f"Index files not found. Run build_index.py first.")
            raise

        start_time = time.time()

        query_embedding = self.embedder.encode([query])
        query_embedding = query_embedding / np.linalg.norm(
            query_embedding, axis=1, keepdims=True
        )

        scores, indices = self.index.search(query_embedding.astype("float32"), k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                results.append(
                    {
                        "document": self.documents[idx],
                        "score": float(score),
                        "index": int(idx),
                    }
                )

        elapsed = time.time() - start_time
        logging.info(
            f"Retrieved {len(results)} results for query '{query}' in {elapsed:.2f} seconds"
        )

        return results
