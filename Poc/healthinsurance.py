from strands import Agent
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient
import os

load_dotenv()
# # Google Gemini
gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)