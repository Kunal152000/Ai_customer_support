from dotenv import load_dotenv
load_dotenv()
from app.database.init_db import init_db
import asyncio
from app.database.session import SessionLocal
from app.chunking.repository import ChunkRepository
from app.embeddings.repository import DocumentEmbeddingRepository
from app.embeddings.ai_provider import OpenRouterEmbeddingProvider
from app.embeddings.service import EmbeddingService


DOCUMENT_ID = "fb1b9ad9-1414-4ba2-aa84-edb534320632"

async def main():
    await init_db()
    async with SessionLocal() as db:
        chunk_repo = ChunkRepository(db)
        embedding_repo = DocumentEmbeddingRepository(db)
        provider = OpenRouterEmbeddingProvider()

        embedding_service = EmbeddingService(provider=provider,repository=embedding_repo)
        print(f"This is db: {db}")
        print(f"DB bind: {db.bind}")
        chunks = await chunk_repo.get_by_document(DOCUMENT_ID)

        print(f"Found {len(chunks)} chunks")

        await embedding_service.generate_embeddings(chunks)

        await db.commit()

        print("Embeddings stored successfully.")

if __name__ == "__main__":
    asyncio.run(main())