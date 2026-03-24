# Core Module

## Overview
Core functionality: configuration, logging, and routing logic.

## Files

- **config.py** - Settings management using pydantic-settings, loads YAML config and .env files
- **logger.py** - Logging configuration
- **routing.py** - Router class that maps models to providers
- **db.py** - Request logging to database (if enabled)

## Configuration

Settings are loaded from:
- `config/config.yaml` - Provider definitions and model mappings
- `.env` or `config/.env` - API keys

### Environment Variables
- `LOG_LEVEL` - Logging level (default: INFO)
- `HOST` - Server host (default: 127.0.0.1)
- `PORT` - Server port (default: 8082)
- `NVIDIA_API_KEY` - NVIDIA API key
- `OPENROUTER_API_KEY` - OpenRouter API key

## Routing

The Router class (`core/routing.py`) handles:
- Looking up provider for a given model name
- Translating model aliases to actual model names
- Provider instantiation via factory