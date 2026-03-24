from core.config import routing_config, ProviderConfig
from providers.base import BaseProvider
from providers.factory import ProviderFactory
from core.logger import logger

class Router:
    def __init__(self, config=routing_config):
        self.config = config

    def get_provider_for_model(self, requested_model: str) -> BaseProvider:
        """
        Determines which provider config to use based on the requested model.
        Returns an instantiated Provider.
        """
        mapping = self.config.model_mapping.get(requested_model)
        
        provider_name = None
        target_model = requested_model
        
        if isinstance(mapping, str):
            provider_name = mapping
        elif isinstance(mapping, dict):
            provider_name = mapping.get("provider")
            target_model = mapping.get("target_model", requested_model)
        
        if provider_name:
            logger.info(f"Routed model '{requested_model}' to provider '{provider_name}' as '{target_model}'")
        else:
            provider_name = self.config.default_provider
            logger.info(f"No specific mapping for '{requested_model}'. Using default '{provider_name}'")
            
        provider_cfg = self.config.providers.get(provider_name)
        
        if not provider_cfg:
            raise ValueError(f"Provider '{provider_name}' is not defined in config.")
            
        return ProviderFactory.create(provider_cfg, custom_model=target_model)

# Singleton router instance for simple di
router = Router()
