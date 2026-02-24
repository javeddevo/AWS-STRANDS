from strands import Agent,tool
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
from strands_tools import calculator, current_time
import os


@tool
def uppercase(text: str):
    return text.upper()

load_dotenv()
#Google Gemini
gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)

agent = Agent(model=gemini_model, tools=[calculator, current_time, uppercase])
result=agent("""I have a therre task for you:
     Task1:what is squareroot of 16",
     Task2:what is the current time,
     Task3:make this senetence uppercase: "hello world" """)
#print(result.metrics.get_summary())
print(f"Total tokens: {result.metrics.accumulated_usage['totalTokens']}")
print(f"Execution time: {sum(result.metrics.cycle_durations):.2f} seconds")
print(f"Tools used: {list(result.metrics.tool_metrics.keys())}")
