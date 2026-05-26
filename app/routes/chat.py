from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.models.schemas import ChatRequest, ChatResponse, HealthResponse
from app.services.rag import run_rag_pipeline
from app.vectorstore.session_store import session_store
from app.utils.helpers import logger

router = APIRouter()


# ── Health Check Endpoint ─────────────────────────────────────
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    GET /health
    Returns service health status.
    """
    return HealthResponse(
        status="healthy",
        message="NovaTech GenAI Assistant is running."
    )


# ── Chat Endpoint ─────────────────────────────────────────────
@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: Request):
    """
    POST /api/chat
    Accepts user message + sessionId.
    Runs full RAG pipeline and returns grounded reply.
    """

    # ── Step 1: Parse and validate request body ───────────────
    try:
        body = await request.json()
    except Exception:
        logger.error("Invalid JSON received.")
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid JSON format in request body."}
        )

    # ── Step 2: Validate with Pydantic schema ─────────────────
    try:
        chat_request = ChatRequest(**body)
    except ValidationError as e:
        errors = e.errors()
        first_error = errors[0]["msg"] if errors else "Validation error"
        logger.error(f"Validation error: {first_error}")
        raise HTTPException(
            status_code=422,
            detail={"error": first_error}
        )

    session_id = chat_request.sessionId
    user_message = chat_request.message

    logger.info(f"Received message | Session: {session_id} | Message: '{user_message}'")

    # ── Step 3: Get conversation history for this session ─────
    history = session_store.get_history(session_id)

    # ── Step 4: Run RAG pipeline ──────────────────────────────
    try:
        result = run_rag_pipeline(
            user_message=user_message,
            history=history
        )
    except Exception as e:
        logger.error(f"RAG pipeline error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error during RAG processing."}
        )

    # ── Step 5: Save messages to session history ──────────────
    session_store.add_message(session_id, role="user", content=user_message)
    session_store.add_message(session_id, role="assistant", content=result["reply"])

    logger.info(
        f"Response sent | Session: {session_id} | "
        f"Chunks: {result['retrievedChunks']} | "
        f"Tokens: {result['tokensUsed']}"
    )

    # ── Step 6: Return structured response ────────────────────
    return ChatResponse(
        reply=result["reply"],
        tokensUsed=result["tokensUsed"],
        retrievedChunks=result["retrievedChunks"]
    )


# ── Clear Session Endpoint (Bonus) ────────────────────────────
@router.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """
    DELETE /api/session/{sessionId}
    Clears conversation history for a session.
    """
    if not session_store.session_exists(session_id):
        raise HTTPException(
            status_code=404,
            detail={"error": f"Session '{session_id}' not found."}
        )

    session_store.clear_session(session_id)
    return JSONResponse(
        content={"message": f"Session '{session_id}' cleared successfully."}
    )