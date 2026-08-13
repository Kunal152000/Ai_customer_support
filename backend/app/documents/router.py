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
    return await repo.list_by_owner(current_user.name)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    service = DocumentService(db)
    document = await service.upload_document(file=file, owner_name=current_user.name)
    return DocumentResponse.model_validate(document)