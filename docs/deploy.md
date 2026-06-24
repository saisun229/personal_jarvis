# Deploying to Fly.io

Every push to `master` runs `.github/workflows/deploy.yml`, which deploys
`services/mcp-server` and `apps/agent-api` (which also serves the built
`apps/web` dashboard) to Fly.io as two separate apps:
**https://jarvis-mcp-server.fly.dev** and **https://jarvis-agent-api.fly.dev**.

Both are already created and live as of the first manual deploy. This doc
is the reference for what was done and what's needed if you ever rebuild
this from scratch (new Fly account, rotated token, etc).

## One-time account setup

1. **Fly.io account** (card required even for the free allowance — two
   `shared-cpu-1x`/256mb apps with `min_machines_running = 0` (scale to
   zero when idle) cost close to nothing for personal use).

2. **Install flyctl**, get an API token from the Fly dashboard (Account →
   Access Tokens — note: tokens created this way are *limited* tokens and
   can't mint further child tokens via `flyctl tokens create`, but they
   work fine for `flyctl deploy`/`apps create`/`secrets set`, which is all
   we need):
   ```bash
   curl -L https://fly.io/install.sh | sh
   export FLY_API_TOKEN="<paste token>"
   ```

3. **Create the two apps** (names are globally unique on Fly — if taken,
   pick something else and update `app = "..."` in the matching
   `fly.<service>.toml` at the repo root):
   ```bash
   flyctl apps create jarvis-mcp-server
   flyctl apps create jarvis-agent-api
   ```

4. **Set secrets** on each (`JARVIS_MCP_TOKEN` must be a real random value,
   not `dev-token`, and must match exactly between the two apps):
   ```bash
   flyctl secrets set -a jarvis-mcp-server \
     JARVIS_MCP_TOKEN="<random string>" \
     SUPABASE_URL="https://<project>.supabase.co" \
     SUPABASE_SERVICE_ROLE_KEY="<service role key>" \
     GOOGLE_CLIENT_ID="<client id>" \
     GOOGLE_CLIENT_SECRET="<client secret>" \
     GOOGLE_REDIRECT_URI="https://jarvis-mcp-server.fly.dev/auth/google/callback"

   flyctl secrets set -a jarvis-agent-api \
     OPENAI_API_KEY="<openai key>" \
     MCP_SERVER_URL="https://jarvis-mcp-server.fly.dev" \
     JARVIS_MCP_TOKEN="<same random string as above>" \
     SUPABASE_URL="https://<project>.supabase.co" \
     SUPABASE_SERVICE_ROLE_KEY="<service role key>"
   ```

5. **Add the same Fly API token as a GitHub secret** so Actions can deploy:
   repo → Settings → Secrets and variables → Actions → New repository
   secret → name `FLY_API_TOKEN` → paste the same token from step 2.
   (We didn't bother minting a separate "deploy-only" token — see the note
   in step 2; reusing the limited dashboard token is fine here.)

6. Push to `master`. Actions tab → two jobs, `deploy-mcp-server` and
   `deploy-agent-api`.

## A real bug hit during setup: `fly.toml` location matters

`flyctl` resolves the `[build] dockerfile` path in `fly.toml` **relative to
the directory containing that `fly.toml` file** — always, regardless of
`--config`'s path or the cwd. Having `services/mcp-server/fly.toml` point
at `dockerfile = "services/mcp-server/Dockerfile"` double-prefixes the
path and fails with "dockerfile not found". Fix: both `fly.toml` files now
live at the **repo root** as `fly.mcp-server.toml` and `fly.agent-api.toml`
— `dockerfile` paths inside them stay relative to root, which also happens
to be required anyway for `apps/agent-api`'s Dockerfile, since it needs to
reach into the sibling `apps/web/` directory and a context scoped to
`apps/agent-api/` couldn't see it.

## Google OAuth note

The refresh token already stored in Supabase keeps working on the
deployed server without re-doing the consent flow — the redirect URI is
only checked during the initial authorization-code exchange, not on
token refresh. Only add
`https://jarvis-mcp-server.fly.dev/auth/google/callback` to the OAuth
client's Authorized redirect URIs in Google Cloud Console if you ever
need to redo consent (e.g. after revoking access).

## What "every commit deploys" means in practice

Every push to `master` redeploys *both* services, even if only one
changed — simplest correct behavior for a two-service personal project.
If this gets noisy later, the workflow can add `paths:` filters per job so
e.g. a dashboard-only change skips redeploying `mcp-server`.

## Rotating `JARVIS_MCP_TOKEN`

Update the secret on *both* Fly apps in the same breath
(`flyctl secrets set -a <app> JARVIS_MCP_TOKEN=...`), or agent-api's calls
to mcp-server will start failing with 401s until both match again.
