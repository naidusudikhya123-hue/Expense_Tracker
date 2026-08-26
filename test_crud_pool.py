import asyncio

asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

from database import init_db, pool
from crud import add_expense, list_expenses


async def main():

    await init_db()

    print("\n--- ADD EXPENSE ---")

    result = await add_expense(
        date="2026-08-26",
        amount=399,
        category="Education",
        subcategory="Course",
        note="Krishnaik ML course"
    )

    print(result)

    print("\n--- LIST EXPENSES ---")

    expenses = await list_expenses(
        "2026-08-01",
        "2026-08-31"
    )

    for expense in expenses:
        print(expense)

    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())