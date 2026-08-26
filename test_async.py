import asyncio
import os

# Windows + Psycopg async
asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

import psycopg


async def main():

    print("Connecting asynchronously...")

    conn = await psycopg.AsyncConnection.connect(
        os.environ["DATABASE_URL"]
    )

    print("✅ Async PostgreSQL connection OK")

    cur = await conn.execute(
        "SELECT 1 AS test"
    )

    row = await cur.fetchone()

    print("Result:", row)

    await conn.close()

    print("Connection closed")


if __name__ == "__main__":
    asyncio.run(main())