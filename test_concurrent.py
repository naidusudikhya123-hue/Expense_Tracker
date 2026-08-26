import asyncio

import asyncio

asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)
from database import init_db, close_db
from crud import add_expense, list_expenses


async def user_a():
    print("🟢 USER A → adding expense")

    result = await add_expense(
        "user-a",
        "2026-08-26",
        250,
        "Food",
        "Lunch",
        "Concurrent test"
    )

    print("🟢 USER A → finished")
    print(result)


async def user_b():
    print("🔵 USER B → getting expenses")

    result = await list_expenses(
        "user-b",
        "2026-08-01",
        "2026-08-31"
    )

    print("🔵 USER B → finished")
    print(result)


async def main():

    print("Starting concurrent test...\n")

    await init_db()

    try:
        await asyncio.gather(
            user_a(),
            user_b()
        )

    finally:
        await close_db()

    print("\nConcurrent test finished")


if __name__ == "__main__":

    asyncio.run(main())