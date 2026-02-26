from strands import Agent
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient
from pathlib import Path
import os

load_dotenv()

# Google Gemini Model
gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)

# Get the absolute path to the MCP server script
mcp_server_path = Path(__file__).parent / "order_mcp_server.py"

# Create MCP client with stdio transport
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

        # Create Agent with MCP tools
        agent = Agent(
            model=gemini_model,
            tools=tools,
            instructions="""You are a helpful customer service agent specializing in order support.
            You have access to order lookup tools via MCP that fetch data based on order_id or email.
            When customers ask about their orders, use the appropriate tools to retrieve information.
            Always provide clear, friendly, and helpful responses."""
        )

        # Example customer queries
        queries = [
            "What is the status of order 1001?",
            "Can you give me the tracking information for order 1002?",
            "What items are in order 1003?",
            "Can I return order 1005?",
            "Show me all details for order 1008",
            "What orders does alice.smith@email.com have?",
        ]
        
        print("\n" + "="*70)
        print("CUSTOMER ORDER SERVICE - AWS STRANDS + MCP + PANDAS POC")
        print("="*70)
        
        for query in queries:
            print(f"\n{'='*70}")
            print(f"Customer Query: {query}")
            print(f"{'='*70}")
            response = agent(query)
            print(f"Agent Response:\n{response}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
