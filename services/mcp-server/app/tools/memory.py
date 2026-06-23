import json
import uuid
from datetime import datetime, timezone

from app.db import get_conn
from app.registry import RISK_PRIVATE_WRITE, RISK_READ_ONLY, tool


@tool("memory.write", risk_level=RISK_PRIVATE_WRITE)
def write(params: dict) -> dict:
    memory_id = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "insert into memories (id, type, content, metadata, created_at) values (?, ?, ?, ?, ?)",
        (
            memory_id,
            params.get("type", "note"),
            params.get("content", ""),
            json.dumps(params.get("metadata", {})),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    return {"id": memory_id, "status": "written"}


@tool("memory.search_recent", risk_level=RISK_READ_ONLY)
def search_recent(params: dict) -> dict:
    limit = params.get("limit", 5)
    conn = get_conn()
    rows = conn.execute("select id, type, content, created_at from memories order by created_at desc limit ?", (limit,)).fetchall()
    conn.close()
    return {"memories": [dict(row) for row in rows]}
