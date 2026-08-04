class PromptBuilder:

    @staticmethod
    def build(question: str, context: str) -> str:
        return f"""
You are a helpful AI support assistant.

Answer ONLY using the provided context.

Do not make up information. If the answer is not present in the context, reply:
"I don't have enough information to answer that."

Context:
{context}

Question:
{question}

Answer:
"""