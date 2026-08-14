from app.embeddings.abstract_embedding_base import EmbeddingProvider
from app.embeddings.repository import DocumentEmbeddingRepository
from app.chunking.models import DocumentChunk
import os

BATCH_SIZE = 50  # Stay well within API rate limits

class EmbeddingService:

    def __init__(self, provider: EmbeddingProvider, repository: DocumentEmbeddingRepository):
        self.provider = provider
        self.repository = repository

    async def generate_embeddings(self, chunks: list[DocumentChunk]):
        model = os.getenv("EMBEDDING_MODEL")

        # Process in batches to avoid hitting API rate limits
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]
            texts = [chunk.chunk_text for chunk in batch]
            vectors = await self.provider.embed(texts)

            for chunk, vector in zip(batch, vectors):
                await self.repository.add_embedding(
                    chunk_id=chunk.id,
                    embedding=vector,
                    model=model,
                )

            # Commit each batch so data is persisted even if a later batch fails
            await self.repository.db.commit()
            print(f"Embedded batch {i // BATCH_SIZE + 1} ({len(batch)} chunks)")

    async def generate_query_embedding(self, query: str):
        vector = await self.provider.embed([query])
        return vector[0]