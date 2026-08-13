# import hashlib
# import mimetypes
from pathlib import Path
from uuid import uuid4, UUID

from fastapi import HTTPException, UploadFile
from app.documents.enums import DocumentStatus, DocumentType
from app.documents.models import DocumentMetadata
from app.documents.repository import DocumentRepository
from app.storage.local import LocalStorageService
from app.parsers.parser_factory import ParserFactory
from app.chunking.service import ChunkService
from sqlalchemy.ext.asyncio import AsyncSession
from app.documents.repository import DocumentRepository
from app.storage.local import LocalStorageService
from app.chunking.recursive_chunker import RecursiveChunker
class DocumentService:
    def __init__(self,db: AsyncSession):
        self.repository = DocumentRepository(db)
        self.storage = LocalStorageService()

    async def upload_document(self, file: UploadFile, owner_name: str, email: str) -> DocumentMetadata:
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
                email=email,
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
    
    async def delete_document(self, document_id: UUID, user_email: str) -> None:
        document = await self.repository.get_document(document_id)
        if not document:
            raise HTTPException(404, "Document not found")
        
        # Verify ownership
        if document.email != user_email:
            raise HTTPException(403, "You do not have permission to delete this document.")
            
        # Optional: Delete chunks explicitly if DB doesn't have ON DELETE CASCADE for chunks. 
        # Since embeddings have ON DELETE CASCADE off chunks, deleting chunks will delete embeddings.
        from app.chunking.service import ChunkService
        chunk_service = ChunkService(self.repository.db)
        await chunk_service.delete_chunks(document_id)
        
        # Delete file from storage
        try:
            self.storage.delete(document.storage_location)
        except Exception as e:
            # Continue even if physical file is missing to ensure DB consistency
            print(f"Warning: could not delete file {document.storage_location}: {e}")
            
        # Delete metadata
        await self.repository.delete_document(document)

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

class ProcessingService:

    def __init__(self, db: AsyncSession):
        self.repository = DocumentRepository(db)
        self.storage = LocalStorageService()
        self.parser_factory = ParserFactory()
        self.chunk_service = ChunkService(db)
        self.chunker = RecursiveChunker()   

    async def process_document(self,document_id: UUID,) -> int:
        document = await self.repository.get_document(document_id)
        if document is None:
            raise ValueError("Document not found")
        
        path = self.storage.read(document.storage_location)
        parser = self.parser_factory.get_parser(path)
        text = parser.parse(path)
        chunks = self.chunker.chunk(text)

        return await self.chunk_service.save_chunks(document.id,chunks)