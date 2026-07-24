from sqlalchemy import select
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
    
    async def find_similar_embeddings(self, query_embedding, limit=5):
        # Use cosine similarity to find the most similar embeddings
        # print("Query embedding:", query_embedding)
        distance = DocumentEmbedding.embedding.cosine_distance(query_embedding)

        stmt = (select(DocumentEmbedding, distance.label("distance")).order_by(distance).limit(limit))

        result = await self.db.execute(stmt)
        # print("Similar embeddings found:", result.scalars().all())
        return result.scalars().all()
    
