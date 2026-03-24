# Config Module

## Overview
Configuration files for the Claude Code Router.

## Files

- **config.yaml** - Provider definitions and model mappings
- **.env.example** - Template for environment variables

## config.yaml Structure

```yaml
providers:
  provider_name:
    base_url: "https://api.provider.com/v1"
    api_key: "your-api-key"  # or use env_key_name
    env_key_name: "PROVIDER_API_KEY"
    type: "openai_compatible"

model_mapping:
  "model_alias": "provider_name"
  # or with translation:
  "model_alias":
    provider: "provider_name"
    target_model: "actual_model_name"

default_provider: "provider_name"
```

## Model Mapping

Two formats supported:
1. Simple: Maps model name directly to provider
2. With translation: Maps alias to provider + actual model name