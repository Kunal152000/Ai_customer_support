# import hashlib
# import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.documents.enums import DocumentStatus, DocumentType
from app.documents.models import DocumentMetadata
from app.documents.repository import DocumentRepository
from app.storage.abstract_storage_base import StorageService

class DocumentService:
    def __init__(self,repository: DocumentRepository,storage: StorageService):
        self.repository = repository
        self.storage = storage

    async def upload_document(self,file: UploadFile,owner_name: str,) -> DocumentMetadata:
        if not file.filename:
            raise HTTPException(400, "Filename is missing.")

        extension = Path(file.filename).suffix.lower()
        stored_filename = f"{uuid4()}{extension}"
        file_bytes = await file.read()
        # file_hash = hashlib.sha256(file_bytes).hexdigest()
        file_size = len(file_bytes)
        file.file.seek(0)
        # mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        # document_type = self._get_document_type(extension)
        storage_location = await self.storage.save(file=file,filename=stored_filename,)

        try:
            document = DocumentMetadata(
                # id
                owner_name=owner_name,
                original_filename=file.filename,
                stored_filename=stored_filename,
                storage_location=storage_location,
                document_type = self._get_document_type(extension),
                # mime_type=mime_type,
                file_size=file_size,
                # file_hash=file_hash,
                status=DocumentStatus.UPLOADED,
                version=1,
                title=None,
            )
            return await self.repository.create_document(document)
        
        except Exception:
            self.storage.delete(storage_location)
            raise
    
    def _get_document_type(self, extension: str) -> DocumentType:
        mapping = {
            ".pdf": DocumentType.PDF,
            ".doc": DocumentType.DOC,
            ".docx": DocumentType.DOCX,
            ".txt": DocumentType.TXT,
            ".csv": DocumentType.CSV,
            ".xlsx": DocumentType.XLSX,
            ".url": DocumentType.URL,
        }

        return mapping.get(extension, DocumentType.TXT)