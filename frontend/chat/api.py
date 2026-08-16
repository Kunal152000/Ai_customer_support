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

    def delete_document(self, document_id: str) -> dict:
        return self.client.delete(f"/documents/{document_id}")

    def chat_stream(self, question: str, document_id: str | None = None):
        payload = {"question": question}
        if document_id:
            payload["document_id"] = document_id
        # Returns an active generator yielding string chunks
        return self.client.post_stream("/chat", json=payload)
