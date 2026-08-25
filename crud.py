from database import get_db


# =========================================================
# CREATE
# =========================================================

def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """
    Add a new expense to the database.
    """

    with get_db() as db:

        cur = db.execute(
            """
            INSERT INTO expenses
            (date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                date,
                amount,
                category,
                subcategory,
                note
            )
        )

        expense_id = cur.lastrowid

        return {
            "id": expense_id,
            "date": date,
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "note": note
        }


# =========================================================
# READ ONE
# =========================================================

def get_expense(id: int):
    """
    Get one expense by ID.
    """

    with get_db() as db:

        cur = db.execute(
            """
            SELECT
                id,
                date,
                amount,
                category,
                subcategory,
                note
            FROM expenses
            WHERE id = ?
            """,
            (id,)
        )

        row = cur.fetchone()

        if row is None:
            return {
                "status": "error",
                "message": f"Expense with id {id} not found"
            }

        return dict(row)


# =========================================================
# READ MANY
# =========================================================

def list_expenses(
    start_date: str,
    end_date: str
):
    """
    List expenses within a date range.
    """

    with get_db() as db:

        cur = db.execute(
            """
            SELECT
                id,
                date,
                amount,
                category,
                subcategory,
                note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY date ASC, id ASC
            """,
            (
                start_date,
                end_date
            )
        )

        rows = cur.fetchall()

        return [
            dict(row)
            for row in rows
        ]


# =========================================================
# UPDATE
# =========================================================

def update_expense(
    id: int,
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """
    Update an existing expense.
    """

    with get_db() as db:

        # Check whether expense exists
        cur = db.execute(
            """
            SELECT id
            FROM expenses
            WHERE id = ?
            """,
            (id,)
        )

        if cur.fetchone() is None:
            return {
                "status": "error",
                "message": f"Expense with id {id} not found"
            }

        # Update
        db.execute(
            """
            UPDATE expenses
            SET
                date = ?,
                amount = ?,
                category = ?,
                subcategory = ?,
                note = ?
            WHERE id = ?
            """,
            (
                date,
                amount,
                category,
                subcategory,
                note,
                id
            )
        )

        return {
            "status": "updated",
            "id": id,
            "date": date,
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "note": note
        }


# =========================================================
# DELETE
# =========================================================

def delete_expense(id: int):
    """
    Delete an expense by ID.
    """

    with get_db() as db:

        # Check whether expense exists
        cur = db.execute(
            """
            SELECT *
            FROM expenses
            WHERE id = ?
            """,
            (id,)
        )

        row = cur.fetchone()

        if row is None:
            return {
                "status": "error",
                "message": f"Expense with id {id} not found"
            }

        db.execute(
            """
            DELETE FROM expenses
            WHERE id = ?
            """,
            (id,)
        )

        return {
            "status": "deleted",
            "id": id
        }