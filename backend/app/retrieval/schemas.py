from uuid import UUID
from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    question: str
    document_id: UUID | None = None


class RetrievedChunk(BaseModel):
    chunk_id: str
    text: str


class RetrievalResponse(BaseModel):
    chunks: list[RetrievedChunk]