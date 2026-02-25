from strands import Agent, tool
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
from strands_tools import calculator, current_time
import os

load_dotenv()


@tool
def word_count(sent: str):
    return len(sent.split())


gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
)

agent = Agent(model=gemini_model, tools=[word_count, current_time, calculator])
agent(
    "i have four request for you \
      1.how many words are in this current sentence. \
      2.calculate teh square root of 9. \
      3.get the current date. \
      4.If a person is born in 2000, whats his age now"
)
