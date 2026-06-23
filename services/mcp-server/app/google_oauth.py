from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx

from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
from app.db import client

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def build_auth_url() -> str:
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def _store_tokens(token_response: dict, account_email: str):
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=token_response.get("expires_in", 3600))).isoformat()
    row = {
        "provider": "google",
        "account_email": account_email,
        # NOTE: stored as plaintext for the MVP. Token encryption is an
        # explicitly deferred hardening step (see task.md).
        "access_token_encrypted": token_response["access_token"],
        "scopes": SCOPES,
        "metadata": {"expires_at": expires_at, "token_type": token_response.get("token_type", "Bearer")},
    }
    if "refresh_token" in token_response:
        row["refresh_token_encrypted"] = token_response["refresh_token"]

    existing = client.table("integrations").select("id").eq("provider", "google").execute()
    if existing.data:
        client.table("integrations").update(row).eq("id", existing.data[0]["id"]).execute()
    else:
        client.table("integrations").insert(row).execute()


def exchange_code_for_tokens(code: str) -> str:
    response = httpx.post(
        TOKEN_URL,
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI,
        },
        timeout=30,
    )
    response.raise_for_status()
    token_response = response.json()

    userinfo = httpx.get(USERINFO_URL, headers={"Authorization": f"Bearer {token_response['access_token']}"}, timeout=30)
    userinfo.raise_for_status()
    account_email = userinfo.json().get("email", "unknown")

    _store_tokens(token_response, account_email)
    return account_email


def _refresh_access_token(integration: dict) -> str:
    response = httpx.post(
        TOKEN_URL,
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": integration["refresh_token_encrypted"],
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    response.raise_for_status()
    token_response = response.json()

    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=token_response.get("expires_in", 3600))).isoformat()
    client.table("integrations").update(
        {
            "access_token_encrypted": token_response["access_token"],
            "metadata": {**integration.get("metadata", {}), "expires_at": expires_at},
        }
    ).eq("id", integration["id"]).execute()

    return token_response["access_token"]


def get_valid_access_token() -> str:
    rows = client.table("integrations").select("*").eq("provider", "google").execute()
    if not rows.data:
        raise RuntimeError("Google account not connected yet — visit /auth/google/start in a browser first")

    integration = rows.data[0]
    expires_at = integration.get("metadata", {}).get("expires_at")
    if expires_at and datetime.fromisoformat(expires_at) > datetime.now(timezone.utc) + timedelta(minutes=2):
        return integration["access_token_encrypted"]

    return _refresh_access_token(integration)
