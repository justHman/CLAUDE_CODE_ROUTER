import uvicorn
from core.config import settings
from core.logger import logger
from core.db import init_db

if __name__ == "__main__":
    init_db()
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "api.server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        reload_includes=["*.yaml"]
    )
