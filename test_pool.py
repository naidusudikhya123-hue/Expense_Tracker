import asyncio

asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

from database import pool, init_db


async def main():

    print("Starting pool test...")

    await init_db()

    print()
    print("Pool max size:", pool.max_size)
    print("Pool min size:", pool.min_size)
    print("Available:", pool.get_stats()["pool_available"])

    async with pool.connection() as db:

        cur = await db.execute(
            "SELECT 1 AS test"
        )

        row = await cur.fetchone()

        print("Database result:", row)

    print()
    print("Available after query:", pool.get_stats()["pool_available"])

    await pool.close()

    print("Pool closed")


if __name__ == "__main__":
    asyncio.run(main())