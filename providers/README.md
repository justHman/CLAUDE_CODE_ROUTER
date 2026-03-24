# Providers Module

## Overview
LLM provider implementations using factory pattern.

## Files

- **base.py** - Base provider class defining the interface
- **factory.py** - Factory for creating provider instances
- **openai_compat.py** - OpenAI-compatible provider implementation (used by NVIDIA, OpenRouter, etc.)

## Adding a New Provider

1. Create a new class inheriting from `BaseProvider` in a new file
2. Implement `generate_message()` and `generate_stream()` methods
3. Register the provider in `factory.py`
4. Add provider config to `config/config.yaml`

## Supported Providers

- **NVIDIA** - Via OpenAI-compatible API
- **OpenRouter** - Via OpenAI-compatible API
- Any OpenAI-compatible provider