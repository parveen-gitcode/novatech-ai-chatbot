import json
from sentence_transformers import SentenceTransformer
from app.vectorstore.store import vector_store
from app.utils.helpers import chunk_text, logger

# ── Load embedding model once at startup ─────────────────────
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector for a given text."""
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def load_and_index_documents(docs_path: str = "docs.json") -> None:
    """
    Load documents from docs.json, chunk them,
    generate embeddings, and store in the vector store.
    """
    if not vector_store.is_empty():
        logger.info("VectorStore already populated. Skipping indexing.")
        return

    logger.info(f"Loading documents from {docs_path} ...")

    with open(docs_path, "r") as f:
        documents = json.load(f)

    total_chunks = 0

    for doc_index, doc in enumerate(documents):
        title = doc.get("title", f"Document_{doc_index}")
        content = doc.get("content", "")

        if not content.strip():
            logger.warning(f"Skipping empty document: {title}")
            continue

        # ── Chunk the document ────────────────────────────────
        chunks = chunk_text(content, chunk_size=400)

        for chunk_index, chunk in enumerate(chunks):
            chunk_id = f"doc{doc_index}_chunk{chunk_index}"

            # ── Generate embedding ────────────────────────────
            embedding = get_embedding(chunk)

            # ── Store in vector store ─────────────────────────
            vector_store.add(
                chunk_id=chunk_id,
                text=chunk,
                embedding=embedding,
                title=title,
                source=docs_path
            )

            total_chunks += 1
            logger.info(f"Indexed chunk: {chunk_id} | Title: {title}")

    logger.info(f"Indexing complete. Total chunks stored: {total_chunks}")