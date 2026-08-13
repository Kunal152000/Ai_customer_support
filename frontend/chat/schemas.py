from uuid import UUID
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: UUID
    original_filename: str
    status: str


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
