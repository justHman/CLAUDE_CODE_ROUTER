# API Module

## Overview
FastAPI server endpoints for the Claude Code Router.

## Files

- **server.py** - Main FastAPI application entry point
- **routes.py** - API route definitions (/v1/messages endpoint)
- **deps.py** - Dependency injection helpers

## Key Endpoints

### POST /v1/messages
Handles Claude Code message requests, supports both streaming and non-streaming responses.

## Usage
This module is auto-loaded by uvicorn when running `python main.py`.