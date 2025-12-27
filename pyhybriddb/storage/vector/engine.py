"""
Vector Storage Engine - AI/Embeddings
Stores vectors and performs similarity search.
"""

import numpy as np
import uuid
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

class VectorIndex:
    """Vector Index (Flat / Brute Force for MVP)"""

    def __init__(self, name: str, dimension: int, path: Path):
        self.name = name
        self.dimension = dimension
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)

        self.ids: List[str] = []
        self.vectors: Optional[np.ndarray] = None
        self._load()

    def _load(self):
        """Load vectors and IDs"""
        ids_file = self.path / "ids.npy"
        vec_file = self.path / "vectors.npy"

        if ids_file.exists() and vec_file.exists():
            self.ids = np.load(str(ids_file), allow_pickle=True).tolist()
            self.vectors = np.load(str(vec_file))
        else:
            self.vectors = np.zeros((0, self.dimension), dtype=np.float32)

    def add(self, vector: List[float], record_id: Optional[str] = None) -> str:
        """Add a vector"""
        if record_id is None:
            record_id = str(uuid.uuid4())

        vec_np = np.array([vector], dtype=np.float32)

        if self.vectors.shape[0] == 0:
            self.vectors = vec_np
        else:
            self.vectors = np.vstack([self.vectors, vec_np])

        self.ids.append(record_id)
        self._save()
        return record_id

    def _save(self):
        """Save to disk"""
        np.save(str(self.path / "ids.npy"), np.array(self.ids))
        np.save(str(self.path / "vectors.npy"), self.vectors)

    def search(self, query_vector: List[float], k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for top-k similar vectors using Cosine Similarity.
        Returns list of (id, score).
        """
        if self.vectors.shape[0] == 0:
            return []

        q = np.array(query_vector, dtype=np.float32)

        # Cosine Similarity: (A . B) / (||A|| * ||B||)
        # Normalize query
        norm_q = np.linalg.norm(q)
        if norm_q == 0:
            return []
        q = q / norm_q

        # Normalize database vectors (Ideally cache these norms)
        # For MVP we compute on fly or assume stored vectors are raw
        # Let's compute dot product against normalized vectors

        # Normalize rows
        norms = np.linalg.norm(self.vectors, axis=1)
        norms[norms == 0] = 1 # Avoid div by zero
        normalized_vectors = self.vectors / norms[:, np.newaxis]

        # Dot product
        scores = np.dot(normalized_vectors, q)

        # Get top k
        # argsort returns indices of sorted array (ascending)
        # We want descending (highest score first)
        top_k_indices = np.argsort(scores)[-k:][::-1]

        results = []
        for idx in top_k_indices:
            results.append((self.ids[idx], float(scores[idx])))

        return results

class VectorStorageEngine:
    """Engine managing vector indexes"""

    def __init__(self, db_path: str):
        self.base_path = Path(db_path) / "vectors"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.indexes: Dict[str, VectorIndex] = {}

    def create_index(self, name: str, dimension: int) -> VectorIndex:
        """Create a vector index"""
        idx_path = self.base_path / name
        index = VectorIndex(name, dimension, idx_path)
        self.indexes[name] = index
        return index

    def get_index(self, name: str) -> Optional[VectorIndex]:
        """Get existing index"""
        if name in self.indexes:
            return self.indexes[name]

        # Try loading
        idx_path = self.base_path / name
        if idx_path.exists():
            # We need dimension to load (or infer from file).
            # Let's try loading vectors file shape if exists
            vec_file = idx_path / "vectors.npy"
            if vec_file.exists():
                try:
                    vecs = np.load(str(vec_file))
                    dim = vecs.shape[1] if vecs.ndim > 1 else 0
                    # Handle empty case
                    if dim == 0: dim = 128 # Default? Or fail.
                    return self.create_index(name, dim)
                except:
                    pass
        return None
