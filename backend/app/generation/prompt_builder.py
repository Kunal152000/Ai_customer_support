class PromptBuilder:

    @staticmethod
    def build(question: str, context: str) -> str:
        return f"""You are an intelligent document assistant. A user is asking questions about a document they have uploaded.

Use the provided context excerpts to answer the question. The context may reference the answer indirectly — synthesize and infer from what is present rather than looking for an exact statement.

If the context contains relevant information, always attempt to answer using it.
Only say "I don't have enough information to answer that." if the context is completely unrelated to the question.

Context from document:
{context}

Question: {question}

Answer:"""