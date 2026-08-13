# Backend Code Flow — AI Support API

> **Stack:** FastAPI · SQLAlchemy (async) · PostgreSQL + pgvector · OpenRouter (LLM + Embeddings)  
> **Entry point:** `backend/app/main.py`

---

## 1. Application Bootstrap

```
python -m uvicorn app.main:app
        │
        ├─ FastAPI app created with lifespan hook
        │         └─ lifespan()  →  await init_db()
        │                              └─ Creates all SQLAlchemy tables
        │                                 (users, documents_metadata, documents_chunks, document_embeddings)
        │
        └─ Routers registered:
              /health   → health_router
              /auth     → auth_router
              /documents → document_router
              /chunking  → chunk_router
              /retrieval → retrieval_router
              /chat      → response_router (generation)
```

---

## 2. Health Check APIs

### `GET /health/`
```
Request → health_check()
        └─ Returns { status: "healthy", service: "AI Support Backend" }
```

### `GET /health/ready`
```
Request → ready_check()
        └─ Depends(get_db)  →  db.connection()
              ├─ Success → { status: "ready", database: "connected" }
              └─ Failure → { status: "not_ready", database: "disconnected", error: <msg> }
```

---

## 3. Auth APIs

### `POST /auth/register`

```
Request Body: { name, email, password }
        │
        ▼
router.register()
        │
        ├─ Depends(get_db)            →  async PostgreSQL session
        │
        └─ AuthService(db)
                │
                ├─ repository.get_by_email(email)
                │       └─ SELECT * FROM users WHERE email = ?
                │               ├─ Found   → raise ValueError("Email already exists")
                │               └─ Not found → continue
                │
                └─ repository.create(name, email, hash_password(password))
                        ├─ security.hash_password()  →  PasswordHash.hash(password)  [pwdlib]
                        ├─ INSERT INTO users ...
                        ├─ db.commit() + db.refresh()
                        └─ Returns User ORM object
                                │
                                ▼
                    UserResponse { id, name, email }   →  HTTP 200
```

### `POST /auth/login`

```
Request: OAuth2PasswordRequestForm (username=email, password)
        │
        ▼
router.login()
        │
        ├─ Depends(get_db)
        │
        └─ AuthService(db)
                │
                ├─ repository.get_by_email(email)
                │       └─ SELECT * FROM users WHERE email = ?
                │               └─ Not found / wrong password → raise ValueError("Invalid email or password")
                │
                ├─ security.verify_password(plain, hashed)  →  PasswordHash.verify()
                │
                └─ jwt.create_access_token(user.id)
                        ├─ Payload: { sub: user_id, exp: now + ACCESS_TOKEN_EXPIRE_MINUTES }
                        ├─ jwt.encode(payload, SECRET_KEY, ALGORITHM)
                        └─ Returns JWT string
                                │
                                ▼
                    TokenResponse { access_token, token_type: "bearer" }  →  HTTP 200
```

---

## 4. Auth Guard (used by all protected endpoints)

Every protected router declares `dependencies=[Depends(get_current_user)]`.

```
Incoming Request with  Authorization: Bearer <token>
        │
        ▼
dependencies.get_current_user()
        │
        ├─ oauth2_scheme  →  extracts Bearer token from header
        │
        ├─ jwt.decode_access_token(token)
        │       ├─ jose.jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        │       │       └─ Expired / invalid  →  return None
        │       └─ Returns payload dict { sub: user_id, exp: ... }
        │
        ├─ payload is None or payload["sub"] is None  →  HTTP 401
        │
        └─ UserRepository.get_by_id(user_id)
                ├─ db.get(User, user_id)
                ├─ Not found  →  HTTP 401
                └─ Found      →  returns User object (injected into route handler)
```

---

## 5. Document Upload API

### `POST /documents/upload`

```
Request: multipart/form-data  (owner_name: str, file: UploadFile)
  + Authorization: Bearer <token>
        │
        ▼
router.upload_document()
        │
        ├─ Depends(get_current_user)   →  validates JWT (see §4)
        ├─ Depends(get_db)
        │
        └─ DocumentService(db)
                │
                ├─ Validate filename  →  HTTP 400 if missing
                │
                ├─ Derive extension (.pdf / .docx / .txt / etc.)
                ├─ Generate stored_filename = uuid4() + extension
                ├─ Read file bytes  →  compute file_size
                │
                ├─ LocalStorageService.save(file, stored_filename)
                │       └─ Writes bytes to  backend/storage/<stored_filename>
                │               Returns storage_location path string
                │
                ├─ _get_document_type(extension)
                │       └─ Maps extension to DocumentType enum
                │               (PDF / DOCX / DOC / TXT / CSV / XLSX / URL)
                │
                ├─ Build DocumentMetadata ORM object
                │       { owner_name, original_filename, stored_filename,
                │         storage_location, document_type, file_size,
                │         status=UPLOADED, version=1, title=None }
                │
                └─ DocumentRepository.create_document(document)
                        ├─ db.add(), db.commit(), db.refresh()
                        └─ Returns persisted DocumentMetadata
                                │
                                ▼
                    DocumentResponse { id, owner_name, original_filename,
                      stored_filename, storage_location, document_type,
                      file_size, status, version, title,
                      created_at, updated_at }   →  HTTP 200
```

---

## 6. Document Processing (Chunking) API

### `POST /chunking/{document_id}/process`

```
Request: Path param document_id (UUID)
  + Authorization: Bearer <token>
        │
        ▼
router.process_document()
        │
        ├─ Depends(get_current_user)
        ├─ Depends(get_db)
        │
        └─ ProcessingService(db)
                │
                ├─ DocumentRepository.get_document(document_id)
                │       └─ SELECT * FROM documents_metadata WHERE id = ?
                │               └─ Not found  →  ValueError → HTTP 404
                │
                ├─ LocalStorageService.read(storage_location)
                │       └─ Returns Path object of stored file
                │
                ├─ ParserFactory.get_parser(path)
                │       ├─ .pdf   →  PdfParser
                │       │               └─ pymupdf.open()  →  page.get_text() for each page
                │       ├─ .docx  →  DocxParser
                │       │               └─ python-docx paragraph extraction
                │       └─ .txt   →  TxtParser
                │                       └─ plain text read
                │
                ├─ parser.parse(path)  →  full text string
                │
                ├─ RecursiveChunker.chunk(text)
                │       └─ LangChain RecursiveCharacterTextSplitter
                │               chunk_size=1000, chunk_overlap=200
                │               Returns list[str]
                │
                └─ ChunkService.save_chunks(document_id, chunks)
                        │
                        ├─ Build list of DocumentChunk ORM objects
                        │       { document_id, chunk_index, chunk_text, word_count }
                        │
                        └─ ChunkRepository.create_many(chunk_models)
                                ├─ db.add_all(chunks)
                                ├─ db.commit()
                                └─ Returns count of chunks saved
                                        │
                                        ▼
                            { message: "Document processed successfully",
                              chunks_saved: <N> }  →  HTTP 200
```

---

## 7. Retrieval API

### `POST /retrieval`

```
Request Body: { question: str }
  + Authorization: Bearer <token>
        │
        ▼
router.retrieve_context()
        │
        ├─ Depends(get_current_user)
        ├─ Depends(get_db)
        │
        └─ RetrievalService(db)
                │
                ├─ Construct OpenRouterEmbeddingProvider
                │       └─ LangChain OpenAIEmbeddings(model, api_key, base_url=OpenRouter)
                │
                ├─ EmbeddingService.generate_query_embedding(question)
                │       └─ provider.embed([question])
                │               └─ OpenRouter API call  →  vector: list[float]
                │
                ├─ DocumentEmbeddingRepository.find_similar_embeddings(query_vector, limit=TOP_K)
                │       └─ SELECT ... FROM document_embeddings
                │            ORDER BY embedding <=> query_vector   (cosine distance, pgvector)
                │            LIMIT TOP_K
                │               Returns list[DocumentEmbedding]
                │
                ├─ Extract chunk_ids from embeddings
                │
                ├─ ChunkRepository.get_chunks_by_ids(chunk_ids)
                │       └─ SELECT * FROM documents_chunks WHERE id IN (...)
                │               Returns list[DocumentChunk]
                │
                └─ Build results list
                        [{ chunk_id: str, text: chunk_text }, ...]
                                │
                                ▼
                    RetrievalResponse { chunks: [{ chunk_id, text }, ...] }  →  HTTP 200
```

---

## 8. Chat / Generation API

### `POST /chat`

```
Request Body: { question: str }
  + Authorization: Bearer <token>
        │
        ▼
router.generate_response()
        │
        ├─ Depends(get_current_user)
        ├─ Depends(get_db)
        │
        └─ GenerationService(db)
                │
                ├─ Step 1 — Retrieval (same as §7)
                │       RetrievalService.retrieve(question)
                │       Returns [{ chunk_id, text }, ...]
                │
                ├─ Step 2 — Build context string
                │       context = "\n\n".join(chunk["text"] for chunk in retrieval_response)
                │
                ├─ Step 3 — Build prompt
                │       PromptBuilder.build(question, context)
                │       └─ Template:
                │               "You are a helpful AI support assistant.
                │                Answer ONLY using the provided context.
                │                Context: {context}
                │                Question: {question}
                │                Answer:"
                │
                └─ Step 4 — LLM call
                        OpenRouterProvider.generate_response(prompt)
                        └─ AsyncOpenAI(api_key, base_url=OpenRouter)
                                .chat.completions.create(
                                    model=OPENROUTER_MODEL,
                                    messages=[{ role: "user", content: prompt }]
                                )
                                Returns response.choices[0].message.content
                                        │
                                        ▼
                            GenerationResponse { answer: str }  →  HTTP 200
```

---

## 9. Database Layer

| Table | ORM Model | Purpose |
|---|---|---|
| `users` | `auth.models.User` | Stores registered users |
| `documents_metadata` | `documents.models.DocumentMetadata` | Document records & lifecycle |
| `documents_chunks` | `chunking.models.DocumentChunk` | Text chunks per document |
| `document_embeddings` | `embeddings.models.DocumentEmbedding` | pgvector embeddings per chunk |

- **Session:** `database/session.py` provides `get_db()` as an async dependency  
- **Init:** `database/init_db.py` runs `Base.metadata.create_all()` on startup  
- **Vector search:** pgvector extension with cosine distance operator `<=>`

---

## 10. End-to-End Request Lifecycle Summary

```
Client
  │
  ├── POST /auth/register  →  Create user (hashed password)
  ├── POST /auth/login     →  Validate credentials → JWT token
  │
  ├── POST /documents/upload          →  Save file to disk + DB record
  ├── POST /chunking/{id}/process     →  Parse → Chunk → Save chunks
  │   (embeddings are generated via a separate flow / not yet in router)
  │
  ├── POST /retrieval                 →  Embed query → cosine search → top-K chunks
  └── POST /chat                      →  Retrieve + Prompt + LLM → answer string
```
