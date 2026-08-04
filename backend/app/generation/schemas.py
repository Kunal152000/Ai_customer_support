from pydantic import BaseModel
from uuid import UUID

class GenerationRequest(BaseModel):
    question: str 

class SourceResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID

class GenerationResponse(BaseModel):
    answer: str
    # sources: list[SourceResponse]