# 🤖 AI Document Support

A full-stack RAG (Retrieval-Augmented Generation) application that lets users upload documents (PDF, DOCX, TXT) and have intelligent conversations with them — powered by OpenRouter LLMs and vector embeddings.

---

## ✨ Use Case

Ever needed to quickly understand a long research paper, contract, or book without reading it cover to cover? This application lets you:

- Upload any document (PDF / DOCX / TXT)
- Ask natural-language questions about its content
- Get precise, context-aware AI answers — backed only by your document

Each user's documents are completely isolated from other users, ensuring privacy by design.

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| **RAG Pipeline** | Answers are grounded in your actual document using vector similarity search — not hallucinated |
| **Async Embedding Generation** | After upload, chunking & embedding happens via FastAPI `BackgroundTasks` — upload returns instantly, processing happens asynchronously |
| **Simulated Streaming Response** | LLM answers are rendered word-by-word in the frontend for a natural, ChatGPT-like experience |
| **User Isolation** | Documents are linked to users via `email` as a foreign key — no cross-user data leakage |
| **Persistent Sessions** | JWT token stored in browser cookies — stay logged in for 7 days across page refreshes |
| **Document Management** | Upload, browse, select for chat, and fully delete documents (cascades: metadata → chunks → embeddings → physical file) |
| **Back-Navigation** | Seamlessly switch between documents without a full page reload |

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|---|---|
| **Framework** | FastAPI (async) |
| **Database** | PostgreSQL + pgvector extension |
| **ORM** | SQLAlchemy (async) |
| **Embeddings** | OpenRouter Embedding API (via LangChain OpenAI client) |
| **LLM** | OpenRouter (OpenAI-compatible API) |
| **Text Splitting** | LangChain `RecursiveCharacterTextSplitter` |
| **Auth** | JWT Bearer tokens |

### Frontend
| Layer | Technology |
|---|---|
| **Framework** | Streamlit |
| **Auth Storage** | `streamlit-cookies-controller` (7-day persistent sessions) |
| **HTTP Client** | `requests` |
| **Architecture** | Dependency Injection (Container → Service → API) |

---

## 📐 Architecture

```
┌─────────────────────────────────────────┐
│              Streamlit Frontend          │
│  Auth (Login/Signup) → Chat (RAG UI)    │
│  SessionManager ← CookieController      │
└────────────────┬────────────────────────┘
                 │ HTTP (JWT Bearer)
┌────────────────▼────────────────────────┐
│              FastAPI Backend             │
│  /auth  /documents  /chunking  /chat    │
├─────────────────────────────────────────┤
│  DocumentService   GenerationService    │
│  EmbeddingService  RetrievalService     │
├─────────────────────────────────────────┤
│         SQLAlchemy Async ORM            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│           PostgreSQL + pgvector          │
│  users   documents_metadata             │
│  documents_chunks  document_embeddings  │
└─────────────────────────────────────────┘
```

### RAG Pipeline (per question)
```
Question → Embed query → Vector similarity search
        → Retrieve top-K chunks → Build prompt
        → LLM (OpenRouter) → Stream answer to UI
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.12+
- PostgreSQL with `pgvector` extension enabled
- An [OpenRouter](https://openrouter.ai) API key

### 1. Clone the repository
```bash
git clone https://github.com/Kunal152000/Ai_customer_support.git
cd Ai_customer_support
```

### 2. Backend setup
```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ai_support
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
SECRET_KEY=your-secret-key
TOP_K=5
```

Run the backend:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend setup
```bash
cd frontend
pip install -r requirements.txt
```

Create a `.env` file in `frontend/`:
```env
BACKEND_URL=http://localhost:8000
```

Run the frontend:
```bash
streamlit run app.py
```

### 4. Database setup
Run the following SQL in your PostgreSQL instance (pgAdmin or psql):
```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Tables are auto-created by SQLAlchemy on startup via Base.metadata.create_all()
-- Add the email foreign key to documents_metadata if not already present:
ALTER TABLE documents_metadata ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE documents_metadata
  ADD CONSTRAINT IF NOT EXISTS fk_user_email
  FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE;
```

---

## 📁 Project Structure

```
AI_support/
├── backend/
│   └── app/
│       ├── auth/          # JWT auth, user model, login/register
│       ├── documents/     # Upload, metadata, deletion
│       ├── chunking/      # Text splitting + async processing
│       ├── embeddings/    # Vector generation + storage
│       ├── retrieval/     # Similarity search
│       └── generation/    # Prompt building + LLM call
└── frontend/
    ├── auth/              # Login/signup views, API, service
    ├── chat/              # Document picker, chat UI, streaming
    ├── config/            # Session manager (cookie-backed)
    ├── core/              # DI Container
    └── utils/             # HTTP client wrapper
```

---

## 📝 Notes

- Documents already uploaded before the background-embedding fix need to be **re-uploaded** to generate embeddings
- The system is designed for **personal/team use** — for production scale, consider Celery + Redis for the embedding pipeline and a proper secrets manager
