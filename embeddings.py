"""
Embedding and semantic search module for Strudel patterns.
Uses local sentence-transformers for embeddings (no API key needed).
"""

import json
import pickle
from pathlib import Path
import numpy as np


def get_embedding_model():
    """Get the sentence-transformer model for embeddings."""
    from sentence_transformers import SentenceTransformer
    # all-mpnet-base-v2 is more powerful for semantic understanding
    return SentenceTransformer('all-mpnet-base-v2')


def create_pattern_text(pattern: dict) -> str:
    """
    Create a rich text representation of a pattern for embedding.
    Combines all the metadata into a searchable text.
    """
    parts = [
        pattern["name"],
        pattern["description"],
        f"mood: {pattern['mood']}",
        f"tempo: {pattern['tempo']}",
        f"tags: {', '.join(pattern['tags'])}",
    ]
    return " | ".join(parts)


def compute_embeddings(patterns: list[dict], model=None) -> np.ndarray:
    """
    Compute embeddings for a list of patterns using sentence-transformers.

    Args:
        patterns: List of pattern dictionaries
        model: Optional pre-loaded model

    Returns:
        numpy array of embeddings (num_patterns, embedding_dim)
    """
    if model is None:
        model = get_embedding_model()

    texts = [create_pattern_text(p) for p in patterns]
    embeddings = model.encode(texts, show_progress_bar=True)
    return np.array(embeddings)


def compute_query_embedding(query: str, model=None) -> np.ndarray:
    """
    Compute embedding for a single query string.

    Args:
        query: The search query
        model: Optional pre-loaded model

    Returns:
        numpy array of shape (embedding_dim,)
    """
    if model is None:
        model = get_embedding_model()

    return np.array(model.encode(query))


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between vectors.

    Args:
        a: Query vector of shape (embedding_dim,)
        b: Matrix of vectors of shape (num_vectors, embedding_dim)

    Returns:
        Array of similarities of shape (num_vectors,)
    """
    a_norm = a / np.linalg.norm(a)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(b_norm, a_norm)


class PatternSearcher:
    """
    Semantic search over Strudel patterns using embeddings.
    """

    def __init__(
        self,
        patterns_path: str = "patterns.json",
        cache_path: str = "embeddings_cache.pkl"
    ):
        self.patterns_path = Path(patterns_path)
        self.cache_path = Path(cache_path)
        self.patterns = []
        self.embeddings = None
        self.model = None
        self._load_patterns()

    def _load_patterns(self):
        """Load patterns from JSON file."""
        with open(self.patterns_path) as f:
            data = json.load(f)
        self.patterns = data["patterns"]

    def _load_cache(self) -> bool:
        """Try to load embeddings from cache. Returns True if successful."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "rb") as f:
                    cache = pickle.load(f)
                # Verify cache is for same patterns
                if cache.get("pattern_ids") == [p["id"] for p in self.patterns]:
                    self.embeddings = cache["embeddings"]
                    return True
            except Exception:
                pass
        return False

    def _save_cache(self):
        """Save embeddings to cache."""
        cache = {
            "pattern_ids": [p["id"] for p in self.patterns],
            "embeddings": self.embeddings
        }
        with open(self.cache_path, "wb") as f:
            pickle.dump(cache, f)

    def _ensure_model(self):
        """Lazy load the embedding model."""
        if self.model is None:
            print("Loading embedding model...")
            self.model = get_embedding_model()

    def build_index(self, force: bool = False):
        """
        Build the embedding index for all patterns.

        Args:
            force: If True, recompute even if cache exists
        """
        if not force and self._load_cache():
            print(f"Loaded {len(self.patterns)} pattern embeddings from cache")
            return

        self._ensure_model()
        print(f"Computing embeddings for {len(self.patterns)} patterns...")
        self.embeddings = compute_embeddings(self.patterns, self.model)
        self._save_cache()
        print(f"Embeddings computed and cached")

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> list[tuple[dict, float]]:
        """
        Search for patterns similar to the query.

        Args:
            query: Natural language search query
            top_k: Number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of (pattern, score) tuples, sorted by similarity
        """
        if self.embeddings is None:
            self.build_index()

        self._ensure_model()
        query_embedding = compute_query_embedding(query, self.model)
        similarities = cosine_similarity(query_embedding, self.embeddings)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score >= min_score:
                results.append((self.patterns[idx], float(score)))

        return results

    def get_similar_patterns(
        self,
        pattern_id: str,
        top_k: int = 5
    ) -> list[tuple[dict, float]]:
        """
        Find patterns similar to a given pattern.

        Args:
            pattern_id: ID of the pattern to find similar ones for
            top_k: Number of results to return

        Returns:
            List of (pattern, score) tuples
        """
        if self.embeddings is None:
            self.build_index()

        # Find the pattern index
        idx = None
        for i, p in enumerate(self.patterns):
            if p["id"] == pattern_id:
                idx = i
                break

        if idx is None:
            raise ValueError(f"Pattern '{pattern_id}' not found")

        pattern_embedding = self.embeddings[idx]
        similarities = cosine_similarity(pattern_embedding, self.embeddings)

        # Get top-k indices (excluding the pattern itself)
        top_indices = np.argsort(similarities)[::-1][1:top_k+1]

        results = []
        for i in top_indices:
            results.append((self.patterns[i], float(similarities[i])))

        return results


def demo():
    """Demo the semantic search functionality."""
    searcher = PatternSearcher()
    searcher.build_index()

    queries = [
        "something groovy and hypnotic",
        "dark ambient horror",
        "happy upbeat dance music",
        "relaxing meditation",
        "aggressive industrial",
    ]

    print("\n" + "="*60)
    print("SEMANTIC SEARCH DEMO")
    print("="*60)

    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 40)
        results = searcher.search(query, top_k=3)
        for pattern, score in results:
            print(f"  [{score:.3f}] {pattern['name']}")
            print(f"           {pattern['description'][:60]}...")


if __name__ == "__main__":
    demo()
