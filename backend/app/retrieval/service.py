from uuid import UUID

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

    async def retrieve(self, question: str, document_id: UUID | None = None):
        query_embedding = await self.embedding_service.generate_query_embedding(question)

        similar_chunks = await self.embedding_repository.find_similar_embeddings(
            query_embedding=query_embedding,
            limit=int(os.getenv("TOP_K", 3)),
            document_id=document_id,
        )

        if not similar_chunks:
            return []

        chunk_ids = [e.chunk_id for e in similar_chunks]
        chunks = await self.chunk_repository.get_chunks_by_ids(chunk_ids)
        chunk_map = {chunk.id: chunk for chunk in chunks}

        return [
            {"chunk_id": str(chunk.id), "text": chunk.chunk_text}
            for e in similar_chunks
            if (chunk := chunk_map.get(e.chunk_id)) is not None
        ]