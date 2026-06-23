from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from app.registry import RISK_EXTERNAL_WRITE, tool

# Policy exception: EXTERNAL_WRITE is normally approval-gated, but sending to
# our own configured owner chat is pre-approved (see final_goal.md).
# Real send swaps in here once TELEGRAM_BOT_TOKEN/CHAT_ID are set (Phase 6).


@tool("telegram.send_message", risk_level=RISK_EXTERNAL_WRITE)
def send_message(params: dict) -> dict:
    text = params.get("text", "")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {"status": "mocked", "would_send_to": "owner_chat", "text": text}
    raise NotImplementedError("real Telegram send not wired up yet")
