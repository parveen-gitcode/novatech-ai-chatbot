import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routes.chat import router
from app.services.embeddings import load_and_index_documents
from app.utils.helpers import logger

# ── Load environment variables ────────────────────────────────
load_dotenv()


# ── Lifespan: runs on startup & shutdown ──────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup:  Load and index all documents into vector store.
    Shutdown: Log graceful shutdown.
    """
    logger.info("═══════════════════════════════════════")
    logger.info("   NovaTech GenAI Assistant Starting   ")
    logger.info("═══════════════════════════════════════")

    # ── Index documents on startup ────────────────────────────
    docs_path = os.getenv("DOCS_PATH", "docs.json")
    try:
        load_and_index_documents(docs_path=docs_path)
        logger.info("✅ Document indexing complete.")
    except FileNotFoundError:
        logger.error(f"❌ docs.json not found at path: {docs_path}")
    except Exception as e:
        logger.error(f"❌ Error during document indexing: {e}")

    logger.info("🚀 Server is ready to accept requests.")
    logger.info("═══════════════════════════════════════")

    yield  # App runs here

    # ── Shutdown ──────────────────────────────────────────────
    logger.info("NovaTech GenAI Assistant shutting down gracefully.")


# ── Create FastAPI app ────────────────────────────────────────
app = FastAPI(
    title="NovaTech GenAI Assistant",
    description="Production-grade RAG-powered chatbot for NovaTech customer support.",
    version="1.0.0",
    lifespan=lifespan
)


# ── CORS Middleware ───────────────────────────────────────────
# Allows frontend (HTML/JS) to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # In production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Include API routes ────────────────────────────────────────
app.include_router(router)


# ── Serve Frontend Static Files ───────────────────────────────
# Serves CSS and JS from the frontend folder
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.exists(frontend_path):
    app.mount(
        "/static",
        StaticFiles(directory=frontend_path),
        name="static"
    )

    @app.get("/")
    async def serve_frontend():
        """Serve the main chat UI."""
        index_path = os.path.join(frontend_path, "index.html")
        return FileResponse(index_path)
else:
    logger.warning("Frontend directory not found. UI will not be served.")

    @app.get("/")
    async def root():
        return {"message": "NovaTech GenAI Assistant API is running."}


# ── Global Exception Handler ──────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch any unhandled exceptions and return clean error response."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected server error occurred."}
    )


# ── Run directly with: python -m app.main ────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )