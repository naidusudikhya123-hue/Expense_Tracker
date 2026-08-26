from database import pool,init_db


# =========================================================
# CREATE
# =========================================================

async def add_expense(
    user_id: str,
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """Add a new expense to the database."""

    async with pool.connection() as db:

        cur = await db.execute(
            """
            INSERT INTO expenses
            (user_id,date, amount, category, subcategory, note)
            VALUES (%s,%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                user_id,
                date,
                amount,
                category,
                subcategory,
                note
            )
        )

        row = await cur.fetchone()

        await db.commit()

        return {
            "status": "created",
            "id": row["id"],
            "user_id":user_id,
            "date": date,
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "note": note
        }


# =========================================================
# READ ONE
# =========================================================

async def get_expense(user_id:str,id: int):
    """Get one expense belonging to the authenticated user."""

    async with pool.connection() as db:

        cur = await db.execute(
            """
            SELECT
                id,
                user_id,
                date,
                amount,
                category,
                subcategory,
                note
            FROM expenses
            WHERE id = %s
            and user_id=%s
            """,
            (id,user_id)
        )

        row = await cur.fetchone()

        if row is None:
            return {
                "status": "error",
                "message": f"Expense with id {id} not found"
            }

        return dict(row)


# =========================================================
# READ MANY
# =========================================================

async def list_expenses(
    user_id:str,
    start_date: str,
    end_date: str
):
    """List expenses within a date range."""

    async with pool.connection() as db:

        cur = await db.execute(
            """
            SELECT
                id,
                user_id,
                date,
                amount,
                category,
                subcategory,
                note
            FROM expenses
            where user_id=%s and
            date BETWEEN %s AND %s
            ORDER BY date ASC, id ASC
            """,
            (
                user_id,
                start_date,
                end_date
            )
        )

        rows = await cur.fetchall()

        return [
            dict(row)
            for row in rows
        ]


# =========================================================
# UPDATE
# =========================================================

async def update_expense(
    user_id:str,
    id: int,
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """Update an existing expense."""

    async with pool.connection() as db:

        cur = await db.execute(
            """
            UPDATE expenses
            SET
                date = %s,
                amount = %s,
                category = %s,
                subcategory = %s,
                note = %s
            WHERE id = %s and
            user_id=%s
            RETURNING id
            """,
            (
                date,
                amount,
                category,
                subcategory,
                note,
                id,
                user_id
            )
        )

        row = await cur.fetchone()

        if row is None:
            return {
                "status": "error",
                "message": f"Expense with id {id} not found"
            }

        await db.commit()

        return {
            "status": "updated",
            "id": id,
            "user_id":user_id,
            "date": date,
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "note": note
        }


# =========================================================
# DELETE
# =========================================================

async def delete_expense(user_id:str,id: int):
    """Delete an expense by ID."""

    async with pool.connection() as db:

        cur = await db.execute(
            """
            DELETE FROM expenses
            WHERE id = %s and
            user_id=%s
            RETURNING id
            """,
            (id,user_id)
        )

        row = await cur.fetchone()

        if row is None:
            return {
                "status": "error",
                "message": f"Expense with id {id} not found"
            }

        await db.commit()

        return {
            "status": "deleted",
            "id": id,
            "user_id":user_id
        }