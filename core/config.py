import yaml
import os
from dotenv import load_dotenv

# Explicitly load .env into os.environ so that os.getenv() can find the API keys
load_dotenv(".env")
load_dotenv("config/.env")

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
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
