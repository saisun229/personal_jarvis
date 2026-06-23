import json

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.prompts.daily_brief import SYSTEM_PROMPT, build_user_prompt

_client = OpenAI(api_key=OPENAI_API_KEY)


def generate_daily_brief(context: dict) -> dict:
    response = _client.chat.completions.create(
        model=OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(context)},
        ],
    )
    return json.loads(response.choices[0].message.content)
