# personal_jarvis

A personal Jarvis-like AI agent: a daily-briefing agent that reads your
Gmail/Calendar through a dedicated tool server, summarizes it with OpenAI,
and serves the result through a small dashboard.

## Architecture

```
apps/web            — Next.js dashboard, built as a static export
apps/agent-api       — FastAPI. Orchestrates agents, calls OpenAI, serves
                        the dashboard, owns agent_runs/daily_briefs.
services/mcp-server  — FastAPI. The only thing holding external API
                        credentials (Google, Telegram); exposes them as
                        named "tools" agent-api calls over HTTP.
```

`agent-api` never holds a Google token directly — every external action
goes through one auditable chokepoint in `mcp-server`. See
[`docs/how-it-works.md`](docs/how-it-works.md) for the full design
rationale and request walkthrough.

## Getting started

- [`docs/setup.md`](docs/setup.md) — run both services locally.
- [`docs/deploy.md`](docs/deploy.md) — deploy to Fly.io via GitHub Actions.

## Auth, at a glance

- **Dashboard** (`apps/agent-api`): HTTP Basic Auth via `DASHBOARD_USERNAME`
  / `DASHBOARD_PASSWORD`. No-op if unset (local dev).
- **agent-api → mcp-server**: a shared bearer token, `JARVIS_MCP_TOKEN`.
- **Google**: OAuth2, scoped to `gmail.readonly` + `calendar.readonly`,
  stored in Supabase and refreshed automatically.

These are independent layers guarding different boundaries — see the
"Where auth comes in" section of
[`docs/how-it-works.md`](docs/how-it-works.md) for details.

## Status

Phase-by-phase build status lives in [`task.md`](task.md).
