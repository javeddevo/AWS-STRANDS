from strands import Agent
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
import os
from strands.session.file_session_manager import FileSessionManager

load_dotenv()

gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
)


session_manager = FileSessionManager(
    session_id="Test1", storage_dir="./sessions/Test1.json"
)
agent = Agent(model=gemini_model, session_manager=session_manager)
# agent("Hey my name is Javeed")
agent("Hey do you remeber my name?")
