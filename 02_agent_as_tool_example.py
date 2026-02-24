"""
FILE 2: AGENT AS A TOOL
=======================

In this pattern:
- One agent can be wrapped and used as a TOOL by another agent
- The main agent doesn't need to know internal details of the sub-agent
- Sub-agent is called just like any other tool (calculator, API call, etc.)
- Main agent can use it for specific specialized tasks

Use case: Reusable agent functionality
Example: 
  - Main Agent uses "CodeReviewAgent" as a tool
  - Main Agent uses "SentimentAnalysisAgent" as a tool
  - Each agent is encapsulated and replaceable

KEY INSIGHT: Tools in Strands don't have to be simple functions!
They can be entire agents with their own logic, memory, and tools.
"""

from strands import Agent, tool
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================================================
# STEP 1: Initialize the Gemini Model
# We'll use the same model for both agents, but in production they could differ
# ============================================================================
gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)

# ============================================================================
# STEP 2: Create a Specialized Agent - CODE REVIEWER
# This agent will be wrapped as a tool
# ============================================================================
code_reviewer_agent = Agent(
    name="code_reviewer",
    system_prompt="""
You are an expert Code Reviewer. Your job is to:
1. Review Python code provided to you
2. Identify bugs, inefficiencies, and improvements
3. Provide specific feedback with line-by-line suggestions
4. Rate code quality on a scale of 1-10

Be concise and professional. Focus on:
- Performance issues
- Security vulnerabilities
- Code style and readability
- Best practices violations
""",
    model=gemini_model,
)

# ============================================================================
# STEP 3: Wrap the Agent as a TOOL using the @tool decorator
# This makes the specialized agent callable as a tool
# ============================================================================

@tool
def code_review(code_snippet: str, language: str = "python") -> str:
    """
    Review code and provide feedback.
    
    Args:
        code_snippet: The code to review
        language: Programming language (default: python)
    
    Returns:
        Detailed code review feedback
    
    NOTE: This tool internally runs the code_reviewer_agent
    The main agent doesn't know or care about that detail.
    It just calls code_review() like any other tool.
    """
    review_prompt = f"""Review this {language} code and provide feedback:

{code_snippet}

Provide:
1. Issues found
2. Improvements
3. Quality rating (1-10)
4. Specific suggestions
"""
    return code_reviewer_agent(review_prompt)


@tool
def code_optimize(code_snippet: str) -> str:
    """
    Optimize code for performance.
    Internally uses the code_reviewer_agent with optimization focus.
    """
    optimize_prompt = f"""Optimize this Python code for performance:

{code_snippet}

Provide:
1. Current time complexity
2. Optimization suggestions
3. Optimized version
4. Performance improvement estimate
"""
    return code_reviewer_agent(optimize_prompt)


# ============================================================================
# STEP 4: Create a MAIN Agent that uses the specialized agent as tools
# This is a project manager that delegates tasks
# ============================================================================
project_manager_agent = Agent(
    name="project_manager",
    system_prompt="""
You are a Project Manager overseeing code quality.

When you receive a request:
1. If it's about CODE REVIEW → use the code_review tool
2. If it's about CODE OPTIMIZATION → use the code_optimize tool
3. If it's about BOTH → use both tools in sequence
4. Summarize findings and next steps

You have access to specialized agents (as tools) for code-related tasks.
Use them to delegate work while you focus on overall quality management.
""",
    model=gemini_model,
    tools=[code_review, code_optimize],  # Specialized agents wrapped as tools
)

# ============================================================================
# STEP 5: Example: Use the Main Agent with Sub-Agent Tools
# ============================================================================

def agent_as_tool_example():
    """
    Demonstrate using agents as tools
    """
    print("\n" + "="*70)
    print("AGENT AS A TOOL - DEMONSTRATION")
    print("="*70)
    
    # Sample code to review
    sample_code = """
def find_max(arr):
    max_val = arr[0]
    for i in range(len(arr)):
        if arr[i] > max_val:
            max_val = arr[i]
    return max_val
"""
    
    # Request that main agent will handle
    request = f"""Please review this code and suggest optimizations:

{sample_code}

Focus on:
1. Readability
2. Performance
3. Edge cases
"""
    
    print("\n[PROJECT MANAGER] Processing request...")
    print(f"Request:\n{request}\n")
    
    # The main agent will use code_review and code_optimize tools
    # which internally call the code_reviewer_agent
    result = project_manager_agent(request)
    
    print("\n" + "="*70)
    print("PROJECT MANAGER'S SYNTHESIS:")
    print("="*70)
    print(result)
    
    return result


# ============================================================================
# STEP 6: Advanced Example - Chaining Agent Tools
# ============================================================================

def advanced_agent_tool_example():
    """
    Use multiple agent-tools in sequence
    """
    print("\n" + "="*70)
    print("ADVANCED: MULTIPLE AGENT TOOLS IN SEQUENCE")
    print("="*70)
    
    advanced_request = """
I have this Python function that works but feels slow:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

Tasks:
1. Review it for issues
2. Optimize it
3. Recommend the best approach

Use all available tools to give a comprehensive analysis.
"""
    
    print(f"\nRequest:\n{advanced_request}\n")
    result = project_manager_agent(advanced_request)
    
    print("\n" + "="*70)
    print("COMPREHENSIVE ANALYSIS (using multiple agent-tools):")
    print("="*70)
    print(result)
    
    return result


# ============================================================================
# STEP 7: Run Examples
# ============================================================================
if __name__ == "__main__":
    # Example 1: Simple code review
    agent_as_tool_example()
    
    # Example 2: Complex multi-tool analysis
    advanced_agent_tool_example()
    
    print("\n" + "="*70)
    print("KEY TAKEAWAY:")
    print("="*70)
    print("""
Agents can be wrapped as tools using @tool decorator.
This allows:
- Reusable agent logic across your application
- Encapsulation of complex agent workflows
- Easy composition of specialized agents
- Delegation without exposing implementation details

In this example:
- code_review and code_optimize are AGENTS wrapped as TOOLS
- project_manager_agent uses them without knowing their internals
- Each tool call runs the specialized agent's logic
- Results are seamlessly integrated
""")
