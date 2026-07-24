from dotenv import load_dotenv
load_dotenv()
import os
import asyncio

from app.database.init_db import init_db
from app.database.session import SessionLocal

from app.embeddings.ai_provider import OpenRouterEmbeddingProvider
from app.embeddings.service import EmbeddingService
from app.embeddings.repository import DocumentEmbeddingRepository

from app.chunking.repository import ChunkRepository

from app.retrieval.service import RetrievalService


QUESTION = "What experience does Kunal have with FastAPI?"


async def main():
    # Initialize database
    await init_db()

    async with SessionLocal() as session:

        # Create dependencies
        embedding_provider = OpenRouterEmbeddingProvider()
        print("here")
        embedding_repository = DocumentEmbeddingRepository(session)
        embedding_service = EmbeddingService(embedding_provider,embedding_repository)
        chunk_repository = ChunkRepository(session)

        retrieval_service = RetrievalService(
            embedding_service=embedding_service,
            embedding_repository=embedding_repository,
            chunk_repository=chunk_repository,
        )
        print("here1")
        # Retrieve relevant chunks
        results = await retrieval_service.retrieve(
            question=QUESTION,
            top_k=int(os.getenv("TOP_K", 3)))
        print("here2")

        print("\n" + "=" * 100)
        print(f"QUESTION : {QUESTION}")
        print("=" * 100)

        if not results:
            print("\nNo similar chunks found.")
            return

        for index, result in enumerate(results, start=1):
            print(f"\nResult #{index}")
            print("-" * 100)
            # print(f"Score     : {result['score']}")
            print(f"Chunk ID  : {result['chunk_id']}")
            print(f"Chunk Text:\n{result['text']}")
            print("-" * 100)

        print("here3")


if __name__ == "__main__":
    asyncio.run(main())