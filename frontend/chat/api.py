from uuid import UUID

from chat.schemas import ChatResponse, DocumentUploadResponse
from utils.api_client import APIClient


class ChatAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def list_documents(self) -> list[dict]:
        return self.client.get("/documents/")

    def upload(self, file_bytes: bytes, filename: str) -> DocumentUploadResponse:
        response = self.client.upload_file(
            endpoint="/documents/upload",
            file_bytes=file_bytes,
            filename=filename,
        )
        return DocumentUploadResponse.model_validate(response)

    def process(self, document_id: UUID) -> dict:
        return self.client.post(f"/chunking/{document_id}/process")

    def chat(self, question: str, document_id: str | None = None) -> ChatResponse:
        payload = {"question": question}
        if document_id:
            payload["document_id"] = document_id
        response = self.client.post("/chat", json=payload)
        return ChatResponse.model_validate(response)
