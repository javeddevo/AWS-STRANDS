from mcp.server import FastMCP

mcp = FastMCP("Calculator Server")

@mcp.tool(description="Add two numbers together")
def add(x: int, y: int) -> int:
    """Add two numbers and return the result."""
    return x + y

@mcp.tool(description="Subtract one number from another")
def subtract(x: int, y: int) -> int:
    """Subtract one number from another and return the result."""
    return x - y

@mcp.tool(description="Multiply two numbers")
def multiply(x: int, y: int) -> int:
    """Multiply two numbers and return the result."""
    return x * y

@mcp.tool(description="Divide one number by another")
def divide(x: int, y: int) -> float:
    """Divide one number by another and return the result."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

if __name__ == "__main__":
    mcp.run()

