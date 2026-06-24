import base64
import secrets

from starlette.requests import Request
from starlette.responses import Response

from app.config import DASHBOARD_PASSWORD, DASHBOARD_USERNAME


async def basic_auth_middleware(request: Request, call_next):
    if not DASHBOARD_USERNAME or not DASHBOARD_PASSWORD:
        # Local dev: no credentials configured, auth is a no-op.
        return await call_next(request)

    if request.url.path == "/api/health":
        return await call_next(request)

    header = request.headers.get("authorization", "")
    if header.startswith("Basic "):
        try:
            decoded = base64.b64decode(header.removeprefix("Basic ")).decode()
            username, _, password = decoded.partition(":")
        except Exception:
            username, password = "", ""

        if secrets.compare_digest(username, DASHBOARD_USERNAME) and secrets.compare_digest(password, DASHBOARD_PASSWORD):
            return await call_next(request)

    return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="Jarvis"'})
