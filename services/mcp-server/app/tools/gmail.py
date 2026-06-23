import httpx

from app.google_oauth import get_valid_access_token
from app.registry import RISK_READ_ONLY, tool

BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

# Heuristic for "looks automated, probably doesn't need a human reply",
# layered on top of Gmail's own category filtering below. A real follow-up
# detector (Phase 2 of final_goal.md's roadmap) replaces both; for the MVP
# this is enough to filter out obvious bulk/notification mail.
AUTOMATED_SENDER_MARKERS = ["noreply", "no-reply", "notifications@", "notification@", "donotreply", "mailer@"]


def _headers_to_dict(headers: list[dict]) -> dict:
    return {h["name"]: h["value"] for h in headers}


def _fetch_unread(max_results: int, query: str = "is:unread in:inbox") -> list[dict]:
    token = get_valid_access_token()
    auth = {"Authorization": f"Bearer {token}"}

    list_response = httpx.get(BASE_URL, headers=auth, params={"q": query, "maxResults": max_results}, timeout=30)
    list_response.raise_for_status()
    message_ids = [m["id"] for m in list_response.json().get("messages", [])]

    emails = []
    for message_id in message_ids:
        detail = httpx.get(
            f"{BASE_URL}/{message_id}",
            headers=auth,
            params={"format": "metadata", "metadataHeaders": ["Subject", "From", "Date"]},
            timeout=30,
        )
        detail.raise_for_status()
        data = detail.json()
        header_map = _headers_to_dict(data.get("payload", {}).get("headers", []))
        emails.append(
            {
                "thread_id": data.get("threadId"),
                "subject": header_map.get("Subject", "(no subject)"),
                "from": header_map.get("From", "unknown"),
                "date": header_map.get("Date"),
                "snippet": data.get("snippet", ""),
            }
        )
    return emails


@tool("gmail.search_recent_unread", risk_level=RISK_READ_ONLY)
def search_recent_unread(params: dict) -> dict:
    return {"emails": _fetch_unread(max_results=params.get("max_results", 8))}


@tool("gmail.search_needing_reply", risk_level=RISK_READ_ONLY)
def search_needing_reply(params: dict) -> dict:
    # Gmail's own category labels filter out most bulk/promo/social mail
    # before our sender-keyword heuristic even runs.
    query = "is:unread in:inbox -category:promotions -category:social -category:updates -category:forums"
    unread = _fetch_unread(max_results=params.get("max_results", 8), query=query)
    needing_reply = [e for e in unread if not any(marker in e["from"].lower() for marker in AUTOMATED_SENDER_MARKERS)]
    return {"emails": needing_reply}
