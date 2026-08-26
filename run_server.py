import asyncio

# Must happen before FastMCP/Psycopg async starts
asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

from main import mcp


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)