from app.embeddings.abstract_embedding_base import EmbeddingProvider
from app.embeddings.repository import DocumentEmbeddingRepository
from app.chunking.models import DocumentChunk
import os

class EmbeddingService:

    def __init__(self,provider: EmbeddingProvider,repository: DocumentEmbeddingRepository):
        self.provider = provider
        self.repository = repository
    
    async def generate_embeddings(self,chunks: list[DocumentChunk]):
        # print("This is chunks data",chunks)
        texts = [chunk.chunk_text for chunk in chunks]

        vectors = await self.provider.embed(texts)
        
        # to add embedding in db
        for chunk, vector in zip(chunks, vectors):
            await self.repository.add_embedding(chunk_id=chunk.id,embedding=vector,model=os.getenv("EMBEDDING_MODEL"))
    
    async def generate_query_embedding(self,query: str):
        vector = await self.provider.embed([query])
        return vector[0]