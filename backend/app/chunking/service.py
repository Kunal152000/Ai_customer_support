from uuid import UUID

from app.chunking.models import DocumentChunk
from app.chunking.repository import ChunkRepository

class ChunkService:
    def __init__(self,repository: ChunkRepository):
        self.repository = repository

    async def save_chunks(self,document_id: UUID,chunks: list[str],) -> int:

        if not chunks:
            return 0

        chunk_models = [
            DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                chunk_text=chunk,
                word_count=len(chunk.split()),
            )
            for index, chunk in enumerate(chunks)
        ]

        return await self.repository.create_many(chunk_models)

    async def get_chunks(self,document_id: UUID):
        return await self.repository.get_by_document(document_id)

    async def delete_chunks(self,document_id: UUID):
        await self.repository.delete_by_document(document_id)