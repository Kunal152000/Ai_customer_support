import json
from app.documents.models import DocumentMetadata
from app.generation.openrouter_provider import OpenRouterProvider

class QueryRouter:
    def __init__(self):
        self.provider = OpenRouterProvider()

    async def classify_and_answer(self, query: str, document: DocumentMetadata) -> dict:
        """
        Act as an intelligent router.
        If the query can be answered via the metadata/summary alone, generate the answer directly!
        If it requires deep document knowledge, route to DEEP_RAG.
        """
        metadata_json = json.dumps(document.extended_metadata or {})
        
        prompt = f"""You are an intelligent query routing agent for a document assistant.

Document Metadata (contains title, author, type, and full document summary):
{metadata_json}

User Query: "{query}"

Instructions:
Evaluate if the User Query can be completely and accurately answered ONLY using the Document Metadata provided above.

1. INTENT = "METADATA": If the user is asking about the author, title, document type, or publication details.
2. INTENT = "SUMMARY": If the user is asking for a summary, gist, or "what is this about?".
3. INTENT = "DEEP_RAG": If the user is asking a specific question about the document's content, plot, data, or details NOT explicitly covered in the summary.

If INTENT is METADATA or SUMMARY, you MUST provide the 'response' field containing the final answer to the user's query, written in a helpful and conversational tone.
If INTENT is DEEP_RAG, leave 'response' empty.

Respond ONLY with a valid JSON object:
{{
  "intent": "METADATA" | "SUMMARY" | "DEEP_RAG",
  "response": "string or null"
}}
"""
        try:
            content = await self.provider.generate_response(
                prompt=prompt,
                response_format={"type": "json_object"},
                temperature=0.0
            )
            return json.loads(content)
        except Exception as e:
            print(f"Router failed: {e}. Defaulting to DEEP_RAG.")
            return {"intent": "DEEP_RAG"}
