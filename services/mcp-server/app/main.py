from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import require_bearer_token
from app.db import init_db, log_tool_call
from app.google_oauth import build_auth_url, exchange_code_for_tokens
from app.registry import TOOL_REGISTRY, is_blocked

# Import tool modules so their @tool decorators register into TOOL_REGISTRY.
from app.tools import calendar, gmail, memory, tasks, telegram  # noqa: F401

app = FastAPI(title="Jarvis MCP Server")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


# Human-driven browser flow (owner-only, single-user deployment) — not
# behind the bearer token used for machine-to-machine tool calls.
@app.get("/auth/google/start")
def google_auth_start():
    return RedirectResponse(build_auth_url())


@app.get("/auth/google/callback")
def google_auth_callback(code: str):
    account_email = exchange_code_for_tokens(code)
    return HTMLResponse(f"<h1>Connected</h1><p>Google account linked: {account_email}</p>")


@app.get("/tools", dependencies=[Depends(require_bearer_token)])
def list_tools():
    return {name: t.risk_level for name, t in TOOL_REGISTRY.items()}


@app.post("/tools/{tool_name}", dependencies=[Depends(require_bearer_token)])
def call_tool(tool_name: str, params: dict | None = None):
    params = params or {}
    tool_def = TOOL_REGISTRY.get(tool_name)
    if tool_def is None:
        raise HTTPException(status_code=404, detail=f"unknown tool: {tool_name}")

    if is_blocked(tool_def.risk_level):
        log_tool_call(tool_name, tool_def.risk_level, params, None, status="blocked")
        raise HTTPException(status_code=403, detail=f"tool '{tool_name}' is disabled (risk level {tool_def.risk_level})")

    try:
        result = tool_def.handler(params)
    except Exception as exc:
        log_tool_call(tool_name, tool_def.risk_level, params, None, status="error", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))

    log_tool_call(tool_name, tool_def.risk_level, params, result, status="ok")
    return result
