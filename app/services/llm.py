import os
import google.generativeai as genai
from google.api_core.exceptions import (
    InvalidArgument,
    PermissionDenied,
    ResourceExhausted,
    DeadlineExceeded,
    ServiceUnavailable
)
from app.utils.helpers import logger
from dotenv import load_dotenv

load_dotenv()

# ── Configure Gemini client once at startup ───────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY is missing. Please set it in your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# ── Model config ──────────────────────────────────────────────
GENERATION_CONFIG = genai.types.GenerationConfig(
    temperature=0.2,        # Low = more factual, less creative
    max_output_tokens=512,
)

MODEL_NAME = "gemini-2.5-flash"


def call_llm(prompt: str) -> dict:
    """
    Send the constructed RAG prompt to Gemini and return:
    {
        "reply": str,
        "tokensUsed": int
    }

    Handles all common API failure scenarios gracefully.
    """

    try:
        logger.info(f"Calling Gemini model: {MODEL_NAME}")

        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=GENERATION_CONFIG,
        )

        # ── Send prompt to Gemini ─────────────────────────────
        response = model.generate_content(prompt)

        # ── Extract reply text ────────────────────────────────
        reply_text = response.text.strip()

        # ── Log token usage if available ──────────────────────
        tokens_used = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            tokens_used = (
                response.usage_metadata.prompt_token_count +
                response.usage_metadata.candidates_token_count
            )
            logger.info(f"Tokens used: {tokens_used}")

        logger.info("Gemini response received successfully.")

        return {
            "reply": reply_text,
            "tokensUsed": tokens_used
        }

    # ── Invalid API Key ───────────────────────────────────────
    except PermissionDenied:
        logger.error("Invalid or unauthorized Gemini API key.")
        return {
            "reply": "Service error: Invalid API key. Please contact support.",
            "tokensUsed": 0
        }

    # ── Bad request / invalid input ───────────────────────────
    except InvalidArgument as e:
        logger.error(f"Invalid argument sent to Gemini: {e}")
        return {
            "reply": "Service error: Invalid request format.",
            "tokensUsed": 0
        }

    # ── Rate limit exceeded ───────────────────────────────────
    except ResourceExhausted:
        logger.error("Gemini API rate limit exceeded.")
        return {
            "reply": "Service is currently busy. Please try again in a moment.",
            "tokensUsed": 0
        }

    # ── Request timeout ───────────────────────────────────────
    except DeadlineExceeded:
        logger.error("Gemini API request timed out.")
        return {
            "reply": "Request timed out. Please try again.",
            "tokensUsed": 0
        }

    # ── Service unavailable ───────────────────────────────────
    except ServiceUnavailable:
        logger.error("Gemini API service is temporarily unavailable.")
        return {
            "reply": "Service temporarily unavailable. Please try again later.",
            "tokensUsed": 0
        }

    # ── Catch-all for unexpected errors ───────────────────────
    except Exception as e:
        logger.error(f"Unexpected error during LLM call: {e}")
        return {
            "reply": "An unexpected error occurred. Please try again.",
            "tokensUsed": 0
        }