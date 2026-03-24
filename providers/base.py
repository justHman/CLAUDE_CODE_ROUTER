from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any
from transformers.models import AnthropicMessageRequest

class BaseProvider(ABC):
    """
    Abstract base class for all LLM providers.
    Every provider must be able to take an Anthropic-formatted request
    and return an Anthropic-formatted response (or stream).
    """
    
    def __init__(self, base_url: str, api_key: str | None = None, model: str | None = None, model_config: Any = None):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model # override model if required by provider config
        self.model_config = model_config # Resolved 3-level config

    @abstractmethod
    async def generate_message(self, request: AnthropicMessageRequest) -> Dict[str, Any]:
        """
        Generate a single standard API response mimicking Anthropic JSON.
        """
        pass

    @abstractmethod
    async def generate_stream(self, request: AnthropicMessageRequest) -> AsyncGenerator[str, None]:
        """
        Generate a stream of SSE identical to Anthropic format.
        Yields raw string chunks meant to be pushed out through FastAPI StreamingResponse.
        """
        pass
