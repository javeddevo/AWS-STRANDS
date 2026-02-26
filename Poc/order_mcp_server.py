from mcp.server import FastMCP
import csv
import json
from pathlib import Path

# Initialize MCP Server
mcp = FastMCP("Order Server")

# Path to orders CSV
CSV_PATH = Path(__file__).parent / "orders.csv"

def load_all_orders() -> list:
    """Load all orders from CSV"""
    try:
        orders = []
        with open(CSV_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                orders.append(row)
        return orders
    except Exception as e:
        return []

def find_order_by_id(order_id: str) -> dict:
    """Find a single order by order_id"""
    try:
        with open(CSV_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['order_id'] == order_id:
                    return row
        return None
    except Exception as e:
        return {"error": str(e)}

def find_orders_by_email(email: str) -> list:
    """Find all orders by customer email"""
    try:
        orders = []
        with open(CSV_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['customer_email'].lower() == email.lower():
                    orders.append(row)
        return orders
    except Exception as e:
        return []

# ============================================================================
# MCP TOOLS - Order Query Tools
# ============================================================================

@mcp.tool(description="Get the status of an order by order ID")
def get_order_status(order_id: str) -> str:
    """
    Fetch the current status of an order by order_id
    
    Args:
        order_id: The order ID to look up
        
    Returns:
        JSON string with order status, delivery estimate, and last update
    """
    order = find_order_by_id(order_id)
    if not order:
        return json.dumps({"error": f"Order {order_id} not found"})
    
    response = {
        "order_id": order['order_id'],
        "order_status": order['order_status'],
        "last_update_note": order['last_update_note'],
        "est_delivery": order['est_delivery']
    }
    return json.dumps(response, indent=2)


@mcp.tool(description="Get tracking information for an order")
def get_tracking_info(order_id: str) -> str:
    """
    Get tracking number and carrier details for an order
    
    Args:
        order_id: The order ID to track
        
    Returns:
        JSON string with tracking number, carrier, status, and estimated delivery
    """
    order = find_order_by_id(order_id)
    if not order:
        return json.dumps({"error": f"Order {order_id} not found"})
    
    response = {
        "order_id": order['order_id'],
        "tracking_number": order['tracking_number'],
        "carrier": order['carrier'],
        "status": order['order_status'],
        "est_delivery": order['est_delivery']
    }
    return json.dumps(response, indent=2)


@mcp.tool(description="Get items and pricing for an order")
def get_order_items(order_id: str) -> str:
    """
    Get items and pricing information for an order
    
    Args:
        order_id: The order ID
        
    Returns:
        JSON string with items, total amount, currency, and order date
    """
    order = find_order_by_id(order_id)
    if not order:
        return json.dumps({"error": f"Order {order_id} not found"})
    
    response = {
        "order_id": order['order_id'],
        "items": json.loads(order['items_json']),
        "total_amount": order['total_amount'],
        "currency": order['currency'],
        "order_date": order['order_date']
    }
    return json.dumps(response, indent=2)


@mcp.tool(description="Check if an order is eligible for return")
def check_return_eligibility(order_id: str) -> str:
    """
    Check if an order is eligible for return
    
    Args:
        order_id: The order ID to check
        
    Returns:
        JSON string with returnable status and eligibility message
    """
    order = find_order_by_id(order_id)
    if not order:
        return json.dumps({"error": f"Order {order_id} not found"})
    
    is_returnable = order['is_returnable'].upper() == 'TRUE'
    response = {
        "order_id": order['order_id'],
        "order_status": order['order_status'],
        "is_returnable": is_returnable,
        "message": "This order can be returned" if is_returnable else "This order cannot be returned",
        "items": json.loads(order['items_json'])
    }
    return json.dumps(response, indent=2)


@mcp.tool(description="Get complete order information")
def get_full_order_details(order_id: str) -> str:
    """
    Get complete order information including all details
    
    Args:
        order_id: The order ID
        
    Returns:
        JSON string with all order details
    """
    order = find_order_by_id(order_id)
    if not order:
        return json.dumps({"error": f"Order {order_id} not found"})
    
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


@mcp.tool(description="Get shipping address for an order")
def get_shipping_address(order_id: str) -> str:
    """
    Get shipping address for an order
    
    Args:
        order_id: The order ID
        
    Returns:
        JSON string with shipping address, carrier, and tracking number
    """
    order = find_order_by_id(order_id)
    if not order:
        return json.dumps({"error": f"Order {order_id} not found"})
    
    response = {
        "order_id": order['order_id'],
        "shipping_address": order['shipping_address'],
        "carrier": order['carrier'],
        "tracking_number": order['tracking_number']
    }
    return json.dumps(response, indent=2)

if __name__ == "__main__":
    mcp.run()
