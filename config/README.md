# Config Module

## Overview
Configuration files for the Claude Code Router.

## Files

- **config.yaml** - Provider definitions, common Profiles, and model mappings
- **.env.example** - Template for environment variables

## config.yaml Structure

```yaml
# Level 1: Global Defaults
global_config:
  max_tokens: 4096
  temperature: 0.7

# Level 2: Profiles (Reusable Strategy)
profiles:
  coding:
    temperature: 0.0
    top_k: 1
    system_prompt: "You are an expert engineer..."

# Level 3: Providers
providers:
  provider_name:
    base_url: "https://api.provider.com/v1"
    type: "openai_compatible"
    config:
      temperature: 0.5

# Level 4: Model Mapping (Priority)
model_mapping:
  "model_alias":
    provider: "provider_name"
    target_model: "actual_model_name"
    profile: "coding"
    config:
      max_tokens: 8192

default_provider: "provider_name"
```

## Configuration Layers (Inheritance)

The router supports a 4-level configuration merging strategy:
1. **Global**: `global_config` in `config.yaml`.
2. **Provider**: `providers[name].config`.
3. **Profile**: `profiles[name]` (referenced by `profile` key in model mapping).
4. **Model Specific**: `model_mapping[name].config`.

## Profiles

Profiles allow you to define common parameter sets (like `coding`, `creative`) and reuse them across different models to keep the configuration clean.