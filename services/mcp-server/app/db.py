from supabase import Client, create_client

from app.config import SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL

client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def init_db():
    pass


def log_tool_call(tool_name: str, risk_level: str, input_data: dict, output_data: dict | None, status: str, error: str | None = None):
    client.table("tool_calls").insert(
        {
            "tool_name": tool_name,
            "risk_level": risk_level,
            "input_summary": str(input_data)[:2000],
            "output_summary": str(output_data)[:2000] if output_data is not None else None,
            "status": status,
            "error": error,
        }
    ).execute()
