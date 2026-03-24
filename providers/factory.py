import os
from core.config import ProviderConfig
from providers.base import BaseProvider
from providers.openai_compat import OpenAICompatibleProvider

class ProviderFactory:
    @staticmethod
    def create(config: ProviderConfig, custom_model: str = None) -> BaseProvider:
        api_key = config.api_key
        
        # Fallback to environment variable if specified and not explicitly set
        if not api_key and config.env_key_name:
            api_key = os.getenv(config.env_key_name)
            
        if not api_key:
            # We don't raise error immediately because some mock providers might not need it,
            # but usually it's required.
            pass
            
        if config.type == "openai_compatible":
            return OpenAICompatibleProvider(
                base_url=config.base_url,
                api_key=api_key,
                model=custom_model
            )
        elif config.type == "gemini":
            from providers.gemini import GeminiProvider
            return GeminiProvider(
                base_url=config.base_url or "",
                api_key=api_key,
                model=custom_model
            )
        else:
            raise ValueError(f"Unknown provider type: {config.type}")
