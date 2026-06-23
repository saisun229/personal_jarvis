# Local setup (Phases 1–4: mocked Gmail/Calendar/Telegram, real OpenAI + Supabase)

## Prerequisites

A Supabase project with `infra/supabase/schema.sql` already run in its SQL
Editor (creates `integrations`, `agent_runs`, `tool_calls`, `daily_briefs`,
`tasks`, `memories`, `approvals`).

## MCP server

```bash
cd services/mcp-server
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # set SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY; JARVIS_MCP_TOKEN=dev-token is fine for local dev
.venv/bin/uvicorn app.main:app --port 8001
```

Verify:

```bash
curl localhost:8001/health
curl -H "Authorization: Bearer dev-token" localhost:8001/tools
```

## Agent API

```bash
cd apps/agent-api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # set OPENAI_API_KEY, SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY; JARVIS_MCP_TOKEN must match mcp-server's
.venv/bin/uvicorn app.main:app --port 8000
```

Verify:

```bash
curl localhost:8000/health
curl -X POST localhost:8000/run/good-morning
```

This returns a real OpenAI-generated daily brief built from mocked
Gmail/Calendar/task data (see `services/mcp-server/app/tools/*.py`). The run
and the brief persist to the `agent_runs`/`daily_briefs` tables in Supabase,
and every MCP tool call is logged to `tool_calls` there too.

## Swapping mocks for real integrations later

Each tool's mock implementation lives in one function in
`services/mcp-server/app/tools/`. Replacing it with a real API call (Gmail,
Calendar, Telegram) means changing only that function body — the registry
entry, risk level, and return shape stay the same, so nothing in
`apps/agent-api` needs to change. See `task.md` Phases 5–6 for the order
those swaps happen in.
