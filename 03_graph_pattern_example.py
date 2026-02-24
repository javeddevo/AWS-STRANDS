"""
FILE 3: GRAPH PATTERN
=====================

In this pattern:
- Multiple agents are organized as NODES in a directed graph
- Edges define the flow between agents (who talks to whom)
- An agent processes a task and decides which agent(s) to call next
- Perfect for workflows with multiple possible paths

Use case: Decision trees, workflows with branching logic
Examples:
  - Customer support: Route to sales_agent OR support_agent OR escalation_agent
  - Content creation: research → outline → draft → review → publish
  - Problem solving: diagnose → research → implement → test → deploy

DIFFERENCE FROM SWARM:
- Graph: Sequential/branching paths (step 1 → step 2 → step 3)
- Swarm: Parallel agents (all agents work together on same task)

Graph is like an assembly line, Swarm is like a team brainstorm.
"""

from strands import Agent, tool
from strands.models.gemini import GeminiModel
from strands.multiagent import Graph
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================================================
# STEP 1: Initialize the Gemini Model
# ============================================================================
gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)

# ============================================================================
# STEP 2: Define GRAPH NODES (Agents)
# Each agent represents a step in the workflow
# ============================================================================

# NODE 1: INTAKE AGENT
# First node - receives user request and categorizes it
intake_agent = Agent(
    name="intake",
    system_prompt="""
You are an Intake Specialist. Your job:
1. Receive a customer request
2. Categorize it as: BUG_REPORT, FEATURE_REQUEST, or QUESTION
3. Extract key information
4. Recommend next step

Output format:
CATEGORY: [BUG_REPORT | FEATURE_REQUEST | QUESTION]
PRIORITY: [HIGH | MEDIUM | LOW]
KEY_INFO: [extracted details]
NEXT_STEP: [name of next agent to handle this]
""",
    model=gemini_model,
)

# NODE 2: BUG HANDLER AGENT
# Handles bug reports
bug_handler_agent = Agent(
    name="bug_handler",
    system_prompt="""
You are a Bug Handler. Your job:
1. Receive bug details from intake agent
2. Ask clarifying questions if needed
3. Suggest troubleshooting steps
4. Recommend if escalation needed

Output format:
BUG_SEVERITY: [CRITICAL | HIGH | MEDIUM | LOW]
TROUBLESHOOTING: [steps to try]
ESCALATE: [YES | NO]
NOTES: [for engineering team if escalated]
""",
    model=gemini_model,
)

# NODE 3: FEATURE REQUEST AGENT
# Handles feature requests
feature_agent = Agent(
    name="feature_handler",
    system_prompt="""
You are a Feature Request Handler. Your job:
1. Receive feature request from intake agent
2. Evaluate feasibility and impact
3. Suggest timeline and dependencies
4. Recommend priority level

Output format:
FEASIBILITY: [HIGH | MEDIUM | LOW]
EFFORT_ESTIMATE: [days/weeks]
IMPACT: [HIGH | MEDIUM | LOW]
PRIORITY: [P0 | P1 | P2 | P3]
NEXT_STEP: [Add to backlog | Escalate | Archive]
""",
    model=gemini_model,
)

# NODE 4: GENERAL QUESTION AGENT
# Handles general questions
question_agent = Agent(
    name="question_handler",
    system_prompt="""
You are a Question Handler. Your job:
1. Receive general question from intake agent
2. Provide clear, concise answer
3. Offer related resources or next steps
4. Determine if escalation needed

Output format:
ANSWER: [direct answer to question]
RELATED_TOPICS: [suggestions]
ESCALATE: [YES | NO]
FOLLOW_UP: [suggested next action]
""",
    model=gemini_model,
)

# NODE 5: ESCALATION AGENT
# Handles complex cases that need escalation
escalation_agent = Agent(
    name="escalation_handler",
    system_prompt="""
You are an Escalation Handler. Your job:
1. Receive complex cases from other agents
2. Create escalation ticket with all details
3. Assign to appropriate team
4. Set expected resolution time

Output format:
TICKET_ID: [generated ID]
ASSIGNED_TO: [team/person]
PRIORITY: [CRITICAL | HIGH | MEDIUM]
ETA: [estimated resolution time]
SUMMARY: [executive summary]
""",
    model=gemini_model,
)

# ============================================================================
# STEP 3: Define GRAPH FLOW - How agents connect
# This defines the routing logic between agents
# ============================================================================

def route_from_intake(response: str) -> str:
    """
    Route from intake agent to appropriate handler based on category
    """
    # In real implementation, parse response to determine category
    if "BUG_REPORT" in response:
        return "bug_handler"
    elif "FEATURE_REQUEST" in response:
        return "feature_handler"
    elif "QUESTION" in response:
        return "question_handler"
    else:
        return "question_handler"  # default


def route_from_handler(response: str) -> str:
    """
    Route from any handler to escalation if needed
    """
    if "ESCALATE: YES" in response or "Escalate" in response:
        return "escalation_handler"
    else:
        return "END"  # Complete the workflow


# ============================================================================
# STEP 4: Create the GRAPH
# Define nodes and edges of the graph
# ============================================================================

def create_customer_support_graph():
    """
    Create a graph for customer support workflow
    
    Flow:
    1. Intake → Categorize request
    2. Route to: bug_handler OR feature_agent OR question_agent
    3. If escalate needed → escalation_handler
    4. Otherwise → End
    """
    
    # Create graph nodes (agents)
    graph = Graph(
        nodes=[intake_agent, bug_handler_agent, feature_agent, 
               question_agent, escalation_agent],
        entry_point=intake_agent,  # Start here
        max_iterations=5,  # Prevent infinite loops
    )
    
    return graph


# ============================================================================
# STEP 5: MANUAL GRAPH ORCHESTRATION
# (Graph auto-routing coming in future Strands versions)
# For now, we manually manage the flow
# ============================================================================

def process_customer_request_graph(customer_request: str) -> str:
    """
    Process customer request through the graph workflow
    """
    
    print("\n" + "="*70)
    print("GRAPH PATTERN - CUSTOMER SUPPORT WORKFLOW")
    print("="*70)
    
    # STEP 1: Intake node - categorize and route
    print("\n[STEP 1] INTAKE AGENT - Categorizing request...")
    intake_response = intake_agent(customer_request)
    print(f"Intake Response:\n{intake_response}\n")
    
    # STEP 2: Route based on category (simulated routing logic)
    route = route_from_intake(intake_response)
    print(f"[ROUTING] Directed to: {route}")
    
    handler_response = ""
    
    # STEP 3: Process through appropriate handler
    if route == "bug_handler":
        print("\n[STEP 2] BUG HANDLER - Analyzing bug report...")
        handler_response = bug_handler_agent(
            f"Customer request: {customer_request}\n\nIntake assessment: {intake_response}"
        )
        print(f"Bug Handler Response:\n{handler_response}\n")
        
    elif route == "feature_handler":
        print("\n[STEP 2] FEATURE HANDLER - Evaluating feature request...")
        handler_response = feature_agent(
            f"Customer request: {customer_request}\n\nIntake assessment: {intake_response}"
        )
        print(f"Feature Handler Response:\n{handler_response}\n")
        
    elif route == "question_handler":
        print("\n[STEP 2] QUESTION HANDLER - Answering question...")
        handler_response = question_agent(
            f"Customer request: {customer_request}\n\nIntake assessment: {intake_response}"
        )
        print(f"Question Handler Response:\n{handler_response}\n")
    
    # STEP 4: Check if escalation needed
    escalation_route = route_from_handler(handler_response)
    
    if escalation_route == "escalation_handler":
        print("\n[STEP 3] ESCALATION HANDLER - Creating escalation ticket...")
        final_response = escalation_agent(
            f"Original request: {customer_request}\n\n" +
            f"Intake assessment: {intake_response}\n\n" +
            f"Handler assessment: {handler_response}"
        )
        print(f"Escalation Response:\n{final_response}\n")
    else:
        final_response = handler_response
    
    return final_response


# ============================================================================
# STEP 6: Run Graph Examples
# ============================================================================

def example_bug_report():
    """Example: Customer reports a bug"""
    print("\n" + "█"*70)
    print("EXAMPLE 1: BUG REPORT")
    print("█"*70)
    
    request = """
    The application crashes when I try to upload files larger than 10MB.
    I'm using the web version on Chrome. Error message: 'Maximum file size exceeded'
    """
    
    result = process_customer_request_graph(request)
    return result


def example_feature_request():
    """Example: Customer requests a feature"""
    print("\n" + "█"*70)
    print("EXAMPLE 2: FEATURE REQUEST")
    print("█"*70)
    
    request = """
    I'd like the ability to export reports in PDF format with custom headers
    and footers. Currently only CSV is available.
    """
    
    result = process_customer_request_graph(request)
    return result


def example_general_question():
    """Example: Customer asks a question"""
    print("\n" + "█"*70)
    print("EXAMPLE 3: GENERAL QUESTION")
    print("█"*70)
    
    request = """
    How do I reset my password if I don't have access to my email?
    """
    
    result = process_customer_request_graph(request)
    return result


# ============================================================================
# STEP 7: Run All Examples
# ============================================================================

if __name__ == "__main__":
    # Run examples
    example_bug_report()
    example_feature_request()
    example_general_question()
    
    print("\n" + "="*70)
    print("GRAPH PATTERN KEY CONCEPTS")
    print("="*70)
    print("""
NODES: Individual agents that process tasks
- intake_agent: Entry point
- bug_handler, feature_agent, question_agent: Specialized processors
- escalation_agent: Handles complex cases

EDGES: Connections between agents
- Determined by routing logic
- Based on agent responses

FLOW CONTROL:
- Sequence: intake → (router) → handler → (check escalation) → optional escalation
- Branching: Different paths based on categorization
- Termination: End when task complete

USE CASES:
✓ Customer support workflows
✓ Document processing pipelines
✓ Approval workflows (draft → review → approve → publish)
✓ Troubleshooting decision trees
✓ Multi-step form processing

DIFFERENCE FROM SWARM:
- Graph: Sequential/conditional routing
- Swarm: All agents work together on same problem
    """)
