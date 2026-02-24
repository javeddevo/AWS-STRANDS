from strands import Agent
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
import os
from pathlib import Path
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client

load_dotenv()

# Google Gemini
gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)

# Get the absolute path to the MCP server script
mcp_server_path = Path(__file__).parent / "calculatormcp.py"

stdio_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="python", 
            args=[str(mcp_server_path)]
        )
    )
)

try:
    with stdio_mcp_client:
        # Get the tools from the MCP server
        tools = stdio_mcp_client.list_tools_sync()

        agent = Agent(
            model=gemini_model,
            tools=tools)

        response = agent("what is 2/2")
        print(response)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()