from strands import Agent
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv 
import os

# from strands_tools import calculator, current_time
load_dotenv()
print("hello world")
print("API KEY:", os.getenv("GEMINI_API_KEY"))
# # Google Gemini
gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)
print("gemini model loaded")
agent = Agent(model=gemini_model)
agent("what is 2+2")
