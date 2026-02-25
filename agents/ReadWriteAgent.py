from strands import Agent
from strands_tools import http_request, file_read, file_write
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
import os

load_dotenv()

gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
)

YSTEM_PROMPT = """
You are a responsible AI assistant.

Your primary task is to:
1. Read the file from the provided file path using the available tools.
2. Summarize the content in exactly three concise lines.
3. Write the summary into a new file in the same directory.

Rules:
- Always use the provided tools to read and write files.
- Do not guess file contents.
- Keep the summary clear and meaningful.
- Name the new file as: summary_<original_filename>.txt
- Do not explain your reasoning.
- Confirm once the file is successfully written.
"""
agent = Agent(model=gemini_model, tools=[file_read, file_write])

agent(
    "Get to the folder docs read the awsstrandblog file and get the summary and dump in new file"
)
