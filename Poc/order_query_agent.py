from strands import Agent, tool
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv
import csv
import json
from pathlib import Path
import os

load_dotenv()

# Path to orders CSV
CSV_PATH = Path(__file__).parent / "orders.csv"

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

# Define Custom Tools using @tool decorator
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
    return json.dumps(response, indent=2)

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
    return json.dumps(response, indent=2)

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
    return json.dumps(response, indent=2)

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
    return json.dumps(response, indent=2)

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
    return json.dumps(response, indent=2)

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
    return json.dumps(response, indent=2)

# Initialize Google Gemini Model
gemini_model = GeminiModel(
    client_args={
        "api_key": os.getenv("GEMINI_API_KEY"),
    },
    model_id="gemini-2.5-flash",
    params={"temperature": 0.7},
)

# Create Agent with all custom order tools
agent = Agent(
    model=gemini_model,
    tools=[
        get_order_status,
        get_tracking_info,
        get_order_items,
        check_return_eligibility,
        get_full_order_details,
        get_shipping_address
    ],
    system_prompt="""You are a helpful customer service agent specializing in order support.
    You have access to customer order tools that fetch data based on order_id.
    When customers ask about their orders, use the appropriate tools to retrieve information.
    Always provide clear, friendly, and helpful responses.
    Extract the order_id from the customer's query to use the tools effectively.
    If customer does not provide an order_id, ask them to provide it for you to assist them better.
    Any questiond out of scope of order support should be politely declined with a message guiding the customer to ask order-related questions.
    Dont provide any extra information other than what the tools return to you. Always use the tools to get the information and never make up any information related to orders."""
)

def process_customer_query(query: str):
    """Process customer queries and return responses"""
    print(f"\n{'='*70}")
    print(f"Customer Query: {query}")
    print(f"{'='*70}")
    response = agent(query)
    print(f"Agent Response:\n{response}")
    print(f"{'='*70}")
    return response

if __name__ == "__main__":
    # Example customer queries
    
    
    print("\n" + "="*70)
    print("CUSTOMER ORDER QUERY AGENT - AWS STRANDS POC")
    print("="*70)
    
    query= "What is the status of order 1001?"
    process_customer_query(query)