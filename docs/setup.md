# Local setup (Phase 1–3, mocked Gmail/Calendar/Telegram, real OpenAI)

## MCP server

```bash
cd services/mcp-server
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # JARVIS_MCP_TOKEN=dev-token is fine for local dev
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
cp .env.example .env   # set OPENAI_API_KEY=sk-... ; JARVIS_MCP_TOKEN must match mcp-server's
.venv/bin/uvicorn app.main:app --port 8000
```

Verify:

```bash
curl localhost:8000/health
curl -X POST localhost:8000/run/good-morning
```

This returns a real OpenAI-generated daily brief built from mocked
Gmail/Calendar/task data (see `services/mcp-server/app/tools/*.py`). The run
and the brief persist locally to `apps/agent-api/agent_api.db`, and every
MCP tool call is logged to `services/mcp-server/mcp_server.db`.

## Swapping mocks for real integrations later

Each tool's mock implementation lives in one function in
`services/mcp-server/app/tools/`. Replacing it with a real API call (Gmail,
Calendar, Telegram) means changing only that function body — the registry
entry, risk level, and return shape stay the same, so nothing in
`apps/agent-api` needs to change. See `task.md` Phases 4–6 for the order
those swaps happen in.
