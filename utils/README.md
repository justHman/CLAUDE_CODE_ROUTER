# Utils Module

## Overview
Utility scripts for the Claude Code Router.

## Files

- **get_models.py** - Fetches available models from OpenRouter API and filters for specific providers (minimax, free, stepfun, nemotron, glm, qwen)

## Usage

```powershell
python utils/get_models.py
```

This will print model IDs matching the filter criteria, useful for updating model mappings in config.yaml.