from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.generation.schemas import (
    GenerationRequest,
    GenerationResponse,
)
from app.generation.service import GenerationService
from app.auth.dependencies import get_current_user

router = APIRouter(tags=["Generation"],dependencies=[Depends(get_current_user)])


@router.post("/chat",response_model=GenerationResponse)
async def generate_response(request: GenerationRequest,db: AsyncSession = Depends(get_db),):
    
    generation_service = GenerationService(db)

    answer = await generation_service.answer(request.question)
    print("This is answer to print",answer)
    return GenerationResponse(
        answer=answer
    )