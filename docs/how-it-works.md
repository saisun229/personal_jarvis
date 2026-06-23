# How Jarvis works (Phases 1–5)

This explains what got built today and why it's shaped this way — written
as a learning reference, not just a changelog.

## The big picture

```
You (browser)
     │
     ▼
apps/web            — Next.js dashboard (Phase 7, not built yet)
     │  HTTP
     ▼
apps/agent-api       — FastAPI. Orchestrates agents, calls OpenAI, owns
     │                 agent_runs/daily_briefs.
     │  HTTP + Bearer token
     ▼
services/mcp-server  — FastAPI. The ONLY thing that holds external API
     │                 credentials (Google, Telegram) and talks to them.
     ▼
Gmail / Calendar / Telegram / Supabase
```

Three separate processes, three separate concerns. The rule that makes
this worth the extra complexity: **agent-api never sees a Google token, a
Telegram token, or raw SQL — it only ever calls named "tools" on the MCP
server.** Every external action goes through one chokepoint, which is what
makes risk policy and audit logging actually enforceable instead of just
"a convention everyone hopefully follows."

## What "MCP" means here

MCP (Model Context Protocol) is normally a standardized JSON-RPC-ish
protocol for exposing tools to an LLM agent. We didn't pull in the official
SDK — we hand-built something MCP-*shaped* because it's simpler to debug
today and the concepts transfer directly if we adopt the real SDK later.

Concretely, `services/mcp-server/app/registry.py` defines:

```python
@tool("gmail.search_recent_unread", risk_level=RISK_READ_ONLY)
def search_recent_unread(params: dict) -> dict:
    ...
```

The `@tool` decorator registers the function into a dict —
`TOOL_REGISTRY["gmail.search_recent_unread"] = Tool(name=..., risk_level=...,
handler=...)`. `services/mcp-server/app/main.py` exposes one generic HTTP
endpoint:

```
POST /tools/{tool_name}
```

which looks up the tool by name, checks its risk level isn't blocked
(`FINANCIAL`/`DESTRUCTIVE` are hard-disabled — see `registry.is_blocked`),
calls the handler, logs the call to the `tool_calls` table (name, risk
level, input, output, status, timestamp), and returns the result.

That's the whole "MCP server" idea distilled: **a single auditable front
door for every external action**, addressable by name, with every call
logged before the result goes anywhere. Adding a new tool means writing
one function and one decorator — nothing else changes.

## How a single Jarvis request actually flows

Walking through `POST /run/good-morning` end to end:

1. Your browser (eventually) or `curl` hits `apps/agent-api`'s
   `/run/good-morning`.
2. `agent-api/app/agents/chief_of_staff.py` creates an `agent_runs` row in
   Supabase (`status: running`) and starts calling MCP tools through
   `app/mcp_client.py` — a thin `httpx` wrapper that POSTs to
   `MCP_SERVER_URL/tools/<name>` with the shared bearer token.
3. Each call (`calendar.list_today`, `gmail.search_recent_unread`,
   `tasks.list_open_tasks`, `memory.search_recent`, ...) lands on the MCP
   server, which checks the bearer token, looks up the tool, runs it
   (calling the real Google APIs as of Phase 5), logs it, and returns JSON.
4. `chief_of_staff.py` assembles all those results into one `context`
   dict and hands it to `app/openai_client.py`, which sends it to OpenAI
   with the daily-briefing system prompt
   (`app/prompts/daily_brief.py`) and asks for a structured JSON brief back.
5. The brief gets written to `daily_briefs`, a `memory.write` tool call
   records "brief generated for today" (so future runs can reference it),
   and `telegram.send_message` is called (still mocked — Phase 6).
6. The `agent_runs` row is updated to `status: completed` with the brief
   as output, and the brief is returned to whoever called the endpoint.

Every box in that walk either reads Supabase, writes Supabase, or calls
exactly one MCP tool. There's no place where agent-api improvises a raw
API call to Google — that's the design constraint paying off.

## Where auth comes in — three separate, unrelated layers

This trips people up because "auth" means three different things here:

1. **Bearer token between agent-api and mcp-server** (`JARVIS_MCP_TOKEN`,
   currently `dev-token`). This is *machine-to-machine* auth — it just
   proves "this request came from our own agent-api, not a random caller
   on the internet." Checked in `services/mcp-server/app/auth.py`. It has
   nothing to do with your Google account.

2. **Google OAuth** (`services/mcp-server/app/google_oauth.py`) — this is
   *your* identity, granting the MCP server permission to read *your*
   Gmail/Calendar on your behalf. The flow:
   - `GET /auth/google/start` redirects your browser to Google's consent
     screen, requesting `gmail.readonly` + `calendar.readonly` scopes.
   - Google redirects back to `GET /auth/google/callback?code=...`.
   - The server exchanges that one-time `code` for an `access_token`
     (short-lived, ~1hr) and a `refresh_token` (long-lived), via a
     server-to-server POST to Google's token endpoint — this step needs
     `GOOGLE_CLIENT_SECRET`, which is why it has to happen on the backend,
     never in a browser.
   - Both tokens get stored in Supabase's `integrations` table.
   - Every real Gmail/Calendar tool call runs `get_valid_access_token()`
     first, which checks if the stored token is about to expire and
     silently calls Google's refresh endpoint if so — you only ever do the
     browser consent dance once (until you revoke access).
   - Gotcha we hit: Google **silently drops** scopes like
     `gmail.readonly` from the granted token unless they're explicitly
     enabled on the OAuth consent screen's "Data Access" page — even
     though our code requested them. The token still "works," it just
     quietly doesn't have the permission you think it has. Always check
     granted scopes with `https://oauth2.googleapis.com/tokeninfo` if a
     real API call comes back `403 insufficientPermissions`.

3. **Supabase service role key** — both agent-api and mcp-server hold this
   and use it to read/write every table directly, bypassing row-level
   security. That's safe *only* because both are trusted backend services
   that never expose this key to a browser. (If we ever add direct
   frontend-to-Supabase calls, that must use the separate, much more
   restricted `anon` key instead.)

None of these three auths know about each other. The bearer token doesn't
grant Google access; the Google token doesn't grant Supabase access. Each
one guards a different boundary in the architecture diagram above.

## Why mocks were the right starting point

Every external tool (`gmail.py`, `calendar.py`, `telegram.py`) was built
mock-first with the exact same function signature and return shape the
real implementation uses. That let Phases 1–3 prove the *orchestration*
(agent-api → MCP → OpenAI → storage) worked correctly before any real
credential existed, and meant swapping in Supabase (Phase 4) and Google
(Phase 5) later touched only the inside of one function each time — nothing
in `chief_of_staff.py` or the prompt logic ever had to change.
