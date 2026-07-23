from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.documents.repository import DocumentRepository
from app.documents.service import ProcessingService
from app.chunking.repository import ChunkRepository
from app.chunking.service import ChunkService
from app.chunking.recursive_chunker import RecursiveChunker
from app.parsers.parser_factory import ParserFactory
from app.storage.local import LocalStorageService

router = APIRouter(prefix="/chunking", tags=["Chunking"])


@router.post("/{document_id}/process")
async def process_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repository = DocumentRepository(db)
    chunk_repository = ChunkRepository(db)

    service = ProcessingService(
        repository=repository,
        storage=LocalStorageService(),
        parser_factory=ParserFactory(),
        chunker=RecursiveChunker(),
        chunk_service=ChunkService(chunk_repository),
    )

    try:
        count = await service.process_document(document_id)

        return {
            "message": "Document processed successfully",
            "chunks_saved": count,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))