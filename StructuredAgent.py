from strands import Agent
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()


class Info(BaseModel):
    name: str
    company: str
    department: None | str
    salary: float


gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
)

details = """John works at cognizant in the Platform department as a Python developer. 
   He earns a salary of ₹12 LPA, where he mainly works with agnets creation"""

agent = Agent(model=gemini_model, structured_output_model=Info)
result = agent(details)
response: Info = result.structured_output
print(response)
print("name:", response.name)
print("company:", response.company)
print("department:", response.department)
print("salary:", response.salary)
