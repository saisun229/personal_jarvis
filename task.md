# Task Plan — Jarvis V1 "Daily Command Center" (MVP)

See [final_goal.md](final_goal.md) for the long-term vision. This file tracks
the concrete path to a working MVP, broken into small, independently
verifiable phases. Each phase has a single owner-checkable "done means" line
— don't move to the next phase until that's true.

## Current status (2026-06-23)

Decisions locked in for this build:

- **Local-first**: every phase below is built and verified on localhost
  before any cloud deploy. Deploy is its own later phase.
- **Enterprise 3-service shape, kept as-is**: Next.js web app, FastAPI agent
  API, separate FastAPI MCP server — for the learning value, not because the
  MVP strictly needs 3 services.
- **Credentials available now**: OpenAI key, Supabase project, Google OAuth
  (connected, real Gmail/Calendar data flowing). Telegram bot is **not** set
  up yet (explicitly deferred by the user) — `telegram.send_message` stays
  mocked until Phase 6.
- Phases 1–5 and 7 are done: real OpenAI, real Supabase storage, real
  Gmail + Calendar reads, and a working web dashboard, all verified
  end-to-end. Phase 6 (Telegram) is intentionally skipped for now — only
  `telegram.send_message` remains mocked. See `docs/how-it-works.md` for a
  walkthrough of how the pieces fit together.

## Phase list (MVP)

### Phase 1 — Repo scaffold ✅ done
Create the monorepo layout (`apps/web`, `apps/agent-api`,
`services/mcp-server`, `packages/shared`, `infra/supabase`, `docs`) with
minimal placeholder files (package.json / requirements.txt / Dockerfile
stubs where relevant). No logic yet.
**Done means:** directory tree exists; `apps/agent-api` and
`services/mcp-server` each have a runnable (even if trivial) FastAPI app
that serves `/health`.

### Phase 2 — MCP server with mocked tools ✅ done
Build the MCP server: bearer-token auth middleware, a tool registry, and
stub implementations of:
`gmail.search_recent_unread`, `gmail.search_needing_reply`,
`calendar.list_today`, `calendar.list_next_7_days`, `calendar.find_free_blocks`,
`tasks.list_open_tasks`, `tasks.create_private_task`, `memory.search_recent`,
`memory.write`, `telegram.send_message`.
Each returns realistic fake JSON. Every call is logged to a local file or
SQLite table (`tool_calls`) with tool name, risk level, status, timestamp.
**Done means:** `curl` with a valid bearer token against every tool above
returns mock JSON; a request with no/bad token returns 401; the log file/
table has one row per call made.

### Phase 3 — Agent API orchestration (mocked data, real OpenAI) ✅ done
Build the Agent API: MCP HTTP client, the four logical agents
(`ChiefOfStaffAgent`, `GmailAgent`, `CalendarAgent`, `TaskAgent`) as plain
functions, and `POST /run/good-morning`. The flow calls every MCP tool from
Phase 2, assembles context, sends it to OpenAI with the daily-briefing
prompt (including the "external content is data, not instructions" rule),
and returns the structured brief. Store the run (`agent_runs` row) and the
brief (`daily_briefs` row) — locally (SQLite/JSON) for now, schema-compatible
with the future Supabase tables in `infra/supabase/schema.sql`.
**Done means:** `curl -X POST localhost:.../run/good-morning` returns a real,
readable daily brief generated from the mock Gmail/Calendar/task data, and a
row is persisted with that output.

### Phase 4 — Supabase swap-in ✅ done
Stood up a real Supabase project, ran `infra/supabase/schema.sql`
(integrations, agent_runs, tool_calls, daily_briefs, tasks, memories,
approvals), and swapped the local SQLite storage in both services for the
Supabase client behind the same function names.
**Done means:** same `/run/good-morning` call as Phase 3 now produces rows
visible in the Supabase table editor; local storage code path removed.
*Verified: `agent_runs`, `daily_briefs`, `tool_calls`, and `memories` rows
confirmed via direct REST query against the real Supabase project.*

### Phase 5 — Google OAuth + real Gmail/Calendar read ✅ done
Added the Google OAuth flow directly on the MCP server (`GET
/auth/google/start` + `/auth/google/callback`, since the dashboard doesn't
exist yet) storing access+refresh tokens in the `integrations` table, and
swapped the Gmail/Calendar MCP tools from mock data to real
`gmail.readonly` / `calendar.readonly` API calls using those tokens, with
auto-refresh in `google_oauth.get_valid_access_token()`.
Two gotchas hit and resolved along the way: (1) in a Codespace, the OAuth
redirect URI must be the forwarded `https://<codespace>-8001.app.github.dev`
URL, not `localhost`; (2) Google silently drops sensitive scopes
(gmail.readonly/calendar.readonly) from the granted token unless they're
explicitly added under OAuth consent screen → Data Access, even if
requested in the auth URL.
**Done means:** `/run/good-morning` produces a brief built from my actual
inbox and calendar for today.

### Phase 6 — Telegram alert ⏭ skipped for now (by user's choice)
Create a Telegram bot, store `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID`, and
wire `telegram.send_message` to the real Telegram API. ChiefOfStaffAgent
sends the finished brief there. `telegram.send_message` stays mocked
(logs what it would send) until this is picked back up.
**Done means:** running `/run/good-morning` results in a real Telegram
message arriving in my chat within seconds.

### Phase 7 — Web dashboard ✅ done
Built the Next.js dashboard (`apps/web`) as a **static export**
(`output: "export"` in `next.config.ts`) rather than its own running
server — `next build` produces `apps/web/out/`, and `apps/agent-api`
mounts that directory as static files (`StaticFiles(..., html=True)`)
after all its `/api/*` routes. One deployable service serves both the API
and the dashboard; no CORS, no second port to manage in production.
Pages: `/` (latest brief + trigger button), `/runs`, `/tool-logs`,
`/settings` (connection status only, no secrets rendered). All four fetch
client-side from `/api/...` (same origin).
**Done means:** open the dashboard, click "Run good morning", watch the
brief/runs/tool-logs populate without touching curl.
*Verified: built `out/`, confirmed FastAPI serves `/`, `/runs/`,
`/tool-logs/`, `/settings/` plus all `/api/*` routes from one process on
port 8000; checked visually in the browser via the Codespace forwarded URL.*

### Phase 8 — Deploy ✅ done — live at jarvis-agent-api.fly.dev
Two services deployed (not three): `apps/agent-api` (Dockerfile
multi-stage builds `apps/web` into a static export, then bundles it with
the Python app) and `services/mcp-server`, both on Fly.io. Fly apps
created, secrets set on both (fresh production `JARVIS_MCP_TOKEN`, not
`dev-token`), `FLY_API_TOKEN` added as a GitHub repo secret.
`.github/workflows/deploy.yml` runs on every push to `master` and
redeploys both via `flyctl deploy`.
Real bug hit and fixed: `flyctl` resolves a `fly.toml`'s `dockerfile`
path relative to the directory *containing that `fly.toml`*, not the
build context — both configs had to move to the repo root
(`fly.mcp-server.toml`, `fly.agent-api.toml`) instead of living next to
each service. Documented in `docs/deploy.md`.
**Done means:** the same end-to-end flow works against public
`*.fly.dev` URLs, not just localhost, and a routine push to `master`
redeploys both services without manual steps.
*Verified: `POST https://jarvis-agent-api.fly.dev/api/run/good-morning`
returned a real brief built from live Gmail/Calendar through the
deployed `jarvis-mcp-server.fly.dev`, persisted to Supabase.*

## Explicitly deferred past MVP
Approval queue UI, follow-up detector heuristics, meeting prep, GitHub
integration, Gmail draft/send, scheduled/cron runs, token encryption
hardening, formal MCP OAuth — all later phases per final_goal.md. Plaid,
trading, WhatsApp/Facebook/LinkedIn, voice, home automation, multi-user auth
are out of scope for the MVP entirely.

---

## Today's plan (2026-06-23)

Given what's ready (OpenAI key only, no Google/Supabase/Telegram yet), today
is **Phase 1 → Phase 3**, stopping once `/run/good-morning` produces a real
OpenAI-generated brief end-to-end from mocked tool data. That's the proof
that the architecture and orchestration work; everything after is swapping
mock implementations for real ones, one credential at a time.

- [x] **1a.** Scaffold monorepo dirs + trivial `/health` in agent-api and
      mcp-server. *Verified: both `/health` respond 200 via curl.*
- [x] **1b.** `infra/supabase/schema.sql` written (not yet applied anywhere —
      just the source of truth for table shapes used in Phase 3's local
      storage and Phase 4's real Supabase).
- [x] **2a.** MCP server bearer-auth middleware + tool registry pattern.
      *Verified: tool call without bearer token → 401; with valid token → 200.*
- [x] **2b.** Implemented the 10 mock tools (gmail x2, calendar x3, tasks x3,
      memory x2, telegram x1) with realistic fake payloads + tool_call
      logging to SQLite. *Verified via curl + sqlite3 query on tool_calls.*
- [x] **3a.** Agent API MCP client + the four agent functions
      (`gmail_agent`, `calendar_agent`, `task_agent`, `chief_of_staff`),
      calling all 10 mock tools and assembling one context object.
- [x] **3b.** Daily-briefing OpenAI prompt + `POST /run/good-morning` wiring
      it all together, persisting the run+brief locally.
      *Verified: `curl -X POST localhost:8000/run/good-morning` returned a
      real, structured OpenAI-generated brief; rows confirmed in
      `agent_runs`/`daily_briefs` (agent-api) and `tool_calls` (mcp-server).*

**Today's goal reached: Phases 1–3 done and verified end-to-end.** Real
Gmail/Calendar/Telegram are still mocked (no Google OAuth app / Telegram bot
created yet) — swapping those in is Phases 4–6, one credential at a time,
without touching `apps/agent-api` (see `docs/setup.md`).
