from app.mcp_client import call_tool


def gather() -> dict:
    today = call_tool("calendar.list_today")
    upcoming = call_tool("calendar.list_next_7_days")
    free_blocks = call_tool("calendar.find_free_blocks")
    return {
        "today_events": today.get("events", []),
        "upcoming_events": upcoming.get("events", []),
        "free_blocks": free_blocks.get("free_blocks", []),
    }
