from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    question: str
    # top_k: int


class RetrievedChunk(BaseModel):
    chunk_id: str
    text: str


class RetrievalResponse(BaseModel):
    chunks: list[RetrievedChunk]