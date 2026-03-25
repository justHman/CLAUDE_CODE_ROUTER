import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as messages_router
from api.dashboard import router as dashboard_router
from core.config import settings
from core.logger import setup_logging, logger
from core.db import init_db

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
    
    app.include_router(messages_router)
    app.include_router(dashboard_router)
    
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Claude Code API Router Server! 🚀",
            "docs": "/docs",
            "dashboard": "/dashboard",
            "health": "/health"
        }

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
        
    @app.get("/fly/logs/{app_name}")
    def get_fly_logs(app_name: str):
        """Redirect to Fly.io monitoring dashboard if on Fly, otherwise return info."""
        # FLY_APP_NAME is automatically set by Fly.io at runtime
        if settings.FLY_APP_NAME or os.getenv("FLY_APP_NAME"):
            return RedirectResponse(url=f"https://fly.io/apps/{app_name}/monitoring")
        
        return {
            "status": "local",
            "message": "You are running on Localhost. Please check your terminal/console for logs.",
            "fly_monitoring_url": f"https://fly.io/apps/{app_name}/monitoring"
        }

    return app

app = create_app()
