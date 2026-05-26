from pydantic import BaseModel, field_validator
from typing import Optional

class ChatRequest(BaseModel):
    sessionId: str
    message: str

    @field_validator("message")
    @classmethod
    def message_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Message field is required and cannot be empty")
        return v.strip()

    @field_validator("sessionId")
    @classmethod
    def session_id_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("sessionId is required")
        return v.strip()


class ChatResponse(BaseModel):
    reply: str
    tokensUsed: Optional[int] = 0
    retrievedChunks: int


class HealthResponse(BaseModel):
    status: str
    message: str


class ErrorResponse(BaseModel):
    error: str