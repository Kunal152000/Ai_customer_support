from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings.models import DocumentEmbedding


class DocumentEmbeddingRepository:

    def __init__(self,db: AsyncSession):
        self.db = db

    async def add_embedding(self,chunk_id,embedding,model,):
        entity = DocumentEmbedding( chunk_id=chunk_id,embedding=embedding,model=model,)

        self.db.add(entity)

        await self.db.flush()

        return entity