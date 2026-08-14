from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.documents.service import ProcessingService
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/chunking",
    tags=["Chunking"],
    dependencies=[Depends(get_current_user)],
)


async def _run_processing(document_id: UUID, db: AsyncSession):
    """Background worker — runs after the HTTP response is already sent."""
    try:
        service = ProcessingService(db)
        count = await service.process_document(document_id)
        print(f"[BG] Document {document_id} processed — {count} chunks embedded.")
    except Exception as e:
        print(f"[BG] Processing failed for {document_id}: {e}")


@router.post("/{document_id}/process", status_code=202)
async def process_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    background_tasks.add_task(_run_processing, document_id, db)
    return {"message": "Processing started in the background", "document_id": str(document_id)}