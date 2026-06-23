from datetime import datetime, timezone

from supabase import Client, create_client

from app.config import SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL

_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def init_db():
    pass


def create_run(run_type: str, input_data: dict) -> str:
    now = datetime.now(timezone.utc).isoformat()
    row = (
        _client.table("agent_runs")
        .insert({"run_type": run_type, "status": "running", "input": input_data, "created_at": now, "updated_at": now})
        .execute()
    )
    return row.data[0]["id"]


def complete_run(run_id: str, output_data: dict | None = None, error: str | None = None):
    status = "failed" if error else "completed"
    _client.table("agent_runs").update(
        {"status": status, "output": output_data, "error": error, "updated_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", run_id).execute()


def save_daily_brief(brief_date: str, summary: str, payload: dict) -> str:
    row = (
        _client.table("daily_briefs")
        .insert({"brief_date": brief_date, "summary": summary, "payload": payload})
        .execute()
    )
    return row.data[0]["id"]


def list_runs(limit: int = 20) -> list[dict]:
    rows = _client.table("agent_runs").select("*").order("created_at", desc=True).limit(limit).execute()
    return rows.data


def latest_brief() -> dict | None:
    rows = _client.table("daily_briefs").select("*").order("created_at", desc=True).limit(1).execute()
    return rows.data[0] if rows.data else None


def list_tool_calls(limit: int = 50) -> list[dict]:
    rows = _client.table("tool_calls").select("*").order("created_at", desc=True).limit(limit).execute()
    return rows.data


def google_connected() -> bool:
    rows = _client.table("integrations").select("account_email").eq("provider", "google").execute()
    return len(rows.data) > 0


def google_account_email() -> str | None:
    rows = _client.table("integrations").select("account_email").eq("provider", "google").execute()
    return rows.data[0]["account_email"] if rows.data else None
