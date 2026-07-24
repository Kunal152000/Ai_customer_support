from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.documents.service import ProcessingService

router = APIRouter(
    prefix="/chunking",
    tags=["Chunking"],
)

@router.post("/{document_id}/process")
async def process_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ProcessingService(db)

    try:
        count = await service.process_document(document_id)

        return {
            "message": "Document processed successfully",
            "chunks_saved": count,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))