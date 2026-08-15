
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
        temperature: float = 1.0
    ):
   
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        if response_format:
            kwargs["response_format"] = response_format
            
        response = await self.client.chat.completions.create(**kwargs)
        
        print("This is response from openrouter",response.choices[0].message.content)
        return response.choices[0].message.content