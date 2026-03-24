# Transformers Module

## Overview
Request/response format conversion between Anthropic and OpenAI formats.

## Files

- **models.py** - Pydantic models for request/response structures
- **request.py** - Converts Anthropic-format requests to provider format
- **response.py** - Converts provider responses back to Anthropic format

## Functionality

- Text message conversion
- Image/vision support
- Tool calling (function definitions)
- Stream response handling
- MCP (Model Context Protocol) support

## Request Flow
Claude Code → Anthropic format → request.py transforms → Provider API → response.py transforms → Claude Code