from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.agents import chief_of_staff
from app.config import MCP_SERVER_URL, OPENAI_API_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL
from app.db import google_account_email, google_connected, init_db, latest_brief, list_runs, list_tool_calls

app = FastAPI(title="Jarvis Agent API")

WEB_OUT_DIR = Path(__file__).resolve().parents[2] / "web" / "out"


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/run/good-morning")
def run_good_morning():
    try:
        return chief_of_staff.run_good_morning()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/runs")
def get_runs():
    return {"runs": list_runs()}


@app.get("/api/briefs/latest")
def get_latest_brief():
    return latest_brief() or {}


@app.get("/api/tool-calls")
def get_tool_calls():
    return {"tool_calls": list_tool_calls()}


@app.get("/api/status")
def get_status():
    mcp_status = {"reachable": False, "google_credentials_configured": False, "telegram_configured": False}
    try:
        response = httpx.get(f"{MCP_SERVER_URL}/status", timeout=5)
        response.raise_for_status()
        mcp_status = {"reachable": True, **response.json()}
    except httpx.HTTPError:
        pass

    return {
        "openai_configured": bool(OPENAI_API_KEY),
        "supabase_configured": bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY),
        "mcp_server": mcp_status,
        "google_connected": google_connected(),
        "google_account_email": google_account_email(),
    }


# Mounted last so the /api/* routes above always take priority. This serves
# the Next.js static export (apps/web, built with `output: "export"`) from
# the same FastAPI process — one deployable service for API + dashboard.
if WEB_OUT_DIR.exists():
    app.mount("/", StaticFiles(directory=WEB_OUT_DIR, html=True), name="web")
