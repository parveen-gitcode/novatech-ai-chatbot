import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.vectorstore.store import vector_store
from app.services.embeddings import get_embedding
from app.utils.helpers import log_similarity_scores, logger
import os

# ── Config ────────────────────────────────────────────────────
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.40))
TOP_K = int(os.getenv("TOP_K", 3))


def retrieve_relevant_chunks(user_query: str) -> list[dict]:
    """
    1. Generate embedding for the user query
    2. Compare against all stored chunk embeddings using cosine similarity
    3. Filter by threshold
    4. Return Top-K most relevant chunks
    """

    if vector_store.is_empty():
        logger.error("VectorStore is empty. Documents may not be indexed.")
        return []

    # ── Step 1: Embed the user query ──────────────────────────
    logger.info(f"Generating query embedding for: '{user_query}'")
    query_embedding = get_embedding(user_query)
    query_vector = np.array(query_embedding).reshape(1, -1)

    # ── Step 2: Compare with all stored embeddings ────────────
    all_chunks = vector_store.get_all()
    scored_results = []

    for chunk in all_chunks:
        doc_vector = np.array(chunk["embedding"]).reshape(1, -1)

        # Cosine similarity score between query and chunk
        score = cosine_similarity(query_vector, doc_vector)[0][0]

        scored_results.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "title": chunk["title"],
            "source": chunk["source"],
            "score": float(score)
        })

    # ── Step 3: Sort by score descending ─────────────────────
    scored_results.sort(key=lambda x: x["score"], reverse=True)

    # ── Step 4: Log all scores ────────────────────────────────
    log_similarity_scores(scored_results[:TOP_K])

    # ── Step 5: Apply similarity threshold ───────────────────
    filtered_results = [
        r for r in scored_results
        if r["score"] >= SIMILARITY_THRESHOLD
    ]

    if not filtered_results:
        logger.warning(
            f"No chunks passed threshold {SIMILARITY_THRESHOLD}. "
            f"Best score was: {scored_results[0]['score']:.4f}"
        )
        return []

    # ── Step 6: Return Top-K ──────────────────────────────────
    top_results = filtered_results[:TOP_K]
    logger.info(f"Retrieved {len(top_results)} chunk(s) above threshold.")
    return top_results


def build_context_from_chunks(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a readable context string
    to be injected into the LLM prompt.
    """
    if not chunks:
        return ""

    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Source {i+1}: {chunk['title']}]\n{chunk['text']}"
        )

    return "\n\n".join(context_parts)