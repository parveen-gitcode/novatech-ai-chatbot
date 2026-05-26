# ⚡ NovaTech GenAI Assistant — RAG-Powered Chatbot

A production-grade AI chat assistant built with **FastAPI**, **Gemini AI**,
**Sentence Transformers**, and **RAG (Retrieval-Augmented Generation)**.

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                         │
│                    (frontend/index.html)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ POST /api/chat
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                          │
│                                                             │
│   ┌─────────────┐     ┌──────────────┐    ┌─────────────┐  │
│   │  routes/    │────▶│  services/   │───▶│  prompts/   │  │
│   │  chat.py    │     │  rag.py      │    │ templates.py│  │
│   └─────────────┘     └──────┬───────┘    └─────────────┘  │
│                              │                             │
│              ┌───────────────┼───────────────┐             │
│              ▼               ▼               ▼             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│   │ embeddings.py│  │ retrieval.py │  │    llm.py    │    │
│   │(SentenceT.)  │  │(Cosine Sim.) │  │  (Gemini AI) │    │
│   └──────┬───────┘  └──────┬───────┘  └──────────────┘    │
│          │                 │                               │
│          ▼                 ▼                               │
│   ┌─────────────────────────────┐  ┌──────────────────┐   │
│   │     vectorstore/store.py    │  │  vectorstore/    │   │
│   │    (In-Memory Vector DB)    │  │ session_store.py │   │
│   └─────────────────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 RAG Workflow Explanation

### Indexing Phase (runs once on startup)
```
docs.json
    │
    ▼
Load Documents
    │
    ▼
Chunk Text (400 chars per chunk)
    │
    ▼
Generate Embeddings (all-MiniLM-L6-v2)
    │
    ▼
Store in VectorStore (In-Memory)
```

### Query Phase (runs on every user message)
```
User Question
    │
    ▼
Generate Query Embedding
    │
    ▼
Cosine Similarity Search (vs all stored chunks)
    │
    ▼
Filter by Threshold (≥ 0.40)
    │
    ▼
Retrieve Top-3 Chunks
    │
    ▼
Build RAG Prompt (Context + History + Question)
    │
    ▼
Send to Gemini AI (temperature=0.2)
    │
    ▼
Return Grounded Response to User
```

---

## 🧠 Embedding Strategy

| Property        | Detail                          |
|-----------------|---------------------------------|
| Model           | `all-MiniLM-L6-v2`              |
| Library         | `sentence-transformers`         |
| Vector Size     | 384 dimensions                  |
| Normalization   | L2 normalized (unit vectors)    |
| Cost            | Free — runs locally, no API key |
| Speed           | ~50ms per embedding             |

**Why this model?**
- Lightweight and fast
- Excellent semantic understanding
- No API key or cost required
- Industry standard for RAG pipelines

---

## 📐 Similarity Search Explanation

**Method used:** Cosine Similarity

```
cosine_similarity = (A · B) / (|A| × |B|)

Score range:
  0.0  →  Completely unrelated
  0.5  →  Somewhat related
  1.0  →  Identical meaning
```

**Threshold:** `0.40` (configurable in `.env`)

**Top-K:** `3` chunks retrieved per query

**Why Cosine Similarity?**
- Works well with normalized embeddings
- Not affected by document length
- Industry standard for semantic search

---

## 💡 Prompt Design Reasoning

```
You are a helpful and professional customer support assistant for NovaTech.

Use ONLY the provided context below to answer the user's question.
If the context does not contain enough information, say:
"I could not find enough information in the knowledge base."

Context:
{retrieved_chunks}

Conversation History:
{last_5_pairs}

Question:
{user_message}

Answer:
```

**Design decisions:**
| Choice | Reason |
|--------|--------|
| "Use ONLY the context" | Prevents hallucination |
| temperature = 0.2 | Factual, consistent answers |
| Include history | Supports follow-up questions |
| Fallback instruction | Honest response when unsure |
| Source labels in context | Traceability of answers |

---

## 📁 Project Structure

```
project/
│
├── app/
│   ├── routes/
│   │   └── chat.py           # API endpoints
│   ├── services/
│   │   ├── embeddings.py     # Embedding generation + indexing
│   │   ├── retrieval.py      # Cosine similarity search
│   │   ├── rag.py            # RAG pipeline orchestration
│   │   └── llm.py            # Gemini AI integration
│   ├── models/
│   │   └── schemas.py        # Pydantic request/response models
│   ├── vectorstore/
│   │   ├── store.py          # In-memory vector store
│   │   └── session_store.py  # Conversation history store
│   ├── prompts/
│   │   └── templates.py      # RAG prompt templates
│   ├── utils/
│   │   └── helpers.py        # Chunking, logging, formatting
│   └── main.py               # FastAPI app entry point
│
├── frontend/
│   ├── index.html            # Chat UI
│   ├── styles.css            # Styling
│   └── app.js                # Frontend logic
│
├── docs.json                 # Knowledge base documents
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── README.md                 # This file
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/novatech-rag-chatbot.git
cd novatech-rag-chatbot
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
SIMILARITY_THRESHOLD=0.40
TOP_K=3
```
> Get your free key at: https://aistudio.google.com/app/apikey

### 5. Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Open the app
```
http://localhost:8000
```

---

## 🔌 API Reference

### `POST /api/chat`
```json
// Request
{
  "sessionId": "session_abc123",
  "message": "How do I reset my password?"
}

// Response
{
  "reply": "To reset your password, go to the login page...",
  "tokensUsed": 215,
  "retrievedChunks": 3
}
```

### `GET /health`
```json
{
  "status": "healthy",
  "message": "NovaTech GenAI Assistant is running."
}
```

### `DELETE /api/session/{sessionId}`
```json
{
  "message": "Session 'session_abc123' cleared successfully."
}
```

---

## 🧪 Testing the RAG System

### ✅ Valid questions (should retrieve context)
```
How do I reset my password?
What are the pricing plans?
How do I invite team members?
Is my data encrypted?
How do I get an API key?
```

### ❌ Out-of-scope questions (should return fallback)
```
What is the weather today?
Who is the CEO of Apple?
What is quantum computing?
```

---

## 🚀 Deployment

### Deploy on Render (Free)
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Click **New Web Service**
4. Connect your GitHub repository
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
7. Add environment variable: `GEMINI_API_KEY`
8. Click **Deploy**

### Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click **New Project → Deploy from GitHub**
3. Select your repository
4. Add `GEMINI_API_KEY` in environment variables
5. Railway auto-detects FastAPI and deploys

---

## 📊 Evaluation Coverage

| Criteria               | Weight | Implementation                        |
|------------------------|--------|---------------------------------------|
| RAG Architecture       | 30%    | Full pipeline in `rag.py`             |
| Embedding & Similarity | 25%    | `embeddings.py` + `retrieval.py`      |
| LLM Integration        | 20%    | Gemini in `llm.py` with error handling|
| Prompt Design          | 10%    | Structured prompt in `templates.py`   |
| Frontend UI            | 5%     | Complete chat UI in `frontend/`       |
| Code Quality           | 10%    | Modular structure + logging           |

---

## 🛠️ Tech Stack

| Layer      | Technology                  |
|------------|-----------------------------|
| Backend    | FastAPI + Uvicorn           |
| LLM        | Google Gemini 1.5 Flash     |
| Embeddings | Sentence Transformers       |
| Similarity | Cosine Similarity (sklearn) |
| Storage    | In-Memory (VectorStore)     |
| Frontend   | HTML + CSS + JavaScript     |
| Env Config | python-dotenv               |