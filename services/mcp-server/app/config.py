import os

from dotenv import load_dotenv

load_dotenv()

JARVIS_MCP_TOKEN = os.environ.get("JARVIS_MCP_TOKEN", "dev-token")
MCP_DB_PATH = os.environ.get("MCP_DB_PATH", "mcp_server.db")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
