import sys
from loguru import logger
from core.config import settings

def setup_logging():
    # Remove default logger
    logger.remove()
    
    # Add console logger with pretty formatting
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    logger.info(f"Logger initialized at level {settings.LOG_LEVEL}")

# This can be imported across the app
__all__ = ["logger", "setup_logging"]
