from fastapi import Request
from core.routing import router

async def get_router():
    return router
