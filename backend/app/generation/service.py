from uuid import UUID

from app.retrieval.service import RetrievalService
from app.generation.abstract_ai_base import AIProvider
from app.generation.prompt_builder import PromptBuilder
from app.generation.openrouter_provider import OpenRouterProvider
from app.generation.query_router import QueryRouter
from app.documents.repository import DocumentRepository

class GenerationService:
    def __init__(self, db):
        self.retrieval_service = RetrievalService(db)
        self.provider = OpenRouterProvider()
        self.query_router = QueryRouter()
        self.document_repo = DocumentRepository(db)

    async def answer(self, question: str, document_id: UUID | None = None) -> str:
        # Phase 1: Intelligent Query Routing
        if document_id:
            document = await self.document_repo.get_document(document_id)
            if document:
                route = await self.query_router.classify_and_answer(question, document)
                intent = route.get("intent", "DEEP_RAG")
                
                # Bypass Deep RAG if the router was able to formulate an answer
                if intent in ("METADATA", "SUMMARY") and route.get("response"):
                    print(f"[Query Router] Bypassing RAG. Intent: {intent}")
                    return route["response"]

        # Phase 2: Standard Deep RAG Fallback
        print("[Query Router] Executing standard DEEP_RAG pipeline.")
        retrieval_response = await self.retrieval_service.retrieve(
            question=question,
            document_id=document_id,
        )
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