from app.registry import RISK_READ_ONLY, tool

# Real implementation swaps in here once GOOGLE_CLIENT_ID/SECRET + stored
# OAuth tokens exist (Phase 5). Signature and return shape stay the same.


@tool("calendar.list_today", risk_level=RISK_READ_ONLY)
def list_today(params: dict) -> dict:
    return {
        "events": [
            {
                "title": "1:1 with manager",
                "start": "2026-06-23T13:00:00Z",
                "end": "2026-06-23T13:30:00Z",
                "attendees": ["manager@example.com"],
                "location": "Zoom",
            },
            {
                "title": "Sprint planning",
                "start": "2026-06-23T17:00:00Z",
                "end": "2026-06-23T18:00:00Z",
                "attendees": ["team@example.com"],
                "location": "Conference Room B",
            },
        ]
    }


@tool("calendar.list_next_7_days", risk_level=RISK_READ_ONLY)
def list_next_7_days(params: dict) -> dict:
    return {
        "events": [
            {
                "title": "Dentist appointment",
                "start": "2026-06-25T15:00:00Z",
                "end": "2026-06-25T15:45:00Z",
            },
            {
                "title": "Quarterly review",
                "start": "2026-06-27T16:00:00Z",
                "end": "2026-06-27T17:00:00Z",
            },
        ]
    }


@tool("calendar.find_free_blocks", risk_level=RISK_READ_ONLY)
def find_free_blocks(params: dict) -> dict:
    return {
        "free_blocks": [
            {"start": "2026-06-23T09:30:00Z", "end": "2026-06-23T11:00:00Z"},
            {"start": "2026-06-23T14:00:00Z", "end": "2026-06-23T16:30:00Z"},
        ]
    }
