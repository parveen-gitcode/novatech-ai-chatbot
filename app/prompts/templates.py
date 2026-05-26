def build_rag_prompt(retrieved_context: str, conversation_history: str, user_question: str) -> str:
    return f"""You are a helpful and professional customer support assistant for NovaTech.

Use ONLY the provided context below to answer the user's question.
If the context does not contain enough information, say:
"I could not find enough information in the knowledge base to answer this question."

Do NOT make up any information outside the provided context.

Context:
{retrieved_context}

Conversation History:
{conversation_history}

Question:
{user_question}

Answer:"""


def build_fallback_response() -> str:
    return "I could not find enough information in the knowledge base to answer this question."