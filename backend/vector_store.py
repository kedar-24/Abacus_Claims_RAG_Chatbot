import os
import logging
import pickle
from pathlib import Path
from typing import Optional, List, Dict, Any

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """A simple vector store using sentence transformers and cosine similarity."""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2') -> None:
        self.model = SentenceTransformer(model_name)
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add documents to the vector store."""
        if not documents:
            return

        logger.info(f"Embedding {len(documents)} documents...")
        new_embeddings = self.model.encode(documents)

        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

        self.documents.extend(documents)
        if metadatas:
            self.metadatas.extend(metadatas)
        else:
            self.metadatas.extend([{} for _ in documents])

    def query(self, query_text: str, k: int = 3) -> List[Dict[str, Any]]:
        """Query the vector store for similar documents."""
        if self.embeddings is None:
            return []

        query_embedding = self.model.encode([query_text])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        # Get top k indices
        top_k_indices = np.argsort(similarities)[-k:][::-1]

        results = []
        for idx in top_k_indices:
            score = float(similarities[idx])
            # Handle NaN/Inf for JSON compliance
            if np.isnan(score) or np.isinf(score):
                score = 0.0

            # Sanitize metadata
            safe_metadata = self._sanitize_data(self.metadatas[idx])

            results.append({
                "document": self.documents[idx],
                "metadata": safe_metadata,
                "score": score
            })
        return results

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data for JSON serialization."""
        if isinstance(data, dict):
            return {k: self._sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(v) for v in data]
        elif isinstance(data, float):
            if np.isnan(data) or np.isinf(data):
                return None
        return data

    def save(self, path: str) -> None:
        """Save the vector store to a pickle file."""
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(path_obj, 'wb') as f:
            pickle.dump({
                "documents": self.documents,
                "metadatas": self.metadatas,
                "embeddings": self.embeddings
            }, f)
        logger.info(f"Index saved to {path}")

    def load(self, path: str) -> None:
        """Load the vector store from a pickle file."""
        if not os.path.exists(path):
            logger.warning(f"No existing index found at {path}")
            return

        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data["documents"]
            self.metadatas = data["metadatas"]
            self.embeddings = data["embeddings"]
        logger.info(f"Index loaded from {path} ({len(self.documents)} documents)")
