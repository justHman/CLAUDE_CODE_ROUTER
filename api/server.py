from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as messages_router
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
    
    from api.dashboard import router as dashboard_router
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
        
    return app

app = create_app()
