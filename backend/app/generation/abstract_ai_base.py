from abc import ABC, abstractmethod


class AIProvider(ABC):

    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        """
        Generate a response based on the provided prompt.
        """
        raise NotImplementedError