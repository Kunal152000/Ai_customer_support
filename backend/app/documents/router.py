from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.documents.repository import DocumentRepository
from app.documents.schemas import DocumentResponse
from app.documents.service import DocumentService
from app.storage.local import LocalStorageService

router = APIRouter(prefix="/documents",tags=["Documents"])

@router.post( "/upload",response_model=DocumentResponse,)
async def upload_document(owner_name: str,file: UploadFile = File(...),db: AsyncSession = Depends(get_db),):
    repository = DocumentRepository(db)
    storage = LocalStorageService()
    service = DocumentService(repository,storage,)
    document = await service.upload_document(file=file,owner_name=owner_name)
    return DocumentResponse.model_validate(document)