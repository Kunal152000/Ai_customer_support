from app.embeddings.ai_provider import OpenRouterEmbeddingProvider
from app.embeddings.service import EmbeddingService
from app.embeddings.repository import DocumentEmbeddingRepository
from app.chunking.repository import ChunkRepository
import os

class RetrievalService:

    def __init__(self, db):
        self.embedding_provider = OpenRouterEmbeddingProvider()

        self.embedding_repository = DocumentEmbeddingRepository(db)

        self.embedding_service = EmbeddingService(
            provider=self.embedding_provider,
            repository=self.embedding_repository,
        )

        self.chunk_repository = ChunkRepository(db)

    async def retrieve(self,question: str):
        query_embedding = await self.embedding_service.generate_query_embedding(question)

        similar_chunks = await self.embedding_repository.find_similar_embeddings(
            query_embedding=query_embedding,
            limit=os.getenv("TOP_K")
        )

        if not similar_chunks:
            return []

        chunk_ids = [embedding.chunk_id for embedding in similar_chunks]

        chunks = await self.chunk_repository.get_chunks_by_ids(chunk_ids)

        chunk_map = {chunk.id: chunk for chunk in chunks}

        results = []

        for embedding in similar_chunks:
            chunk = chunk_map.get(embedding.chunk_id)

            if chunk is None:
                continue

            results.append(
                {
                    "chunk_id": str(chunk.id),
                    "text": chunk.chunk_text,
                }
            )

        return results