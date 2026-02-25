"""
FILE 1: AGENT-TO-AGENT COMMUNICATION (A2A)
===========================================

In this pattern:
- Agent 1 (Coordinator) receives a user request
- Coordinator decides to delegate to specialized agents
- Coordinator uses other agents as "tools" via handoffs
- Each specialized agent (Research, Analysis) completes their task
- Results flow back to coordinator which synthesizes final response

Use case: Complex tasks that need different expertise
Example: A request that needs both web research AND code analysis
"""

from strands import Agent, tool
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
import os
import json

load_dotenv()

# ============================================================================
# STEP 1: Initialize the Gemini Model
# This is the brain that powers all agents - same model for simplicity
# ============================================================================
gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)

# ============================================================================
# STEP 2: Define Specialist Agent #1 - RESEARCHER
# This agent focuses on gathering information
# ============================================================================
researcher_agent = Agent(
    name="researcher",
    system_prompt="""
You are a Research Specialist. Your job is to:
1. Take a topic from the coordinator
2. Research and gather information about it
3. Return a concise summary with KEY FACTS

Output format:
RESEARCH RESULTS:
- Fact 1: ...
- Fact 2: ...
- Fact 3: ...
""",
    model=gemini_model,
)

# ============================================================================
# STEP 3: Define Specialist Agent #2 - ANALYST
# This agent focuses on analyzing and providing insights
# ============================================================================
analyst_agent = Agent(
    name="analyst",
    system_prompt="""
You are a Business Analyst. Your job is to:
1. Take research data from the coordinator
2. Analyze it and provide insights
3. Give 3-5 actionable recommendations

Output format:
ANALYSIS & RECOMMENDATIONS:
- Insight 1: ...
- Recommendation 1: ...
- Recommendation 2: ...
""",
    model=gemini_model,
)

# ============================================================================
# STEP 4: Define Coordinator Agent
# This is the main agent that orchestrates the other agents
# It decides when to call which specialist agent
# ============================================================================
coordinator_agent = Agent(
    name="coordinator",
    system_prompt="""
You are a Project Coordinator. You receive user requests and break them down:

WORKFLOW:
1. For requests needing RESEARCH → send to researcher_agent
2. For requests needing ANALYSIS → send to analyst_agent
3. For requests needing BOTH → send to researcher_agent first, then analyst_agent

When you send to another agent, clearly state:
"[HANDOFF TO: agent_name]
Task: [exact task description]"

After getting responses from agents, synthesize them into a final answer.
""",
    model=gemini_model,
    # Note: A2A protocol support is coming to Strands (as per AWS blog)
    # For now, we use manual handoff by instructing the agent
)

# ============================================================================
# STEP 5: Simple Manual Orchestration (until A2A protocol is available)
# In production, Strands A2A protocol will automate this
# ============================================================================

def orchestrate_agent_to_agent(user_request: str) -> str:
    """
    Orchestrate multiple agents for a complex task
    
    Flow:
    1. Coordinator receives request
    2. Coordinator delegates to researcher
    3. Coordinator delegates to analyst  
    4. Coordinator synthesizes results
    """
    
    print("\n" + "="*60)
    print("AGENT-TO-AGENT ORCHESTRATION")
    print("="*60)
    
    # Step 1: Coordinator analyzes request
    print("\n[COORDINATOR] Analyzing user request...")
    coordinator_response = coordinator_agent(user_request)
    print(f"Coordinator Decision: {coordinator_response}\n")
    
    # Step 2: Delegate to Researcher
    print("[COORDINATOR] Delegating to RESEARCHER...")
    research_task = f"Research this topic and provide key facts: {user_request}"
    researcher_response = researcher_agent(research_task)
    print(f"Researcher Response:\n{researcher_response}\n")
    
    # Step 3: Delegate to Analyst with research data
    print("[COORDINATOR] Delegating to ANALYST...")
    analysis_task = f"Based on this research: {researcher_response}\n\nProvide analysis and recommendations."
    analyst_response = analyst_agent(analysis_task)
    print(f"Analyst Response:\n{analyst_response}\n")
    
    # Step 4: Coordinator synthesizes final response
    print("[COORDINATOR] Synthesizing final response...")
    synthesis_prompt = f"""
You are the coordinator. Combine these responses into one clear final answer:

RESEARCH: {researcher_response}

ANALYSIS: {analyst_response}

Final Answer (synthesized):
"""
    final_response = coordinator_agent(synthesis_prompt)
    
    return final_response

# ============================================================================
# STEP 6: Run the Example
# ============================================================================
if __name__ == "__main__":
    # Example user request that requires both research and analysis
    user_input = "What is AWS Strands and why should companies use it?"
    
    result = orchestrate_agent_to_agent(user_input)
    
    print("\n" + "="*60)
    print("FINAL SYNTHESIZED RESPONSE:")
    print("="*60)
    print(result)
