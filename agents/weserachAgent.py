from strands import Agent, tool
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
import os
from ddgs import DDGS

# from strands_tools import calculator, current_time
load_dotenv()
print("hello world")

gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-1.5-flash",
    params={"temperature": 0.7},
)


@tool
def search(query: str, max_results=1) -> str:
    try:
        results = DDGS().text(query, max_results)
        return results if results else "No results found."
    except Exception as e:
        return f"An error occurred while searching: {str(e)}"


agent = Agent(
    model=gemini_model,
    tools=[search],
    system_prompt="Use the search tool to find information on the web. Always use the search tool when you need to find information that is not in your training data. Be concise and provide only the most relevant information from the search results.",
)
while True:
    query = input("Enter your query: ")
    if query.lower() == "exit":
        break
    response = agent(query)
    print("Agent response:", response)
