import asyncio

asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

from database import init_db, close_db, pool


async def database_task(name: str, seconds: int):

    print(f"{name} → requesting connection")

    async with pool.connection() as db:

        print(f"{name} → got connection")

        await asyncio.sleep(seconds)

        print(f"{name} → releasing connection")


async def main():

    print("Starting pool concurrency test...\n")

    await init_db()

    try:

        await asyncio.gather(
            database_task("TASK A", 3),
            database_task("TASK B", 3)
        )

    finally:

        await close_db()

    print("\nPool concurrency test finished")


if __name__ == "__main__":
    asyncio.run(main())