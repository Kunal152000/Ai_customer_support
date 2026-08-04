from app.retrieval.service import RetrievalService
from app.generation.abstract_ai_base import AIProvider
from app.generation.prompt_builder import PromptBuilder
from app.generation.openrouter_provider import OpenRouterProvider

class GenerationService:
    def __init__(self,db):
        self.retrieval_service = RetrievalService(db)
        self.provider = OpenRouterProvider()

    async def answer(self, question: str) -> str:
        # Retrieve the most relevant chunks
        retrieval_response = await self.retrieval_service.retrieve(question)
        print("This is retrieval response",retrieval_response,type(retrieval_response))
        # Combine all retrieved chunks into a single context string
        context = "\n\n".join(
            chunk["text"] for chunk in retrieval_response
        )

        # Build the prompt
        prompt = PromptBuilder.build(
            question=question,
            context=context,
        )

        # Generate the final response from the LLM
        response = await self.provider.generate_response(prompt)

        return response