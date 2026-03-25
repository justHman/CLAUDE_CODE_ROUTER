import asyncio
import subprocess
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.routes import router as messages_router
from core.config import settings
from core.logger import setup_logging, logger
from core.db import init_db

class SSHCommand(BaseModel):
    command: str

def create_app() -> FastAPI:
    setup_logging()
    logger.info("Initializing FastAPI application")
    init_db()  # Initialize the SQLite database and tables
    
    app = FastAPI(
        title="Claude Code Router",
        description="API Router that mimics Anthropic but routes conditionally to multiple providers.",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    from api.dashboard import router as dashboard_router
    app.include_router(messages_router)
    app.include_router(dashboard_router)
    
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Claude Code API Router Server! 🚀",
            "test": "/docs",
            "dashboard": "/dashboard",
            "health": "/health"
        }

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
        
    @app.get("/fly/logs/{app_name}")
    def get_fly_logs(app_name: str):
        """Stream logs for a Fly.io app."""
        def log_generator():
            process = subprocess.Popen(
                ["flyctl", "logs", "-a", app_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            try:
                assert process.stdout is not None
                for line in iter(process.stdout.readline, b''):
                    if not line:
                        break
                    yield line
            finally:
                process.terminate()

        return StreamingResponse(log_generator(), media_type="text/plain")

    return app

app = create_app()
