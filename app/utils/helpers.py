import uuid
import logging

# ── Logger setup ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())


def format_conversation_history(history: list[dict]) -> str:
    """
    Convert history list into a readable string for the prompt.
    Each item: {"role": "user" | "assistant", "content": "..."}
    """
    if not history:
        return "No previous conversation."

    formatted = []
    for turn in history:
        role = "User" if turn["role"] == "user" else "Assistant"
        formatted.append(f"{role}: {turn['content']}")

    return "\n".join(formatted)


def chunk_text(text: str, chunk_size: int = 400) -> list[str]:
    """
    Split text into chunks of approximately `chunk_size` characters.
    Splits on sentence boundaries where possible.
    """
    sentences = text.replace("\n", " ").split(". ")
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text]


def log_similarity_scores(results: list[dict]) -> None:
    """Log retrieved chunks and their similarity scores."""
    logger.info("=== Similarity Search Results ===")
    for i, result in enumerate(results):
        logger.info(
            f"Rank {i+1} | Score: {result['score']:.4f} | "
            f"Source: {result['title']} | "
            f"Chunk: {result['text'][:80]}..."
        )