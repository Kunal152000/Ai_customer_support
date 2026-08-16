from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.documents.schemas import DocumentResponse, DocumentListResponse
from app.documents.service import DocumentService
from app.documents.repository import DocumentRepository
from app.auth.dependencies import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/documents", tags=["Documents"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[DocumentListResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = DocumentRepository(db)
    return await repo.list_by_email(current_user.email)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    service = DocumentService(db)
    document = await service.upload_document(file=file, owner_name=current_user.name, email=current_user.email)
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from uuid import UUID
    try:
        doc_uuid = UUID(document_id)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    service = DocumentService(db)
    await service.delete_document(doc_uuid, current_user.email)
    return {"message": "Document deleted successfully"}

@router.get("/{document_id}/status")
async def get_document_status(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from uuid import UUID
    from fastapi import HTTPException
    try:
        doc_uuid = UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    repo = DocumentRepository(db)
    document = await repo.get_document(doc_uuid)
    if not document or document.email != current_user.email:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return {"status": document.status.value}
