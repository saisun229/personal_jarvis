from datetime import datetime, time, timedelta, timezone

import httpx

from app.google_oauth import get_valid_access_token
from app.registry import RISK_READ_ONLY, tool

EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

# Free-block search assumes a 09:00-18:00 UTC working day. Real per-user
# timezone handling is a future improvement, not needed for the MVP.
WORKDAY_START_HOUR = 9
WORKDAY_END_HOUR = 18


def _list_events(time_min: datetime, time_max: datetime) -> list[dict]:
    token = get_valid_access_token()
    response = httpx.get(
        EVENTS_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "timeMin": time_min.isoformat(),
            "timeMax": time_max.isoformat(),
            "singleEvents": "true",
            "orderBy": "startTime",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("items", [])


def _normalize(item: dict) -> dict:
    return {
        "title": item.get("summary", "(no title)"),
        "start": item.get("start", {}).get("dateTime", item.get("start", {}).get("date")),
        "end": item.get("end", {}).get("dateTime", item.get("end", {}).get("date")),
        "attendees": [a.get("email") for a in item.get("attendees", [])],
        "location": item.get("location"),
    }


@tool("calendar.list_today", risk_level=RISK_READ_ONLY)
def list_today(params: dict) -> dict:
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return {"events": [_normalize(item) for item in _list_events(start, end)]}


@tool("calendar.list_next_7_days", risk_level=RISK_READ_ONLY)
def list_next_7_days(params: dict) -> dict:
    now = datetime.now(timezone.utc)
    return {"events": [_normalize(item) for item in _list_events(now, now + timedelta(days=7))]}


@tool("calendar.find_free_blocks", risk_level=RISK_READ_ONLY)
def find_free_blocks(params: dict) -> dict:
    now = datetime.now(timezone.utc)
    day_start = datetime.combine(now.date(), time(WORKDAY_START_HOUR), tzinfo=timezone.utc)
    day_end = datetime.combine(now.date(), time(WORKDAY_END_HOUR), tzinfo=timezone.utc)

    busy = []
    for item in _list_events(day_start, day_end):
        start_raw = item.get("start", {}).get("dateTime")
        end_raw = item.get("end", {}).get("dateTime")
        if not start_raw or not end_raw:
            continue  # all-day events don't block working hours
        busy.append((datetime.fromisoformat(start_raw), datetime.fromisoformat(end_raw)))
    busy.sort()

    free_blocks = []
    cursor = day_start
    for busy_start, busy_end in busy:
        if busy_start > cursor:
            free_blocks.append({"start": cursor.isoformat(), "end": busy_start.isoformat()})
        cursor = max(cursor, busy_end)
    if cursor < day_end:
        free_blocks.append({"start": cursor.isoformat(), "end": day_end.isoformat()})

    return {"free_blocks": free_blocks}
