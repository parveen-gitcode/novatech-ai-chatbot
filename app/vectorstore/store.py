from app.utils.helpers import logger

class VectorStore:
    """
    In-memory vector store.
    Stores chunks with their embeddings and metadata.
    """

    def __init__(self):
        self._store: list[dict] = []

    def add(self, chunk_id: str, text: str, embedding: list[float], title: str, source: str):
        """Add a chunk with its embedding and metadata."""
        self._store.append({
            "chunk_id": chunk_id,
            "text": text,
            "embedding": embedding,
            "title": title,
            "source": source
        })

    def get_all(self) -> list[dict]:
        """Return all stored chunks."""
        return self._store

    def count(self) -> int:
        """Return total number of chunks stored."""
        return len(self._store)

    def clear(self):
        """Clear all stored chunks."""
        self._store = []
        logger.info("VectorStore cleared.")

    def is_empty(self) -> bool:
        return len(self._store) == 0


# ── Single global instance used across the app ──────────────
vector_store = VectorStore()