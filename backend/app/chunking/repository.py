# app/documents/chunk_repository.py

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chunking.models import DocumentChunk

class ChunkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(self,chunks: list[DocumentChunk]) -> int:
        self.db.add_all(chunks)
        await self.db.commit()

        return len(chunks)

    async def get_by_document(self,document_id: UUID,) -> list[DocumentChunk]:
        result = await self.db.execute(select(DocumentChunk).where(DocumentChunk.document_id == document_id))
        
        return list(result.scalars().all())

    async def delete_by_document(self,document_id: UUID ) -> None:
        await self.db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))

        await self.db.commit()