from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.documents.enums import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    id: UUID

    owner_name: str

    original_filename: str
    stored_filename: str
    storage_location: str

    document_type: DocumentType
    # mime_type: str
    file_size: int
    # file_hash: str

    status: DocumentStatus
    version: int

    title: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentListResponse(BaseModel):
    id: UUID

    original_filename: str

    document_type: DocumentType
    file_size: int

    status: DocumentStatus

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeleteDocumentResponse(BaseModel):
    message: str