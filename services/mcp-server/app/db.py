import json
import sqlite3
import uuid
from datetime import datetime, timezone

from app.config import MCP_DB_PATH

_SCHEMA = """
create table if not exists tool_calls (
    id text primary key,
    tool_name text not null,
    risk_level text not null,
    input_summary text,
    output_summary text,
    status text not null,
    error text,
    created_at text not null
);

create table if not exists tasks (
    id text primary key,
    title text not null,
    description text,
    source text,
    status text default 'open',
    priority text,
    created_at text not null
);

create table if not exists memories (
    id text primary key,
    type text not null,
    content text not null,
    metadata text,
    created_at text not null
);
"""


def get_conn():
    conn = sqlite3.connect(MCP_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(_SCHEMA)
    conn.commit()
    conn.close()


def log_tool_call(tool_name: str, risk_level: str, input_data: dict, output_data: dict | None, status: str, error: str | None = None):
    conn = get_conn()
    conn.execute(
        "insert into tool_calls (id, tool_name, risk_level, input_summary, output_summary, status, error, created_at) "
        "values (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            str(uuid.uuid4()),
            tool_name,
            risk_level,
            json.dumps(input_data)[:2000],
            json.dumps(output_data)[:2000] if output_data is not None else None,
            status,
            error,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()
