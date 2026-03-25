import yaml
import os
from dotenv import load_dotenv

# Explicitly load .env into os.environ so that os.getenv() can find the API keys
load_dotenv(".env")
load_dotenv("config/.env")

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PrivateAttr
from typing import Dict, Optional, Any, List, Union

class ModelParams(BaseModel):
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    system_prompt_prefix: Optional[str] = None
    system_prompt_suffix: Optional[str] = None

class ProviderConfig(BaseModel):
    base_url: str
    api_key: Optional[str] = None
    env_key_name: Optional[str] = None # Name of env var holding the key if not specified directly
    type: str # e.g. "openai_compatible"
    config: Optional[ModelParams] = None # Level 2 Configuration

    # Internal state for key rotation
    _api_keys: List[str] = PrivateAttr(default_factory=list)
    _current_key_idx: int = PrivateAttr(default=0)

    def model_post_init(self, __context: Any) -> None:
        """Parse comma-separated API keys into a list after init."""
        raw_keys = self.api_key
        if not raw_keys and self.env_key_name:
            raw_keys = os.getenv(self.env_key_name)
            
        if raw_keys:
            # Allow splitting by comma for fallback keys
            self._api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]

    def get_active_key(self) -> Optional[str]:
        """Return the current active API key."""
        if not self._api_keys:
            return None
        return self._api_keys[self._current_key_idx]

    def rotate_key(self) -> bool:
        """Move to the next key. Returns True if successfully rotated, False otherwise."""
        from core.logger import logger
        if self._current_key_idx < len(self._api_keys) - 1:
            self._current_key_idx += 1
            logger.info(f"Rotated to backup API key (index {self._current_key_idx}) for provider type '{self.type}'.")
            return True
        return False
        
    def reset_keys(self) -> None:
        """Reset the active key back to the primary."""
        self._current_key_idx = 0

class RoutingConfig(BaseModel):
    providers: Dict[str, ProviderConfig]
    model_mapping: Dict[str, Union[str, Dict[str, Any]]] # Updated to Dict[str, Any] for nested config
    default_provider: str
    global_config: Optional[ModelParams] = None # Level 1 Configuration
    profiles: Optional[Dict[str, ModelParams]] = None # Contextual Profiles

class Settings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    HOST: str = "127.0.0.1"
    PORT: int = 8082
    CONFIG_PATH: str = "config/config.yaml"
    FLY_APP_NAME: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def load_routing_config(path: str) -> RoutingConfig:
    if not os.path.exists(path):
        # Return a sensible default if no yaml file is found
        return RoutingConfig(providers={}, model_mapping={}, default_provider="")
        
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return RoutingConfig(**data)

settings = Settings()
routing_config = load_routing_config(settings.CONFIG_PATH)
