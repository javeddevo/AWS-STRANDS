"""
FILE 4: SWARM PATTERN
=====================

In this pattern:
- Multiple specialized agents work TOGETHER on the SAME problem
- All agents are equal peers (no hierarchy)
- Agents can call each other for help or validation
- Great for collaborative problem-solving

Use case: Complex problems needing multiple perspectives
Examples:
  - Code review: Developer + SecurityAgent + PerformanceAgent all review same code
  - Investment analysis: TechAgent + FinanceAgent + RiskAgent all analyze same opportunity
  - Content creation: Writer + Editor + SEOAgent all work on same article
  - Bug diagnosis: FrontendAgent + BackendAgent + DatabaseAgent collaborate

DIFFERENCE FROM GRAPH:
- Graph: Sequential steps (A → B → C)
- Swarm: Parallel collaboration (A, B, C work together)

DIFFERENCE FROM AGENT AS TOOL:
- Agent as Tool: Main agent calls sub-agent (hierarchical)
- Swarm: All agents are peers (collaborative, non-hierarchical)

Think of it like:
- Graph: Assembly line (one product, multiple stations)
- Agent as Tool: Boss delegating to assistants
- Swarm: Team brainstorm where everyone contributes equally
"""

from strands import Agent, tool
from strands.models.gemini import GeminiModel
from strands.multiagent import Swarm
from dotenv import load_dotenv
import os
import json

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
# STEP 2: Define SWARM MEMBERS (Peer Agents)
# Each agent is a specialist that contributes to solving the problem
# They are NOT hierarchical - they are PEERS
# ============================================================================

# SWARM MEMBER 1: SECURITY AGENT
# Focuses on security aspects of code
security_agent = Agent(
    name="security_expert",
    system_prompt="""
You are a Security Expert in a peer team reviewing code.

Your role:
- Identify security vulnerabilities
- Check for common security issues:
  * SQL injection risks
  * Authentication/authorization flaws
  * Encryption issues
  * Input validation problems
- Provide security recommendations

Work collaboratively with other agents. You can:
- Ask questions to other agents
- Challenge their assumptions
- Provide security perspective

Output format:
SECURITY ANALYSIS:
- Vulnerabilities found: [list]
- Risk level: [CRITICAL | HIGH | MEDIUM | LOW]
- Recommendations: [list]
- Confidence: [your assessment confidence]
""",
    model=gemini_model,
)

# SWARM MEMBER 2: PERFORMANCE AGENT
# Focuses on performance and optimization
performance_agent = Agent(
    name="performance_expert",
    system_prompt="""
You are a Performance Expert in a peer team reviewing code.

Your role:
- Identify performance bottlenecks
- Analyze algorithmic complexity
- Check for memory leaks/inefficiencies
- Suggest optimizations
- Consider scalability

Work collaboratively with other agents. You can:
- Question design decisions
- Suggest trade-offs
- Provide performance perspective

Output format:
PERFORMANCE ANALYSIS:
- Bottlenecks found: [list]
- Time complexity: [O(n) notation]
- Space complexity: [O(n) notation]
- Optimization opportunities: [list]
- Confidence: [your assessment confidence]
""",
    model=gemini_model,
)

# SWARM MEMBER 3: CODE QUALITY AGENT
# Focuses on code readability and maintainability
quality_agent = Agent(
    name="quality_expert",
    system_prompt="""
You are a Code Quality Expert in a peer team reviewing code.

Your role:
- Assess code readability and clarity
- Check coding standards and style
- Evaluate maintainability
- Look for code smells and anti-patterns
- Suggest refactoring improvements

Work collaboratively with other agents. You can:
- Provide counterpoints
- Validate other agents' findings
- Provide quality perspective

Output format:
QUALITY ANALYSIS:
- Code smells found: [list]
- Readability score: [1-10]
- Maintainability issues: [list]
- Refactoring suggestions: [list]
- Confidence: [your assessment confidence]
""",
    model=gemini_model,
)

# SWARM MEMBER 4: ARCHITECT AGENT
# The coordinator who synthesizes all perspectives
architect_agent = Agent(
    name="architect",
    system_prompt="""
You are a Software Architect leading a peer review team.

Your role:
- Receive feedback from all team members
- Synthesize their findings
- Identify conflicts and consensus
- Make final recommendations
- Consider trade-offs between security, performance, and quality

You work WITH your team members, not above them. You:
- Acknowledge all perspectives
- Explain trade-offs
- Provide holistic recommendations

OUTPUT FORMAT:
ARCHITECTURE DECISION:
- Overall assessment: [ACCEPT | REVISE | REJECT]
- Key findings: [synthesized from all agents]
- Trade-offs acknowledged: [list]
- Final recommendations: [prioritized list]
- Risk mitigation: [list]
""",
    model=gemini_model,
)

# ============================================================================
# STEP 3: Optional Tools for Swarm Members
# Tools can help agents investigate and collaborate better
# ============================================================================

@tool
def consult_security_expert(question: str) -> str:
    """
    Any agent can consult the security expert
    """
    return security_agent(f"A team member is asking: {question}\n\nProvide your security perspective.")


@tool
def consult_performance_expert(question: str) -> str:
    """
    Any agent can consult the performance expert
    """
    return performance_agent(f"A team member is asking: {question}\n\nProvide your performance perspective.")


@tool
def consult_quality_expert(question: str) -> str:
    """
    Any agent can consult the quality expert
    """
    return quality_agent(f"A team member is asking: {question}\n\nProvide your quality perspective.")


# ============================================================================
# STEP 4: Create the SWARM
# All agents work together on the same problem
# ============================================================================

def create_code_review_swarm():
    """
    Create a swarm of agents for collaborative code review
    
    Structure:
    - security_expert: Reviews for security issues
    - performance_expert: Reviews for performance issues
    - quality_expert: Reviews for code quality issues
    - architect: Synthesizes all perspectives and makes recommendations
    
    All agents are peers and can interact with each other
    """
    
    swarm = Swarm(
        agents=[
            security_agent,
            performance_agent,
            quality_agent,
            architect_agent,
        ],
        entry_point=architect_agent,  # Start with architect who coordinates
        max_handoffs=10,  # Allow agents to discuss/collaborate
        max_iterations=15,  # Give swarm time to reach consensus
        execution_timeout=300.0,  # 5 minute timeout
        node_timeout=120.0,  # 2 minute per agent timeout
    )
    
    return swarm


# ============================================================================
# STEP 5: Run Swarm Examples
# ============================================================================

def example_code_review_swarm():
    """
    Example: Swarm of agents reviewing code together
    """
    
    print("\n" + "="*70)
    print("SWARM PATTERN - COLLABORATIVE CODE REVIEW")
    print("="*70)
    
    # Code to review
    code_to_review = """
def process_user_data(user_id, data):
    import sqlite3
    
    # Connect to database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Query using string concatenation (VULNERABLE!)
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    cursor.execute(query)
    
    # Process data
    result = []
    for row in cursor.fetchall():
        if len(data) > 0:
            # O(n²) complexity due to nested loops
            for d in data:
                if row[1] == d['name']:
                    # Complex nested processing
                    processed = {
                        'id': row[0],
                        'name': row[1],
                        'email': row[2],
                        'phone': row[3],
                        'address': row[4],
                        'data': d
                    }
                    result.append(processed)
    
    conn.close()
    return result
"""
    
    # Request for swarm to review
    review_request = f"""
Please perform a comprehensive code review of this Python function:

{code_to_review}

Each of you review this from your perspective:
- Security expert: Check for security vulnerabilities
- Performance expert: Check for performance issues
- Quality expert: Check for code quality and readability
- Architect: Synthesize all findings and make recommendations

Work together, discuss, and reach consensus on the overall assessment.
"""
    
    print("\nStarting swarm review of code sample...")
    print("(All agents collaborate on this code)\n")
    
    # Create and run the swarm
    swarm = create_code_review_swarm()
    
    try:
        result = swarm(review_request)
        
        print("\n" + "="*70)
        print("SWARM REVIEW COMPLETE")
        print("="*70)
        print(f"\nFinal Output:\n{result.output}")
        print(f"\nSwarm Status: {result.status}")
        print(f"Agent Sequence: {[node.node_id for node in result.node_history]}")
        
        return result
        
    except Exception as e:
        print(f"\nSwarm execution error: {e}")
        print("\nNote: This is expected if your environment isn't fully configured.")
        print("The Swarm pattern requires proper agent setup and communication.")
        return None


# ============================================================================
# STEP 6: Manual Swarm Orchestration
# (For demonstration without Swarm auto-orchestration)
# ============================================================================

def manual_swarm_collaboration(code_snippet: str):
    """
    Manual orchestration of swarm members for collaborative review
    This shows how agents work together even without auto-orchestration
    """
    
    print("\n" + "="*70)
    print("SWARM PATTERN - MANUAL ORCHESTRATION (All Agents Collaborate)")
    print("="*70)
    
    # PHASE 1: Individual Reviews
    print("\n[PHASE 1] Individual Agent Reviews")
    print("-" * 70)
    
    # Security review
    print("\n1. SECURITY EXPERT reviewing...")
    security_review = security_agent(
        f"Review this code for security issues:\n{code_snippet}"
    )
    print(f"Security Review:\n{security_review}\n")
    
    # Performance review
    print("2. PERFORMANCE EXPERT reviewing...")
    performance_review = performance_agent(
        f"Review this code for performance issues:\n{code_snippet}"
    )
    print(f"Performance Review:\n{performance_review}\n")
    
    # Quality review
    print("3. QUALITY EXPERT reviewing...")
    quality_review = quality_agent(
        f"Review this code for quality issues:\n{code_snippet}"
    )
    print(f"Quality Review:\n{quality_review}\n")
    
    # PHASE 2: Architect Synthesis
    print("\n[PHASE 2] Architect Synthesizes All Perspectives")
    print("-" * 70)
    
    synthesis_prompt = f"""
You are the architect synthesizing a collaborative code review.

Here are the individual reviews:

SECURITY EXPERT'S ASSESSMENT:
{security_review}

PERFORMANCE EXPERT'S ASSESSMENT:
{performance_review}

CODE QUALITY EXPERT'S ASSESSMENT:
{quality_review}

Now synthesize all these perspectives into ONE final recommendation.
Consider:
- Which issues are critical vs. nice-to-have?
- What trade-offs exist between security, performance, and quality?
- What should be fixed immediately vs. refactored later?
- What's the overall verdict on this code?

Provide a final architectural decision with all team perspectives considered.
"""
    
    final_recommendation = architect_agent(synthesis_prompt)
    
    print(f"\nARCHITECT'S SYNTHESIS:\n{final_recommendation}\n")
    
    return {
        "security": security_review,
        "performance": performance_review,
        "quality": quality_review,
        "final": final_recommendation
    }


# ============================================================================
# STEP 7: Run Examples
# ============================================================================

if __name__ == "__main__":
    # Sample code with obvious issues
    sample_code = """
def calculate_fibonacci(n):
    results = []
    for i in range(n):
        if i <= 1:
            results.append(i)
        else:
            # This is exponential complexity - very slow!
            results.append(calculate_fibonacci(i-1) + calculate_fibonacci(i-2))
    return results
"""
    
    print("\n" + "█"*70)
    print("EXAMPLE 1: MANUAL SWARM COLLABORATION")
    print("█"*70)
    
    # Run manual orchestration
    manual_result = manual_swarm_collaboration(sample_code)
    
    print("\n" + "█"*70)
    print("EXAMPLE 2: AUTO SWARM ORCHESTRATION (Strands-managed)")
    print("█"*70)
    
    # Try to run auto-orchestrated swarm
    # (This requires full Strands configuration)
    auto_result = example_code_review_swarm()
    
    print("\n" + "="*70)
    print("SWARM PATTERN KEY CONCEPTS")
    print("="*70)
    print("""
SWARM CHARACTERISTICS:
✓ All agents are PEERS (equal authority)
✓ Agents work on SAME problem (not sequential)
✓ Agents can INTERACT and COLLABORATE
✓ No central hierarchy or boss
✓ Consensus-driven decision making

AGENTS IN OUR EXAMPLE:
1. security_expert: Security perspective
2. performance_expert: Performance perspective
3. quality_expert: Code quality perspective
4. architect: Synthesizes all perspectives

SWARM BENEFITS:
✓ Multiple perspectives on same problem
✓ Better decision-making (team consensus)
✓ Faster problem solving (parallel work)
✓ Resilient (if one agent fails, others continue)
✓ More thorough analysis

USE CASES:
✓ Code review (security + performance + quality)
✓ Product decisions (tech + business + design teams)
✓ Risk analysis (multiple risk experts)
✓ Content review (multiple editors/reviewers)
✓ Complex problem solving (diverse specialists)

ORCHESTRATION MODES:

1. AUTO-ORCHESTRATED (Strands manages flow):
   - Agents can handoff to each other automatically
   - Strands decides when to loop/continue
   - Uses Swarm class

2. MANUAL-ORCHESTRATED (You control flow):
   - You call each agent sequentially
   - You manage the collaboration flow
   - More explicit control

KEY DIFFERENCE FROM OTHER PATTERNS:

A2A (Agent-to-Agent): Sequential delegation
  - Coordinator → Researcher → Analyst
  - Hierarchical

Agent as Tool: Hierarchical delegation
  - Main agent calls sub-agent as tool
  - Sub-agent is subordinate

Graph: Sequential branching
  - intake → (route) → bug_handler OR feature_handler
  - Step-by-step workflow

Swarm: Collaborative peer agents
  - All agents = peers
  - All work on same problem
  - Parallel/interactive
    """)
