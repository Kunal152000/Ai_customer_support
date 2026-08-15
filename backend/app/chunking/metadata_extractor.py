import json
from app.chunking.models import DocumentChunk
from app.generation.openrouter_provider import OpenRouterProvider

class MetadataExtractor:
    def __init__(self):
        self.provider = OpenRouterProvider()
        
    async def _summarize_chunk(self, text: str) -> str:
        """Map step: summarize a block of text."""
        prompt = f"""Summarize the following text excerpt accurately and comprehensively.
Highlight any important names, facts, or concepts.

Text:
{text}

Summary:"""
        try:
            content = await self.provider.generate_response(prompt=prompt)
            return content or ""
        except Exception:
            return ""

    async def extract_metadata(self, filename: str, uploader_name: str, chunks: list[DocumentChunk]) -> dict:
        """Map-reduce summarization and metadata extraction."""
        # Step 1: Map - generate intermediate summaries
        # To avoid API rate limits, we summarize only a sample of chunks (e.g. beginning, middle, end)
        # For small documents (<= 5 chunks), we summarize all. For large docs, we take ~10 spaced chunks.
        step = max(1, len(chunks) // 10)
        sampled_chunks = chunks[::step][:10]
        
        chunk_summaries = []
        for chunk in sampled_chunks:
            # Mistral is fast, but we fire sequentially to avoid rate limits
            summary = await self._summarize_chunk(chunk.chunk_text)
            if summary:
                chunk_summaries.append(summary)
                
        combined_summaries = "\n---\n".join(chunk_summaries)

        # Step 2: Reduce - generate final JSON
        prompt = f"""You are an expert document analysis agent.
Analyze the following extracted summaries from a document and generate the final document metadata.

Rules:
1. "title": Find the real title of the document. If it is not clearly stated in the text, use "{filename}" as the fallback.
2. "author": Find the real author. If no author is mentioned in the text, use "{uploader_name}" as the fallback.
3. "document_type": E.g., "Research Paper", "Novel", "Invoice", "Meeting Notes". Be specific.
4. "brief_summary": Write a highly accurate, comprehensive, and well-structured summary of the ENTIRE document based on the excerpts. NOT vague.

Input Excerpts:
{combined_summaries}

Respond ONLY with a valid JSON object matching this schema:
{{
  "title": "string",
  "author": "string",
  "document_type": "string",
  "brief_summary": "string"
}}"""
        
        try:
            content = await self.provider.generate_response(
                prompt=prompt,
                response_format={"type": "json_object"},
            )
            return json.loads(content)
        except Exception as e:
            print(f"Metadata extraction failed: {e}")
            # Fallback
            return {
                "title": filename,
                "author": uploader_name,
                "document_type": "Unknown",
                "brief_summary": "Summary generation failed."
            }
