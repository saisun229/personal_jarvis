from app.db import client
from app.registry import RISK_PRIVATE_WRITE, RISK_READ_ONLY, tool


@tool("memory.write", risk_level=RISK_PRIVATE_WRITE)
def write(params: dict) -> dict:
    row = (
        client.table("memories")
        .insert({"type": params.get("type", "note"), "content": params.get("content", ""), "metadata": params.get("metadata", {})})
        .execute()
    )
    return {"id": row.data[0]["id"], "status": "written"}


@tool("memory.search_recent", risk_level=RISK_READ_ONLY)
def search_recent(params: dict) -> dict:
    limit = params.get("limit", 5)
    rows = client.table("memories").select("id, type, content, created_at").order("created_at", desc=True).limit(limit).execute()
    return {"memories": rows.data}
