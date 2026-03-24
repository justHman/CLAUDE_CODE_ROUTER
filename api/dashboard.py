from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from core.db import DB_PATH
import os

router = APIRouter()
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"request": request})

@router.get("/api/stats")
async def get_stats():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) as calls, IFNULL(SUM(total_tokens), 0) as tokens, IFNULL(AVG(latency_ms), 0) as latency FROM request_logs")
            summary = dict(cur.fetchone())
            
            cur.execute("SELECT provider, COUNT(*) as calls FROM request_logs GROUP BY provider")
            providers = [dict(r) for r in cur.fetchall()]
            
            cur.execute("SELECT target_model as model, COUNT(*) as calls FROM request_logs GROUP BY target_model")
            models = [dict(r) for r in cur.fetchall()]
            
            cur.execute("SELECT timestamp, target_model, provider, latency_ms, status_code, tokens_out as tokens FROM request_logs ORDER BY timestamp DESC LIMIT 15")
            logs = [dict(r) for r in cur.fetchall()]
            
            return {
                "summary": summary,
                "providers": providers,
                "models": models,
                "recent_logs": logs
            }
    except Exception as e:
        return {"error": str(e)}
