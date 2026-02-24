import os
import json
from strands import Agent, tool
from strands.multiagent import Swarm
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
import os
import logging

# Suppress OpenTelemetry context errors from multi-agent swarm
logging.getLogger("opentelemetry").setLevel(logging.CRITICAL)

load_dotenv()

gemini = GeminiModel(
    client_args={"api_key": os.getenv("GEMINI_API_KEY")},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)

# This is a Python function the Lead Agent can CALL as a tool.
# In real world → this could be a DB call, HR system API, etc.
@tool
def get_team_members():
    """
    Returns the list of team members available for task assignment.
    Lead agent calls this tool to know who is on the team.
    """
    team = ["Alice", "Bob", "Charlie", "Diana"]
    return json.dumps(team)


# ──────────────────────────────────────────────────────────────────────────────
# AGENT 1: RESEARCHER  ← Entry Point
# Validates requirement, researches it, hands off to BA
# ──────────────────────────────────────────────────────────────────────────────
researcher = Agent(
    name="researcher",
    system_prompt="""
You are a Technical Researcher who works ONLY on technical software projects or a research-related task.

STEP 1 — VALIDATE the user requirement first:
- Ask yourself: Is this a technical software/engineering project?
- Valid examples: build an API, create an AI agent, develop a web app, set up cloud infrastructure, etc.
- Invalid examples: write a poem, plan a holiday, cook a recipe, give life advice, etc.

If NOT a technical software requirement, respond with:
    INVALID REQUIREMENT
    Sorry, I only work on technical software projects.
    Please provide a requirement related to software development, cloud, AI, APIs, or engineering.
    Example: "Build a REST API", "Create an AWS Lambda function", "Develop a chatbot using Strands SDK"

Then STOP. Do not hand off to ba_agent.

---

If it is valid, research the topic:
1. Research concepts, tools, dependencies, patterns.
2. Output research summary in this format:

    === RESEARCH SUMMARY ===
    TOPIC: <topic>
    KEY CONCEPTS: <points>
    HOW IT WORKS: <brief>
    DEPENDENCIES: <packages/services>
    NOTES: <important info>

3. Hand off to ba_agent.
""",
    model=gemini,
)

ba_agent = Agent(
    name="ba_agent",
    system_prompt="""
You are a Business Analyst (BA).

You will receive a research summary from the researcher.

Your ONLY job:
1. Read the research summary carefully.
2. Break the work into clear, numbered subtasks.
3. Output the task plan in EXACTLY this format (lead agent depends on it):

    === TASK PLAN ===
    PROJECT: <one-line title>

    TASK 1: <clear task description>
    TASK 2: <clear task description>
    TASK 3: <clear task description>
    TASK 4: <clear task description>
    ... (as many as needed)

    NOTES:
    - <any important considerations>

4. Hand off to lead_agent with the full task plan.

Do NOT write code or architecture. Just the task plan.
""",
    model=gemini,
)



lead_agent = Agent(
    name="lead_agent",
    system_prompt="""
    You are a Technical Lead / Project Manager.

    You will receive a task plan from the BA agent.

    Your job:
    1. Call the tool `get_team_members` to get the list of team members.
    2. Read all tasks from the BA plan (TASK 1, TASK 2, TASK 3...).
    3. Distribute tasks EQUALLY across all members (round-robin, by count only).
    - If tasks > members → assign multiple tasks to members evenly.
    - If tasks < members → remaining members get: "Collaborate and support the team."
    - If tasks == members → one task per member.

    Output in this format:

        === TASK ASSIGNMENT ===
        PROJECT: <project name>

        Alice
        → TASK 1: <task>
        → TASK 5: <task>

        Bob
        → TASK 2: <task>

         Charlie
        → TASK 3: <task>

        Diana
        → Collaborate and support the team.

        TOTAL TASKS: <n>
        TOTAL MEMBERS: <n>
    """,
    tools=[get_team_members],  
    model=gemini,
)

swarm = Swarm(
    [researcher, ba_agent, lead_agent],  # 3 agents
    entry_point=researcher,              # thsi is entry point we need to define
    max_handoffs=4,                      # researcher to ba to lead = 2 handoffs
    max_iterations=8,
    execution_timeout=300.0,             
    node_timeout=120.0,     #each agent             
)

user_req = input("Enter your project requirement: ")
result = swarm(user_req)
print("\n" + "─" * 50)
#print(result.output)
print("\n" + "─" * 50)
print(f"Status : {result.status}")
print(f"Agent order: {[n.node_id for n in result.node_history]}")
# Expected: ['researcher', 'ba_agent', 'lead_agent']
