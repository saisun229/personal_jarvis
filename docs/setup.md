# Local setup

Real OpenAI, real Supabase storage, real Gmail/Calendar via Google OAuth, a
working web dashboard. Telegram is the only thing still mocked (Phase 6,
skipped for now). See `docs/how-it-works.md` for how the pieces fit
together and `task.md` for phase-by-phase status.

## Prerequisites

- A Supabase project with `infra/supabase/schema.sql` already run in its
  SQL Editor (creates `integrations`, `agent_runs`, `tool_calls`,
  `daily_briefs`, `tasks`, `memories`, `approvals`).
- A Google Cloud OAuth client (Web application) with `gmail.readonly` and
  `calendar.readonly` added under OAuth consent screen → Data Access, and
  your redirect URI registered (see `docs/how-it-works.md` for the gotchas).

## MCP server

```bash
cd services/mcp-server
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # set SUPABASE_URL/KEY, GOOGLE_CLIENT_ID/SECRET, GOOGLE_REDIRECT_URI
.venv/bin/uvicorn app.main:app --port 8001
```

Connect your Google account once (only needed the first time, or after
revoking access): visit `http://localhost:8001/auth/google/start` in a
browser and approve the consent screen.

Verify:

```bash
curl localhost:8001/health
curl -H "Authorization: Bearer dev-token" localhost:8001/tools
```

## Web dashboard (build before starting agent-api)

```bash
cd apps/web
npm install
npm run build   # static export -> apps/web/out, served by agent-api below
```

## Agent API (serves both the API and the built dashboard)

```bash
cd apps/agent-api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # set OPENAI_API_KEY, SUPABASE_URL/KEY; JARVIS_MCP_TOKEN must match mcp-server's
.venv/bin/uvicorn app.main:app --port 8000
```

Open `http://localhost:8000/` for the dashboard, or verify with curl:

```bash
curl localhost:8000/api/health
curl -X POST localhost:8000/api/run/good-morning
```

This returns a real OpenAI-generated daily brief built from your actual
Gmail and Calendar. The run and brief persist to Supabase (`agent_runs`,
`daily_briefs`), and every MCP tool call is logged to `tool_calls` there too.

## Architecture note: why the dashboard has no server of its own

`apps/web` builds to static HTML/JS (`output: "export"` in
`next.config.ts`) instead of running its own Next.js server. `agent-api`
mounts that `out/` directory as static files *after* registering its
`/api/*` routes, so one FastAPI process serves both — no CORS, no second
port to manage when deploying. If you change frontend code, re-run
`npm run build` in `apps/web` and restart (or just refresh, if agent-api is
already running and picks up the new `out/` contents) agent-api.

## Swapping mocks for real integrations later

Each tool's mock implementation lives in one function in
`services/mcp-server/app/tools/`. Replacing it with a real API call means
changing only that function body — the registry entry, risk level, and
return shape stay the same, so nothing in `apps/agent-api` needs to change.
`telegram.py` is the one tool still mocked.
