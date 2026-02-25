"""
=============================================================================
GUIDE: HOW TO CRAFT EFFECTIVE PROMPTS FOR AWS STRANDS DEVELOPMENT
=============================================================================

This guide helps you structure your requests for maximum clarity and results.

=============================================================================
SECTION 1: THE PROMPT FRAMEWORK
=============================================================================

An effective prompt has 5 key components:

1. CONTEXT (What are you building?)
2. ROLE (Who should I act as?)
3. TASK (What exactly do you want?)
4. REQUIREMENTS (What should be included?)
5. FORMAT (How should it be delivered?)

Let's break each down:

=============================================================================
SECTION 2: COMPONENT BREAKDOWN
=============================================================================

1. CONTEXT - Set the stage
   ────────────────────────
   WEAK:    "Create some files"
   STRONG:  "I'm learning AWS Strands framework and need practical examples"
   
   Why? Context helps me understand:
   - Your experience level (beginner vs. advanced)
   - Your project goal
   - What matters most to you
   
   TEMPLATE: "I'm [learning/building/fixing] [what] with [framework/language]"

---

2. ROLE - Define the persona
   ─────────────────────────
   WEAK:    "Help me"
   STRONG:  "Act as an AWS Strands framework engineer who worked on the 
             framework's development"
   
   Why? The role shapes the response style:
   - Technical depth
   - Explanation style
   - Assumptions about knowledge
   
   TEMPLATE: "Act as a [specific role] with [expertise]"

---

3. TASK - Be specific about what you want
   ───────────────────────────────────────
   WEAK:    "Explain Strands patterns"
   STRONG:  "Create 4 Python example files demonstrating: 
             (1) Agent-to-Agent communication, 
             (2) Agent as a Tool, 
             (3) Graph pattern, 
             (4) Swarm pattern"
   
   Why? Specific tasks prevent ambiguity:
   - I know exactly what deliverable to create
   - No need to guess or ask clarifying questions
   - You get what you actually want
   
   TEMPLATE: "Create [specific items] that [accomplishes X]"

---

4. REQUIREMENTS - Set expectations
   ──────────────────────────────────
   WEAK:    "With code and comments"
   STRONG:  "Each file should have:
             - Simple, beginner-friendly code
             - Detailed comments explaining each concept
             - Real-world use cases
             - Step-by-step workflow examples
             - Comparison to other patterns"
   
   Why? Requirements ensure quality:
   - Code complexity level
   - Comment density
   - Code style preferences
   - Educational approach
   
   TEMPLATE: "Each [deliverable] should include:
              - [requirement 1]
              - [requirement 2]
              - [requirement 3]"

---

5. FORMAT - Specify how you want it delivered
   ────────────────────────────────────────────
   WEAK:    "Give me code"
   STRONG:  "Create separate Python files in the AWS-STRANDS folder with:
             - Clear file naming (01_pattern_type_example.py)
             - Runnable examples
             - No external dependencies beyond what's in requirements.txt"
   
   Why? Format ensures usability:
   - Where files go
   - File organization
   - Naming conventions
   - Executable vs. documentation
   
   TEMPLATE: "Deliver as [format] with [location/naming/structure]"

=============================================================================
SECTION 3: PUTTING IT ALL TOGETHER
=============================================================================

BEFORE (Vague):
───────────────
"You are an AWS engineer. Create 4 files with examples."

AFTER (Clear):
──────────────
"You are an AWS Strands framework engineer. Create 4 Python example files 
demonstrating each major agent pattern:

1. Agent-to-Agent communication
2. Agent as a Tool
3. Graph pattern
4. Swarm pattern

Requirements for each file:
- Simple, beginner-to-intermediate code
- Detailed comments explaining the concept
- Real-world use case example
- Step-by-step workflow showing how it works
- Comparison to other patterns
- Use Gemini model for consistency

Format:
- Save in AWS-STRANDS folder
- Name as: 01_agent_to_agent_example.py, 02_agent_as_tool_example.py, etc.
- Make them runnable with proper imports
- Include example usage in __main__ block"

Result: Crystal clear deliverables ✓

=============================================================================
SECTION 4: COMMON PROMPT ANTI-PATTERNS & FIXES
=============================================================================

ANTI-PATTERN 1: Vague Goals
───────────────────────────
❌ "Help me with my project"
✅ "Help me debug the authentication flow in my FastAPI application by:
    1. Identifying where the token validation fails
    2. Suggesting fixes with code examples
    3. Explaining the root cause"

Why? Specific goals have specific solutions.

---

ANTI-PATTERN 2: Missing Context
────────────────────────────────
❌ "This code has a bug"
✅ "This Python code throws 'KeyError: user_id' when processing empty lists.
    It's part of a Strands agent that processes customer data.
    The error occurs at line 12 in the database query section."

Why? Context helps me understand the problem's scope and impact.

---

ANTI-PATTERN 3: Unclear Requirements
──────────────────────────────────────
❌ "Make it better"
✅ "Improve this code by:
    - Reducing time complexity from O(n²) to O(n)
    - Adding input validation
    - Adding error handling with specific exception types
    - Keeping it readable with comments"

Why? "Better" is subjective. Specific requirements are measurable.

---

ANTI-PATTERN 4: Assumption About My Knowledge
───────────────────────────────────────────────
❌ "Fix the AWS Strands issue"
✅ "In AWS Strands, when I create multiple agents with the same model,
    they seem to share context. How do I ensure each agent has isolated
    memory/context? Provide code example showing proper isolation."

Why? I need to know what you've already tried and what specifically fails.

---

ANTI-PATTERN 5: Too Much Information
──────────────────────────────────────
❌ "I was born in 1995, I like Python, my company is in Texas, we have
    100 employees, I want to build a multi-agent system..."
✅ "I need a multi-agent system for customer support using AWS Strands.
    Our team knows Python well. We need agents for: routing, bug handling,
    and escalation. Please create a Graph pattern example for this."

Why? Focus on relevant information. Extra details dilute the message.

=============================================================================
SECTION 5: TEMPLATE PROMPTS FOR COMMON TASKS
=============================================================================

TEMPLATE 1: "Create Example Code"
──────────────────────────────────
"Act as a [framework] expert. Create [X] [language] files demonstrating
[concept]. Each file should:
- Target [audience level] learners
- Include [specific features]
- Use [specific library/model]
- Have [comment/documentation level]
- Show [use case examples]
- Be saved in [location] with naming [convention]"

Example Usage:
"Act as an AWS Strands expert. Create 3 Python files demonstrating
Swarm patterns. Each file should target intermediate learners, include
error handling, use Gemini models, have detailed comments, show real-world
scenarios, and be in AWS-STRANDS folder named as swarm_pattern_01.py, etc."

---

TEMPLATE 2: "Debug or Fix Code"
─────────────────────────────────
"I have a [language] [component] in my [framework] project that [problem].
Context: [relevant code/error message]
What I've tried: [previous attempts]
Desired behavior: [expected outcome]
Please: [fix code/explain issue/suggest approach]"

Example Usage:
"I have a Python agent in my AWS Strands project that fails to pass context
between handoffs. Error: 'context not found'. What I've tried: passing
context object directly. Desired: agent should remember prior conversation.
Please suggest the correct way to maintain context in Strands."

---

TEMPLATE 3: "Explain a Concept"
─────────────────────────────────
"Explain [concept] for [audience level] learning [framework/language].
Include: [examples], [comparisons], [use cases], [code samples]
Focus on: [specific aspect]"

Example Usage:
"Explain the difference between Graph and Swarm patterns in AWS Strands
for intermediate learners. Include visual flow examples, use case comparisons,
code snippets, and when to use each. Focus on real-world decision-making."

=============================================================================
SECTION 6: CRAFTING YOUR NEXT PROMPT
=============================================================================

When you ask me next time, follow this structure:

[ CONTEXT ]
What are you building? What's your experience level?

[ ROLE ]
What expertise should I demonstrate?

[ TASK ]
What exactly do you want created/fixed/explained?

[ REQUIREMENTS ]
What specific criteria must be met?

[ FORMAT ]
How should it be delivered?

Example:
────────
Context: I'm building a customer support system using AWS Strands and
         I'm new to multi-agent frameworks.

Role: Act as an AWS Strands development expert.

Task: Create a complete customer support workflow that routes customer
      requests to appropriate specialist agents.

Requirements:
- Use Graph pattern for routing logic
- Support 3 types: bug reports, feature requests, general questions
- Include escalation path for complex issues
- Target beginner-intermediate developers
- Thoroughly commented code
- Real example data and outputs

Format:
- Single Python file in AWS-STRANDS folder
- Named: support_workflow_example.py
- Include sample execution at bottom
- Show expected output

=============================================================================
SECTION 7: QUICK CHECKLIST BEFORE ASKING
=============================================================================

Before you ask me for anything, check:

☐ Is my goal clear and specific?
☐ Did I mention the technology/framework?
☐ Are my requirements explicitly stated?
☐ Did I provide relevant context?
☐ Is the format specified?
☐ Could someone else understand exactly what I want?
☐ Have I avoided vague terms like "better", "improve", "fix"?
☐ Did I include examples of what I'm trying to do?

=============================================================================
SECTION 8: YOUR PERFECT PROMPT FORMULA
=============================================================================

[CONTEXT] I'm [action] [what] with [framework]
[ROLE] Act as [specific persona] with [expertise]
[TASK] Create/Debug/Explain [exactly what]
[REQUIREMENTS] Each [item] should include [specific criteria]
[FORMAT] Deliver as [format] in [location] with [naming/structure]

=============================================================================
FINAL TIPS
=============================================================================

1. BE SPECIFIC
   "Create a calculator agent" ❌
   "Create an Agent that calculates math expressions using Gemini model" ✅

2. SHOW EXAMPLES
   "Fix this code" ❌
   "Fix this code [paste code]. Expected output is [X], actual is [Y]" ✅

3. STATE ASSUMPTIONS
   "Help with the agent" ❌
   "Help with the agent; I'm using Strands 2.0, Gemini API, Python 3.11" ✅

4. EXPLAIN CONSTRAINTS
   "Make it work" ❌
   "Make it work without external packages beyond requirements.txt" ✅

5. SPECIFY AUDIENCE
   "Explain swarms" ❌
   "Explain swarms for someone new to multi-agent frameworks" ✅

=============================================================================
NOW YOU'RE READY!
=============================================================================

You now have 4 working example files:
✓ 01_agent_to_agent_example.py - Sequential delegation pattern
✓ 02_agent_as_tool_example.py - Hierarchical tool pattern
✓ 03_graph_pattern_example.py - Branching workflow pattern
✓ 04_swarm_pattern_example.py - Collaborative peer pattern

Each has:
✓ Detailed comments explaining every step
✓ Real-world use cases
✓ Complete working examples
✓ Comparison to other patterns
✓ Key insights section

Next time you need help, use the framework above and you'll get
exactly what you want!

=============================================================================
"""

# Quick reference for your project

PROMPT_EXAMPLES = {
    "for_debugging": """
    I'm debugging [issue] in my AWS Strands [component].
    
    The problem: [what happens vs what should happen]
    Code affected: [specific file/function]
    Error message: [exact error]
    Environment: [Python version, Strands version, etc.]
    
    Please: [what you want - fix, explanation, suggestions]
    """,
    
    "for_new_feature": """
    I need to add [feature] to my AWS Strands [project].
    
    Context: [what the feature should do]
    Pattern preference: [A2A | Agent-as-Tool | Graph | Swarm]
    Team knowledge: [beginner/intermediate/advanced]
    
    Requirements:
    - [requirement 1]
    - [requirement 2]
    - [requirement 3]
    
    Please create [files/code/explanation]
    """,
    
    "for_learning": """
    I want to understand [concept] in AWS Strands.
    
    Current knowledge: [what I already know]
    Use case: [what I'll use this for]
    Audience level: [beginner/intermediate/advanced]
    
    Please: [explain/show examples/compare patterns]
    With focus on: [specific aspect]
    """,
}

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*79)
    print("QUICK REFERENCE - Prompt Templates")
    print("="*79)
    for key, template in PROMPT_EXAMPLES.items():
        print(f"\n{key.upper()}:\n{template}\n")
