from app.registry import RISK_READ_ONLY, tool

# Real implementation swaps in here once GOOGLE_CLIENT_ID/SECRET + stored
# OAuth tokens exist (Phase 5). Signature and return shape stay the same.


@tool("gmail.search_recent_unread", risk_level=RISK_READ_ONLY)
def search_recent_unread(params: dict) -> dict:
    return {
        "emails": [
            {
                "thread_id": "t-101",
                "subject": "Availability for a quick call this week?",
                "from": "recruiter@example-staffing.com",
                "date": "2026-06-23T08:12:00Z",
                "snippet": "Hi Sai, we'd love to find 20 minutes this week to discuss...",
            },
            {
                "thread_id": "t-102",
                "subject": "[GitHub] Build failed on personal_jarvis#42",
                "from": "notifications@github.com",
                "date": "2026-06-23T07:50:00Z",
                "snippet": "The build for commit 7b1fe5d failed: 1 test failure in...",
            },
            {
                "thread_id": "t-103",
                "subject": "Your payment is due soon",
                "from": "billing@examplebank.com",
                "date": "2026-06-23T06:30:00Z",
                "snippet": "Your statement balance of $0.00 is due on 2026-06-28...",
            },
        ]
    }


@tool("gmail.search_needing_reply", risk_level=RISK_READ_ONLY)
def search_needing_reply(params: dict) -> dict:
    return {
        "emails": [
            {
                "thread_id": "t-101",
                "subject": "Availability for a quick call this week?",
                "from": "recruiter@example-staffing.com",
                "snippet": "Hi Sai, we'd love to find 20 minutes this week to discuss...",
                "days_waiting": 1,
            }
        ]
    }
