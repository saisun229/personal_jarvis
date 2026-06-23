from fastapi import Header, HTTPException

from app.config import JARVIS_MCP_TOKEN


async def require_bearer_token(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer ") or authorization.removeprefix("Bearer ") != JARVIS_MCP_TOKEN:
        raise HTTPException(status_code=401, detail="missing or invalid bearer token")
