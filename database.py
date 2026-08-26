import os

from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set"
    )


pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=5,
    open=False,
    kwargs={
        "row_factory": dict_row
    }
)


async def init_db():

    await pool.open()

    # Wait until at least one connection is ready
    await pool.wait()

    print("PostgreSQL pool ready")

    async with pool.connection() as db:

        await db.execute(
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id SERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        date DATE NOT NULL,
        amount NUMERIC(12, 2) NOT NULL,
        category TEXT NOT NULL,
        subcategory TEXT DEFAULT '',
        note TEXT DEFAULT ''
    )
    """
)

        await db.commit()

    print("Expenses table ready")


async def close_db():

    await pool.close()

    print("Pool closed")