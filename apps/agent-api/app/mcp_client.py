import httpx

from app.config import JARVIS_MCP_TOKEN, MCP_SERVER_URL


def call_tool(tool_name: str, params: dict | None = None) -> dict:
    response = httpx.post(
        f"{MCP_SERVER_URL}/tools/{tool_name}",
        json=params or {},
        headers={"Authorization": f"Bearer {JARVIS_MCP_TOKEN}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
