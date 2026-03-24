from typing import Any
from core.config import routing_config, ProviderConfig
from providers.base import BaseProvider
from providers.factory import ProviderFactory
from core.logger import logger

class Router:
    def __init__(self, config=routing_config):
        self.config = config

    def _resolve_model_config(self, mapping: Any, provider_name: str) -> Any:
        """
        Merges 3 layers of config: Global -> Provider -> Model
        """
        from core.config import ModelParams
        
        # 1. Start with Global
        resolved = self.config.global_config.model_dump() if self.config.global_config else {}
        
        # 2. Layer Provider config
        provider_cfg = self.config.providers.get(provider_name)
        if provider_cfg and provider_cfg.config:
            # Only update non-None values
            p_dict = provider_cfg.config.model_dump()
            resolved.update({k: v for k, v in p_dict.items() if v is not None})
            
        # 3. Layer Profile config
        if isinstance(mapping, dict) and "profile" in mapping:
            profile_name = mapping["profile"]
            if self.config.profiles and profile_name in self.config.profiles:
                p_dict = self.config.profiles[profile_name].model_dump()
                resolved.update({k: v for k, v in p_dict.items() if v is not None})
            else:
                logger.warning(f"Profile '{profile_name}' referenced but not found in config.")

        # 4. Layer Model-specific config
        if isinstance(mapping, dict) and "config" in mapping:
            # Model config in model_mapping is a raw dict that needs to be coerced
            m_config = mapping["config"]
            if isinstance(m_config, dict):
                resolved.update({k: v for k, v in m_config.items() if v is not None})
        
        return ModelParams(**resolved)

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
            
        resolved_model_config = self._resolve_model_config(mapping, provider_name)
            
        return ProviderFactory.create(provider_cfg, custom_model=target_model, model_config=resolved_model_config)

# Singleton router instance for simple di
router = Router()
