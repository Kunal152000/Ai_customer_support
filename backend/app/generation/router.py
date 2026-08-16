from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.generation.schemas import (
    GenerationRequest,
    GenerationResponse,
)
from app.generation.service import GenerationService
from app.auth.dependencies import get_current_user

from fastapi.responses import StreamingResponse

router = APIRouter(tags=["Generation"],dependencies=[Depends(get_current_user)])


@router.post("/chat")
async def generate_response(request: GenerationRequest,db: AsyncSession = Depends(get_db)):
    
    generation_service = GenerationService(db)

    return StreamingResponse(
        generation_service.answer_stream(
            question=request.question,
            document_id=request.document_id,
        ),
        media_type="text/plain"
    )