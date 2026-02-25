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

# Create MCP client with stdio transport
mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",  # for thsi you need tio install uvx in you system and set
        args=["awslabs.aws-documentation-mcp-server@latest"] # aws
    )
))

agent = Agent(tools=[mcp_client])
agent("What is AWS strands")
