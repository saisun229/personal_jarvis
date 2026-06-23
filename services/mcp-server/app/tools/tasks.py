import uuid
from datetime import datetime, timezone

from app.db import get_conn
from app.registry import RISK_PRIVATE_WRITE, RISK_READ_ONLY, tool


@tool("tasks.list_open_tasks", risk_level=RISK_READ_ONLY)
def list_open_tasks(params: dict) -> dict:
    conn = get_conn()
    rows = conn.execute("select id, title, description, source, status, priority, created_at from tasks where status = 'open' order by created_at desc").fetchall()
    conn.close()
    return {"tasks": [dict(row) for row in rows]}


@tool("tasks.create_private_task", risk_level=RISK_PRIVATE_WRITE)
def create_private_task(params: dict) -> dict:
    task_id = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "insert into tasks (id, title, description, source, status, priority, created_at) values (?, ?, ?, ?, 'open', ?, ?)",
        (
            task_id,
            params.get("title", "Untitled task"),
            params.get("description"),
            params.get("source", "jarvis"),
            params.get("priority"),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    return {"id": task_id, "status": "created"}


@tool("tasks.complete_task", risk_level=RISK_PRIVATE_WRITE)
def complete_task(params: dict) -> dict:
    conn = get_conn()
    conn.execute("update tasks set status = 'done' where id = ?", (params.get("id"),))
    conn.commit()
    conn.close()
    return {"id": params.get("id"), "status": "done"}
