from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.init_db import init_db
from app.auth.router import auth_router
from app.auth.router import health_rotuer
from app.documents.router import router as document_router
from app.chunking.router import router as chunk_router
from app.retrieval.router import router as retrieval_router
from app.generation.router import router as response_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="AI Support API",version="1.0.0",lifespan=lifespan)
app.include_router(health_rotuer)
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(chunk_router)
app.include_router(retrieval_router)
app.include_router(response_router) 
@app.get("/")
async def root():
    return {"message": "AI Support API is running"}