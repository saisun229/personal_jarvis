import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8001")
JARVIS_MCP_TOKEN = os.environ.get("JARVIS_MCP_TOKEN", "dev-token")

AGENT_DB_PATH = os.environ.get("AGENT_DB_PATH", "agent_api.db")
