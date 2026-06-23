from app.db import client
from app.registry import RISK_PRIVATE_WRITE, RISK_READ_ONLY, tool


@tool("tasks.list_open_tasks", risk_level=RISK_READ_ONLY)
def list_open_tasks(params: dict) -> dict:
    rows = client.table("tasks").select("*").eq("status", "open").order("created_at", desc=True).execute()
    return {"tasks": rows.data}


@tool("tasks.create_private_task", risk_level=RISK_PRIVATE_WRITE)
def create_private_task(params: dict) -> dict:
    row = (
        client.table("tasks")
        .insert(
            {
                "title": params.get("title", "Untitled task"),
                "description": params.get("description"),
                "source": params.get("source", "jarvis"),
                "status": "open",
                "priority": params.get("priority"),
            }
        )
        .execute()
    )
    return {"id": row.data[0]["id"], "status": "created"}


@tool("tasks.complete_task", risk_level=RISK_PRIVATE_WRITE)
def complete_task(params: dict) -> dict:
    client.table("tasks").update({"status": "done"}).eq("id", params.get("id")).execute()
    return {"id": params.get("id"), "status": "done"}
