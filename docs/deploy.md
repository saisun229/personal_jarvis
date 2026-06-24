# Deploying to Fly.io

Every push to `master` runs `.github/workflows/deploy.yml`, which deploys
`services/mcp-server` and `apps/agent-api` (which also serves the built
`apps/web` dashboard) to Fly.io as two separate apps. This is a one-time
setup; after it's done, deploys are automatic.

## One-time setup (you)

1. **Create a Fly.io account** at fly.io (a card is required even for the
   free allowance, but two `shared-cpu-1x`/256mb apps that mostly idle
   should cost close to nothing).

2. **Install flyctl** locally and log in:
   ```bash
   curl -L https://fly.io/install.sh | sh
   fly auth login
   ```

3. **Create the two apps** (names must be globally unique on Fly — if
   `jarvis-mcp-server` or `jarvis-agent-api` are taken, pick something else
   and update the `app = "..."` line in the matching `fly.toml`):
   ```bash
   fly apps create jarvis-mcp-server
   fly apps create jarvis-agent-api
   ```

4. **Set secrets on `jarvis-mcp-server`** (same Google/Supabase values
   already in `services/mcp-server/.env` locally):
   ```bash
   fly secrets set -a jarvis-mcp-server \
     JARVIS_MCP_TOKEN="<pick a long random string, not dev-token>" \
     SUPABASE_URL="https://<project>.supabase.co" \
     SUPABASE_SERVICE_ROLE_KEY="<service role key>" \
     GOOGLE_CLIENT_ID="<client id>" \
     GOOGLE_CLIENT_SECRET="<client secret>" \
     GOOGLE_REDIRECT_URI="https://jarvis-mcp-server.fly.dev/auth/google/callback"
   ```

5. **Set secrets on `jarvis-agent-api`** — `JARVIS_MCP_TOKEN` must be the
   *exact same value* you set on `jarvis-mcp-server` above:
   ```bash
   fly secrets set -a jarvis-agent-api \
     OPENAI_API_KEY="<openai key>" \
     MCP_SERVER_URL="https://jarvis-mcp-server.fly.dev" \
     JARVIS_MCP_TOKEN="<same long random string as step 4>" \
     SUPABASE_URL="https://<project>.supabase.co" \
     SUPABASE_SERVICE_ROLE_KEY="<service role key>"
   ```

6. **(Only if you ever need to redo the Google consent flow on the deployed
   server)** add `https://jarvis-mcp-server.fly.dev/auth/google/callback`
   to the OAuth client's Authorized redirect URIs in Google Cloud Console.
   Not needed for the first deploy — the refresh token already stored in
   Supabase keeps working regardless of which host calls Google's token
   endpoint; the redirect URI is only checked during the initial consent
   exchange.

7. **Create a Fly API token and add it as a GitHub secret**:
   ```bash
   fly tokens create deploy -x 999999h
   ```
   Copy the output, then in GitHub: repo → Settings → Secrets and
   variables → Actions → New repository secret → name it `FLY_API_TOKEN`,
   paste the value.

8. Push to `master`. Watch the run under the repo's Actions tab — two jobs,
   `deploy-mcp-server` and `deploy-agent-api`.

## After the first deploy

Visit `https://jarvis-agent-api.fly.dev/` for the dashboard. Click "Run
good morning" — same flow as local, just on a public, always-reachable URL.

## What "every commit deploys" means in practice

Every push to `master` redeploys *both* services, even if only one
changed — simplest correct behavior for a two-service personal project.
If this gets noisy later, the workflow can add `paths:` filters per job so
e.g. a dashboard-only change skips redeploying `mcp-server`.

## Rotating `JARVIS_MCP_TOKEN`

`dev-token` (used for local dev) must not be used in production — set a
real random value in step 4/5 above. If you ever rotate it, update the
secret on *both* Fly apps in the same breath, or agent-api's calls to
mcp-server will start failing with 401s until both match again.
