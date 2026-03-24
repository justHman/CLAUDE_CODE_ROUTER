import sqlite3
import os
from pathlib import Path
from datetime import datetime
from loguru import logger

# Use environment variable for DB directory (useful for Docker/Fly.io Volumes)
db_env = os.getenv("DB_DIR", "data")
DB_DIR = Path(db_env)
DB_PATH = DB_DIR / "router.db"

def init_db():
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS request_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    requested_model TEXT,
                    target_model TEXT,
                    provider TEXT,
                    latency_ms INTEGER,
                    status_code INTEGER,
                    tokens_in INTEGER,
                    tokens_out INTEGER,
                    total_tokens INTEGER
                )
            ''')
            conn.commit()
        logger.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

def log_request(requested_model: str, target_model: str, provider: str, latency_ms: int, status_code: int, tokens_in: int = 0, tokens_out: int = 0):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            total = tokens_in + tokens_out
            cursor.execute('''
                INSERT INTO request_logs (timestamp, requested_model, target_model, provider, latency_ms, status_code, tokens_in, tokens_out, total_tokens)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), requested_model, target_model, provider, latency_ms, status_code, tokens_in, tokens_out, total))
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to log request to DB: {e}")
