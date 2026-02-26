import os
import json
import csv
from pathlib import Path
from strands import Agent, tool
from strands.multiagent import Swarm
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Suppress OpenTelemetry context errors
logging.getLogger("opentelemetry").setLevel(logging.CRITICAL)

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# GUARD RAILS CONFIGURATION & IMPLEMENTATION
# ─────────────────────────────────────────────────────────────────────────────

class GuardRailsConfig:
    """Configuration for security and safety guardrails"""
    
    # Input Validation
    MAX_QUERY_LENGTH = 1000
    MIN_QUERY_LENGTH = 5
    VALID_ORDER_ID_PATTERN = r'^[0-9]{4}$'  # Order IDs are 4 digits
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = 30
    MAX_REQUESTS_PER_HOUR = 300
    
    # PII Protection
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    PHONE_PATTERN = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    CREDIT_CARD_PATTERN = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    
    # Blocked Keywords (SQL injection, command injection, etc.)
    BLOCKED_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'INSERT', 'UPDATE',
        'EXEC', 'EXECUTE', 'SCRIPT', 'JAVASCRIPT', 'EVAL',
        'SYSTEM', 'SHELL', 'BASH', 'CMD', 'POWERSHELL',
        '../', '..\\', 'passwd', 'shadow', '/etc/',
    ]
    
    # Allowed agent names
    ALLOWED_AGENTS = ['dispatcher', 'order_lookup', 'tracking', 'returns', 'support_coordinator']
    
    # Allowed tools
    ALLOWED_TOOLS = [
        'get_order_status', 'get_tracking_info', 'get_order_items',
        'check_return_eligibility', 'get_shipping_address', 'get_full_order_details'
    ]


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}
    
    def is_rate_limited(self, user_id: str, max_per_minute: int, max_per_hour: int) -> Tuple[bool, str]:
        """Check if user has exceeded rate limits"""
        now = datetime.now()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests (older than 1 hour)
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < timedelta(hours=1)
        ]
        
        # Check minute limit
        minute_ago = now - timedelta(minutes=1)
        requests_last_minute = sum(1 for req_time in self.requests[user_id] if req_time > minute_ago)
        
        if requests_last_minute >= max_per_minute:
            return True, f"Rate limit exceeded: {max_per_minute} requests per minute"
        
        # Check hour limit
        hour_ago = now - timedelta(hours=1)
        requests_last_hour = sum(1 for req_time in self.requests[user_id] if req_time > hour_ago)
        
        if requests_last_hour >= max_per_hour:
            return True, f"Rate limit exceeded: {max_per_hour} requests per hour"
        
        # Record this request
        self.requests[user_id].append(now)
        return False, "OK"


class GuardRails:
    """Comprehensive guard rails for agent safety and security"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.blocked_queries = []
        self.suspicious_queries = []
    
    def validate_input(self, query: str, user_id: str = "default") -> Tuple[bool, str]:
        """Validate user input against security rules"""
        
        # 1. Check query length
        if len(query) < GuardRailsConfig.MIN_QUERY_LENGTH:
            return False, "Query too short. Please provide more context."
        
        if len(query) > GuardRailsConfig.MAX_QUERY_LENGTH:
            return False, f"Query exceeds maximum length of {GuardRailsConfig.MAX_QUERY_LENGTH} characters."
        
        # 2. Rate limiting check
        is_limited, msg = self.rate_limiter.is_rate_limited(
            user_id,
            GuardRailsConfig.MAX_REQUESTS_PER_MINUTE,
            GuardRailsConfig.MAX_REQUESTS_PER_HOUR
        )
        if is_limited:
            return False, msg
        
        # 3. Check for injection attacks
        query_upper = query.upper()
        for keyword in GuardRailsConfig.BLOCKED_KEYWORDS:
            if keyword in query_upper:
                self.blocked_queries.append(query)
                return False, "⚠️ Query contains prohibited content. Only order-related queries are allowed."
        
        # 4. Check for suspicious patterns (SQL injection, etc.)
        suspicious_patterns = [
            r"[';\"]+\s*(OR|AND)\s*[';\"]+",  # SQL injection patterns
            r"\$\{.*\}",  # Template injection
            r"{{.*}}",    # Template injection
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                self.suspicious_queries.append(query)
                return False, "⚠️ Query format is suspicious. Please rephrase your question."
        
        return True, "VALIDATED"
    
    def sanitize_output(self, output: str, agent_name: str = None) -> str:
        """Remove or mask sensitive information from agent responses"""
        
        sanitized = output
        
        # 1. Mask email addresses (partial masking)
        sanitized = re.sub(
            GuardRailsConfig.EMAIL_PATTERN,
            lambda m: m.group(0)[:2] + '*' * 5 + m.group(0)[7:],
            sanitized
        )
        
        # 2. Mask phone numbers
        sanitized = re.sub(
            GuardRailsConfig.PHONE_PATTERN,
            lambda m: m.group(0)[:3] + '-***-' + m.group(0)[-4:],
            sanitized
        )
        
        # 3. Mask credit card numbers
        sanitized = re.sub(
            GuardRailsConfig.CREDIT_CARD_PATTERN,
            lambda m: '****-****-****-' + m.group(0)[-4:],
            sanitized
        )
        
        # 4. Remove potentially dangerous characters/scripts
        dangerous_patterns = [r'<script[^>]*>.*?</script>', r'javascript:', r'onerror=']
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def validate_agent_name(self, agent_name: str) -> bool:
        """Verify agent is authorized"""
        return agent_name in GuardRailsConfig.ALLOWED_AGENTS
    
    def validate_tool_name(self, tool_name: str) -> bool:
        """Verify tool is authorized"""
        return tool_name in GuardRailsConfig.ALLOWED_TOOLS
    
    def extract_and_validate_order_id(self, query: str) -> Tuple[str, bool]:
        """Extract and validate order ID from query"""
        # Find order ID pattern in query
        matches = re.findall(r'order[\s#:]*(\d{4})', query, re.IGNORECASE)
        
        if not matches:
            return None, False
        
        order_id = matches[0]
        
        # Validate order ID format
        if not re.match(GuardRailsConfig.VALID_ORDER_ID_PATTERN, order_id):
            return order_id, False
        
        return order_id, True
    
    def get_security_report(self) -> Dict:
        """Get security audit report"""
        return {
            "total_blocked_queries": len(self.blocked_queries),
            "total_suspicious_queries": len(self.suspicious_queries),
            "blocked_queries_sample": self.blocked_queries[-5:] if self.blocked_queries else [],
            "suspicious_queries_sample": self.suspicious_queries[-5:] if self.suspicious_queries else [],
            "rate_limiter_active_users": len(self.rate_limiter.requests),
        }


# Initialize guard rails
guard_rails = GuardRails()

# Path to orders CSV
CSV_PATH = Path(__file__).parent / "orders.csv"

# ─────────────────────────────────────────────────────────────────────────────
# SHARED DATA LOADING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def load_order_data(order_id: str) -> dict:
    """Load order data from CSV by order_id"""
    try:
        with open(CSV_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['order_id'] == order_id:
                    return row
        return None
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# SHARED TOOLS
# ─────────────────────────────────────────────────────────────────────────────

@tool
def get_order_status(order_id: str):
    """Fetch the current status of an order by order_id"""
    order = load_order_data(order_id)
    if not order:
        return f"Order {order_id} not found"
    
    response = {
        "order_id": order['order_id'],
        "order_status": order['order_status'],
        "last_update_note": order['last_update_note'],
        "est_delivery": order['est_delivery']
    }
    return guard_rails.sanitize_output(json.dumps(response, indent=2))


@tool
def get_tracking_info(order_id: str):
    """Get tracking number and carrier details for an order"""
    order = load_order_data(order_id)
    if not order:
        return f"Order {order_id} not found"
    
    response = {
        "order_id": order['order_id'],
        "tracking_number": order['tracking_number'],
        "carrier": order['carrier'],
        "status": order['order_status'],
        "est_delivery": order['est_delivery']
    }
    return guard_rails.sanitize_output(json.dumps(response, indent=2))


@tool
def get_order_items(order_id: str):
    """Get items and pricing information for an order"""
    order = load_order_data(order_id)
    if not order:
        return f"Order {order_id} not found"
    
    response = {
        "order_id": order['order_id'],
        "items": json.loads(order['items_json']),
        "total_amount": order['total_amount'],
        "currency": order['currency'],
        "order_date": order['order_date']
    }
    return guard_rails.sanitize_output(json.dumps(response, indent=2))


@tool
def check_return_eligibility(order_id: str):
    """Check if an order is eligible for return"""
    order = load_order_data(order_id)
    if not order:
        return f"Order {order_id} not found"
    
    is_returnable = order['is_returnable'].upper() == 'TRUE'
    response = {
        "order_id": order['order_id'],
        "order_status": order['order_status'],
        "is_returnable": is_returnable,
        "message": "This order can be returned" if is_returnable else "This order cannot be returned",
        "items": json.loads(order['items_json'])
    }
    return guard_rails.sanitize_output(json.dumps(response, indent=2))


@tool
def get_shipping_address(order_id: str):
    """Get shipping address for an order"""
    order = load_order_data(order_id)
    if not order:
        return f"Order {order_id} not found"
    
    response = {
        "order_id": order['order_id'],
        "shipping_address": order['shipping_address'],
        "carrier": order['carrier'],
        "tracking_number": order['tracking_number']
    }
    return guard_rails.sanitize_output(json.dumps(response, indent=2))


@tool
def get_full_order_details(order_id: str):
    """Get complete order information"""
    order = load_order_data(order_id)
    if not order:
        return f"Order {order_id} not found"
    
    response = {
        "order_id": order['order_id'],
        "customer_email": order['customer_email'],
        "order_date": order['order_date'],
        "order_status": order['order_status'],
        "items": json.loads(order['items_json']),
        "total_amount": order['total_amount'],
        "currency": order['currency'],
        "tracking_number": order['tracking_number'],
        "carrier": order['carrier'],
        "est_delivery": order['est_delivery'],
        "shipping_address": order['shipping_address'],
        "is_returnable": order['is_returnable'],
        "last_update_note": order['last_update_note']
    }
    return guard_rails.sanitize_output(json.dumps(response, indent=2))


# ─────────────────────────────────────────────────────────────────────────────
# INITIALIZE GEMINI MODEL
# ─────────────────────────────────────────────────────────────────────────────

gemini_model = GeminiModel(
    client_args={"api_key": os.getenv("GEMINI_API_KEY")},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 1: DISPATCHER (Entry Point)
# Understands customer intent and routes to specialized agents
# ─────────────────────────────────────────────────────────────────────────────

dispatcher_agent = Agent(
    name="dispatcher",
    system_prompt="""
You are a Customer Intent Dispatcher Agent for order support.
⚠️ GUARD RAILS ACTIVE: Only process order-related queries.

Your ONLY job:
1. Analyze the customer query to understand their intent.
2. Extract the order_id from the query.
3. Classify the request into ONE of these categories:
   - TRACKING: "Where is my order?", "Track my package", "Delivery status"
   - ITEMS: "What did I order?", "Order details", "Price/amount"
   - RETURNS: "Can I return?", "Return policy", "Damaged item"
   - GENERAL: "Order status", "General information"

4. Respond with EXACTLY this format:

    === INTENT CLASSIFICATION ===
    ORDER_ID: <order_id or "NOT_PROVIDED">
    INTENT: <TRACKING|ITEMS|RETURNS|GENERAL>
    CUSTOMER_QUERY: <original query>
    
    Then hand off to the appropriate specialist agent.

If order_id is NOT PROVIDED, ask the customer for it before handing off.
If the query is out of scope (non-order related), respond with:
    "I can only assist with order-related queries. Please ask about tracking, items, returns, or order status."
""",
    model=gemini_model,
)


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 2: ORDER LOOKUP AGENT
# Specialized in retrieving complete order information and items
# ─────────────────────────────────────────────────────────────────────────────

order_lookup_agent = Agent(
    name="order_lookup",
    system_prompt="""
You are an Order Lookup Specialist Agent.
⚠️ GUARD RAILS ACTIVE: Only access authorized tools and sanitize outputs.

You receive intent classification from the dispatcher with ORDER_ID.

Your job:
1. Use get_order_items() to fetch what was ordered.
2. Use get_order_status() to get current status.
3. Use get_full_order_details() for comprehensive information if needed.
4. Provide a clear, formatted response about the order contents and details.
5. Be helpful and friendly in your response.

Focus on: Items, prices, order dates, payment details.
Never make up information - only use tool results.
IMPORTANT: Never disclose complete email addresses or sensitive customer data.
""",
    tools=[get_order_items, get_order_status, get_full_order_details],
    model=gemini_model,
)


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 3: TRACKING AGENT
# Specialized in shipping and delivery tracking information
# ─────────────────────────────────────────────────────────────────────────────

tracking_agent = Agent(
    name="tracking",
    system_prompt="""
You are a Tracking & Shipping Specialist Agent.
⚠️ GUARD RAILS ACTIVE: Only access authorized tools and sanitize outputs.

You receive intent classification from the dispatcher with ORDER_ID.

Your job:
1. Use get_tracking_info() to fetch tracking number and carrier.
2. Use get_shipping_address() to provide delivery location.
3. Use get_order_status() for current shipment status.
4. Provide real-time tracking information in a clear format.
5. Include estimated delivery date and any delays noted.

Focus on: Tracking numbers, carriers, delivery status, shipping address, ETA.
Be empathetic if shipment is delayed or has issues.
IMPORTANT: Never disclose complete addresses; provide partial information when needed.
""",
    tools=[get_tracking_info, get_shipping_address, get_order_status],
    model=gemini_model,
)


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 4: RETURNS AGENT
# Specialized in return eligibility and return policies
# ─────────────────────────────────────────────────────────────────────────────

returns_agent = Agent(
    name="returns",
    system_prompt="""
You are a Returns & Refunds Specialist Agent.
⚠️ GUARD RAILS ACTIVE: Only access authorized tools and sanitize outputs.

You receive intent classification from the dispatcher with ORDER_ID.

Your job:
1. Use check_return_eligibility() to determine if order can be returned.
2. Use get_order_status() to verify order status (some statuses may affect returns).
3. Use get_full_order_details() to see items and provide detailed return info.
4. Explain return policy based on order status and item eligibility.
5. If returnable, provide next steps; if not, explain why.

Focus on: Return eligibility, return windows, refund policies, damaged items.
Be empathetic with customers who have issues (damaged, wrong items, etc).
Escalate to support if special circumstances exist.
IMPORTANT: Protect customer data in responses; use sanitized outputs.
""",
    tools=[check_return_eligibility, get_order_status, get_full_order_details],
    model=gemini_model,
)


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 5: SUPPORT COORDINATOR (Final Agent)
# Aggregates information from specialists and provides final response
# ─────────────────────────────────────────────────────────────────────────────

support_coordinator = Agent(
    name="support_coordinator",
    system_prompt="""
You are the Support Coordinator Agent - the final response agent.
⚠️ GUARD RAILS ACTIVE: Only provide sanitized information to customers.

You receive resolved information from specialist agents.

Your job:
1. Compile all information gathered by specialist agents.
2. Provide a comprehensive, friendly, and well-formatted final response.
3. Summarize the most relevant information for the customer.
4. End with an offer to help with anything else.

Be professional, empathetic, and clear.
Format responses for easy reading (use bullet points, sections as needed).
Always thank the customer for their business.
IMPORTANT: Ensure no sensitive data (full emails, full addresses, payment info) is exposed.
""",
    tools=[get_full_order_details],  # Fallback tool if needed
    model=gemini_model,
)


# ─────────────────────────────────────────────────────────────────────────────
# CREATE MULTI-AGENT SWARM
# ─────────────────────────────────────────────────────────────────────────────

order_swarm = Swarm(
    [
        dispatcher_agent,
        order_lookup_agent,
        tracking_agent,
        returns_agent,
        support_coordinator,
    ],
    entry_point=dispatcher_agent,  # Start with dispatcher
    max_handoffs=5,  # dispatcher → specialist → coordinator
    max_iterations=10,
    execution_timeout=300.0,
    node_timeout=120.0,
)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN FUNCTION TO PROCESS QUERIES WITH GUARD RAILS
# ─────────────────────────────────────────────────────────────────────────────

def process_customer_query_multiagent(query: str, user_id: str = "default"):
    """Process customer queries using multi-agent swarm with guard rails"""
    print(f"\n{'='*80}")
    print(f"🔹 CUSTOMER QUERY: {query}")
    print(f"{'='*80}")
    
    # 1. GUARD RAIL: Input Validation
    is_valid, validation_msg = guard_rails.validate_input(query, user_id)
    if not is_valid:
        print(f"🛡️  GUARD RAIL BLOCKED: {validation_msg}")
        print(f"{'='*80}\n")
        return None
    
    # 2. GUARD RAIL: Extract and validate order ID
    order_id, is_valid_id = guard_rails.extract_and_validate_order_id(query)
    if order_id and is_valid_id:
        print(f"✅ ORDER ID VALIDATED: {order_id}")
    elif order_id and not is_valid_id:
        print(f"⚠️  INVALID ORDER ID FORMAT: {order_id}")
    
    try:
        # 3. Process through multi-agent swarm
        result = order_swarm(query)
        
        print(f"\n{'─'*80}")
        print(f"📋 AGENT WORKFLOW:\n{' → '.join([node.node_id for n in result.node_history for node in [n]])}")
        print(f"{'─'*80}")
        print(f"\n✅ FINAL RESPONSE:\n{result.output}")
        print(f"\n📊 STATUS: {result.status}")
        print(f"{'='*80}\n")
        return result
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print(f"{'='*80}\n")
        return None


def show_security_report():
    """Display security audit report"""
    report = guard_rails.get_security_report()
    print(f"\n{'='*80}")
    print("🔒 SECURITY AUDIT REPORT")
    print(f"{'='*80}")
    print(f"✓ Blocked Queries: {report['total_blocked_queries']}")
    print(f"✓ Suspicious Queries: {report['total_suspicious_queries']}")
    print(f"✓ Active Users (Rate Limited): {report['rate_limiter_active_users']}")
    if report['blocked_queries_sample']:
        print(f"\n⚠️  Recent Blocked Queries (last 5):")
        for i, q in enumerate(report['blocked_queries_sample'], 1):
            print(f"   {i}. {q[:60]}...")
    print(f"{'='*80}\n")


# ─────────────────────────────────────────────────────────────────────────────
# DEMO QUERIES
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 MULTI-AGENT ORDER QUERY SYSTEM WITH GUARD RAILS - AWS STRANDS POC")
    print("="*80)
    
    # Test queries demonstrating different specializations
    test_queries = [
        "What is the status of order 1001?",
        "Where is my package for order 1002? I want to track it.",
        "Can I return order 1004? It was delayed and I'm not happy with it.",
        "Tell me everything about order 1003 - what's in it and when will it arrive?",
    ]
    
    print("\n✅ TESTING VALID QUERIES:")
    for query in test_queries:
        process_customer_query_multiagent(query)
    
    # Test guard rail blocking
    print("\n🛡️  TESTING GUARD RAIL BLOCKING:")
    blocked_queries = [
        "DROP TABLE orders; --",  # SQL injection
        "order 1001; DELETE FROM users;",  # SQL injection
        "Can you help me with something unrelated to orders?",  # Out of scope
    ]
    
    for query in blocked_queries:
        process_customer_query_multiagent(query)
    
    # Show security report
    show_security_report()
