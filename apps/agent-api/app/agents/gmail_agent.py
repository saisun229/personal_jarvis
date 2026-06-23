from app.mcp_client import call_tool


def gather() -> dict:
    unread = call_tool("gmail.search_recent_unread")
    needing_reply = call_tool("gmail.search_needing_reply")
    return {
        "important_emails": unread.get("emails", []),
        "needs_reply": needing_reply.get("emails", []),
    }
