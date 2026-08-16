
from app.generation.abstract_ai_base import AIProvider
from openai import AsyncOpenAI
import os

class OpenRouterProvider(AIProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL"),
        )
        self.model = os.getenv("OPENROUTER_MODEL")

    async def generate_response(
        self, 
        prompt: str, 
        response_format: dict | None = None,
        temperature: float = 1.0,
        stream: bool = False
    ):
   
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        if response_format:
            kwargs["response_format"] = response_format
            
        if stream:
            kwargs["stream"] = True
            response = await self.client.chat.completions.create(**kwargs)
            async def generate():
                async for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            return generate()
            
        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content