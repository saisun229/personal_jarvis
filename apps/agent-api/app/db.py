import json
import sqlite3
import uuid
from datetime import datetime, timezone

from app.config import AGENT_DB_PATH

_SCHEMA = """
create table if not exists agent_runs (
    id text primary key,
    run_type text not null,
    status text not null,
    input text,
    output text,
    error text,
    created_at text not null,
    updated_at text not null
);

create table if not exists daily_briefs (
    id text primary key,
    brief_date text not null,
    summary text not null,
    payload text,
    created_at text not null
);
"""


def get_conn():
    conn = sqlite3.connect(AGENT_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(_SCHEMA)
    conn.commit()
    conn.close()


def create_run(run_type: str, input_data: dict) -> str:
    run_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    conn.execute(
        "insert into agent_runs (id, run_type, status, input, output, error, created_at, updated_at) "
        "values (?, ?, 'running', ?, null, null, ?, ?)",
        (run_id, run_type, json.dumps(input_data), now, now),
    )
    conn.commit()
    conn.close()
    return run_id


def complete_run(run_id: str, output_data: dict | None = None, error: str | None = None):
    status = "failed" if error else "completed"
    conn = get_conn()
    conn.execute(
        "update agent_runs set status = ?, output = ?, error = ?, updated_at = ? where id = ?",
        (status, json.dumps(output_data) if output_data is not None else None, error, datetime.now(timezone.utc).isoformat(), run_id),
    )
    conn.commit()
    conn.close()


def save_daily_brief(brief_date: str, summary: str, payload: dict) -> str:
    brief_id = str(uuid.uuid4())
    conn = get_conn()
    conn.execute(
        "insert into daily_briefs (id, brief_date, summary, payload, created_at) values (?, ?, ?, ?, ?)",
        (brief_id, brief_date, summary, json.dumps(payload), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return brief_id
