from app.services.retrieval import retrieve_relevant_chunks, build_context_from_chunks
from app.services.llm import call_llm
from app.prompts.templates import build_rag_prompt, build_fallback_response
from app.utils.helpers import format_conversation_history, logger


def run_rag_pipeline(user_message: str, history: list[dict]) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks
    2. Build context
    3. Build prompt
    4. Call LLM
    5. Return reply + metadata
    """

    # ── Step 1: Retrieve relevant chunks ─────────────────────
    logger.info("Starting RAG pipeline...")
    retrieved_chunks = retrieve_relevant_chunks(user_message)

    # ── Step 2: Check if anything was retrieved ───────────────
    if not retrieved_chunks:
        logger.warning("No relevant chunks found. Returning fallback response.")
        return {
            "reply": build_fallback_response(),
            "tokensUsed": 0,
            "retrievedChunks": 0
        }

    # ── Step 3: Build context string ─────────────────────────
    context = build_context_from_chunks(retrieved_chunks)
    logger.info(f"Context built from {len(retrieved_chunks)} chunk(s).")

    # ── Step 4: Format conversation history ──────────────────
    formatted_history = format_conversation_history(history)

    # ── Step 5: Build the full RAG prompt ────────────────────
    prompt = build_rag_prompt(
        retrieved_context=context,
        conversation_history=formatted_history,
        user_question=user_message
    )
    logger.info("RAG prompt constructed successfully.")

    # ── Step 6: Call LLM ─────────────────────────────────────
    llm_response = call_llm(prompt)

    # ── Step 7: Return structured response ───────────────────
    return {
        "reply": llm_response.get("reply", build_fallback_response()),
        "tokensUsed": llm_response.get("tokensUsed", 0),
        "retrievedChunks": len(retrieved_chunks)
    }