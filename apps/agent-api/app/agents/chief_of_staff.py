from datetime import datetime, timezone

from app.agents import calendar_agent, gmail_agent, task_agent
from app.db import complete_run, create_run, save_daily_brief
from app.mcp_client import call_tool
from app.openai_client import generate_daily_brief


def run_good_morning() -> dict:
    run_id = create_run("good_morning", input_data={})
    try:
        context = {
            "calendar": calendar_agent.gather(),
            "email": gmail_agent.gather(),
            "tasks": task_agent.gather(),
            "recent_memories": call_tool("memory.search_recent", {"limit": 5}).get("memories", []),
        }

        brief = generate_daily_brief(context)

        brief_date = datetime.now(timezone.utc).date().isoformat()
        save_daily_brief(brief_date, brief.get("summary", ""), brief)

        call_tool(
            "memory.write",
            {"type": "episode", "content": f"Daily brief generated for {brief_date}", "metadata": {}},
        )

        telegram_text = brief.get("summary", "")
        call_tool("telegram.send_message", {"text": telegram_text})

        complete_run(run_id, output_data=brief)
        return {"run_id": run_id, "brief": brief}
    except Exception as exc:
        complete_run(run_id, error=str(exc))
        raise
