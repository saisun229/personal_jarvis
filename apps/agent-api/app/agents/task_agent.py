from app.mcp_client import call_tool


def gather() -> dict:
    open_tasks = call_tool("tasks.list_open_tasks")
    return {"open_tasks": open_tasks.get("tasks", [])}


def create_suggested_task(title: str, description: str = "", priority: str = "medium"):
    return call_tool(
        "tasks.create_private_task",
        {"title": title, "description": description, "priority": priority, "source": "jarvis-daily-brief"},
    )
