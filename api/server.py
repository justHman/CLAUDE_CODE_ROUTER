import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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
    async def get_fly_logs(app_name: str):
        """Stream logs for a Fly.io app."""
        async def log_generator():
            process = await asyncio.create_subprocess_exec(
                "flyctl", "logs", "-a", app_name,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            try:
                assert process.stdout is not None
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    yield line
            finally:
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass

        return StreamingResponse(log_generator(), media_type="text/plain")

    @app.post("/fly/ssh/{app_name}")
    async def execute_fly_ssh_command(app_name: str, payload: SSHCommand):
        """Execute a single command on a Fly.io app via ssh console."""
        process = await asyncio.create_subprocess_exec(
            "flyctl", "ssh", "console", "-a", app_name, "-C", payload.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return {
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
            "returncode": process.returncode
        }

    @app.websocket("/fly/ssh/ws/{app_name}")
    async def fly_ssh_websocket(websocket: WebSocket, app_name: str):
        """Interactive ssh console over websocket."""
        await websocket.accept()
        process = await asyncio.create_subprocess_exec(
            "flyctl", "ssh", "console", "-a", app_name, "-q",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        async def read_stdout():
            assert process.stdout is not None
            while True:
                data = await process.stdout.read(1024)
                if not data:
                    break
                await websocket.send_text(data.decode('utf-8', errors='replace'))

        async def read_stderr():
            assert process.stderr is not None
            while True:
                data = await process.stderr.read(1024)
                if not data:
                    break
                await websocket.send_text(data.decode('utf-8', errors='replace'))

        async def read_ws():
            try:
                assert process.stdin is not None
                while True:
                    data = await websocket.receive_text()
                    process.stdin.write(data.encode('utf-8'))
                    await process.stdin.drain()
            except WebSocketDisconnect:
                pass

        task1 = asyncio.create_task(read_stdout())
        task2 = asyncio.create_task(read_stderr())
        task3 = asyncio.create_task(read_ws())

        try:
            done, pending = await asyncio.wait(
                [task1, task2, task3],
                return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
        finally:
            try:
                process.terminate()
            except Exception:
                pass

    return app

app = create_app()
