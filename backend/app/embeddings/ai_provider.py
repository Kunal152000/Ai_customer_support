from langchain_openai import OpenAIEmbeddings
import os
from app.embeddings.abstract_embedding_base import EmbeddingProvider

class OpenRouterEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        self.client = OpenAIEmbeddings(
            model=os.getenv("EMBEDDING_MODEL"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL"),
        )

    async def embed(self,texts: list[str],) -> list[list[float]]:
        return await self.client.aembed_documents(texts)