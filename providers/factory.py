import os
from typing import Any, Dict
from core.config import ProviderConfig
from providers.base import BaseProvider
from providers.openai_compat import OpenAICompatibleProvider

class ProviderFactory:
    @staticmethod
    def create(config: ProviderConfig, custom_model: str = None, model_config: Any = None) -> BaseProvider:
        if config.type == "openai_compatible":
            return OpenAICompatibleProvider(
                config=config,
                custom_model=custom_model,
                model_config=model_config
            )
        elif config.type == "gemini":
            from providers.gemini import GeminiProvider
            return GeminiProvider(
                config=config,
                custom_model=custom_model,
                model_config=model_config
            )
        else:
            raise ValueError(f"Unknown provider type: {config.type}")
