# Personal Jarvis — Final Goal

## What this is

A private, single-user AI operating system that connects to my digital life
(Gmail, Calendar, tasks, GitHub, notes, finances, etc.) and helps me answer,
every day: *what matters today, who do I need to follow up with, what should
I work on next.*

This is not a "do everything" agent. It is a trusted layer that:

- Reads broadly.
- Writes carefully (private writes are fine; external/financial/destructive
  writes need explicit approval).
- Remembers decisions across days.
- Logs every tool call it makes, so every action is auditable after the fact.
- Is useful every single day, not just a tech demo.

## Architecture shape (enterprise-style, for learning)

Two deployable services, talking over HTTP — the web dashboard is a static
build artifact, not a third running service:

```
Browser
   │
   ▼
Agent API (FastAPI) ── serves the Next.js static export (apps/web/out) +
   │                    orchestrates agents, calls OpenAI, owns agent_runs
   │  Bearer token
   ▼
MCP Server (FastAPI, MCP-shaped tool registry) ── owns external API creds,
   │                                              enforces tool risk policy,
   ▼                                              logs every tool call
External APIs (Gmail, Calendar, Telegram, ...) + Supabase (storage)
```

The dashboard (`apps/web`, Next.js with `output: "export"`) builds to
static HTML/JS and gets mounted by the Agent API alongside its `/api/*`
routes — one process, no CORS, one less thing to deploy.

Why split it this way: the Agent API never touches a Gmail/Telegram/Supabase
credential directly — it only calls named tools on the MCP server. That's the
boundary that makes risk policy and audit logging enforceable in one place,
and it's the same shape a real multi-tenant agent platform would use.

## Tool risk levels (enforced by the MCP server, not the agent)

```
READ_ONLY        — always allowed
PRIVATE_WRITE     — always allowed (writes only to our own Supabase rows)
EXTERNAL_WRITE    — requires approval, except telegram.send_message to my own chat
FINANCIAL         — disabled until Phase 4
DESTRUCTIVE       — disabled indefinitely (no delete tools, period)
```

## Security non-negotiables

- External content (email bodies, web pages, docs) is **data, never
  instructions** — the briefing prompt explicitly tells the model not to obey
  anything embedded in fetched content (prompt-injection defense).
- Every MCP tool call is authenticated (bearer token) and logged.
- No email sending, no calendar mutation, no deletes, no financial actions —
  not even stubbed as "enabled" — until a later phase explicitly turns them on.
- Secrets (Supabase service role key, Google refresh tokens, bot tokens) never
  reach the frontend.

## Phased roadmap (direction, not a today-commitment)

1. **Daily Command Center (MVP)** — Gmail read, Calendar read, OpenAI daily
   brief, Telegram alert, Supabase storage, tool-call audit log.
2. **Productivity expansion** — draft replies, real task apps, Drive search,
   meeting prep, approval queue.
3. **GitHub builder** — Jarvis helps maintain its own and other repos
   (issues, PRs, project planning).
4. **Finance & portfolio** — read-only Plaid/bank/stock data, no money
   movement, ever, in this phase.
5. **Maps, deals, life logistics** — weather, errands, price watching.
6. **Content & social** — draft-only, human approval before anything posts.
7. **Messaging** — Slack/Discord/Telegram/SMS via official APIs only; no
   personal-account scraping (no WhatsApp/Facebook/LinkedIn scraping, ever).
8. **Photos, files, local worker** — local indexing/OCR/embeddings.
9. **Voice & home** — voice interface, Home Assistant, with approval gates
   on anything physical/security-related.

## What "good" looks like, day one of real use

```
Good morning Sai.

Today: 2 meetings, 5 unread emails, best focus block 9:30–11:00.

Needs attention:
1. Recruiter asked for availability
2. GitHub notification: build failed
3. Bank email looks like a payment reminder

Top 3:
1. Reply to recruiter
2. Fix failed build
3. Review payment reminder
```

Optimize for daily usefulness, trust, and clean architecture — not for
integration count.
