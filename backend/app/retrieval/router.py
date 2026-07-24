import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.retrieval.schemas import RetrievalRequest, RetrievalResponse
from app.retrieval.service import RetrievalService

router = APIRouter(tags=["Retrieval"])


@router.post("/retrieval", response_model=RetrievalResponse)
async def retrieve_context(
    request: RetrievalRequest,
    db: AsyncSession = Depends(get_db),
):
    retrieval_service = RetrievalService(db)

    chunks = await retrieval_service.retrieve(
        question=request.question,
        top_k=int(os.getenv("TOP_K", 3)),
    )

    return RetrievalResponse(chunks=chunks)