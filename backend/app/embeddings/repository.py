from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings.models import DocumentEmbedding
from app.chunking.models import DocumentChunk


class DocumentEmbeddingRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_embedding(self, chunk_id, embedding, model):
        entity = DocumentEmbedding(chunk_id=chunk_id, embedding=embedding, model=model)
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def find_similar_embeddings(self, query_embedding, limit=5, document_id: UUID | None = None):
        distance = DocumentEmbedding.embedding.cosine_distance(query_embedding)

        stmt = (
            select(DocumentEmbedding, DocumentChunk)
            .join(DocumentChunk, DocumentChunk.id == DocumentEmbedding.chunk_id)
        )
        if document_id:
            stmt = stmt.where(DocumentChunk.document_id == document_id)
            
        stmt = stmt.order_by(distance).limit(limit)

        result = await self.db.execute(stmt)
        # result.all() returns a list of tuples: [(embedding, chunk), ...]
        return result.all()
