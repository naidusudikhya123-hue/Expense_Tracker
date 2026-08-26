from database import pool


# =========================================================
# TOTAL SUMMARY
# =========================================================

async def summarize(
    user_id: str,
    start_date: str,
    end_date: str
):
    """Return total spending and transaction count for one user."""

    async with pool.connection() as db:

        cur = await db.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total_expenses,
                COUNT(*) AS transaction_count
            FROM expenses
            WHERE user_id = %s
            AND date BETWEEN %s AND %s
            """,
            (
                user_id,
                start_date,
                end_date
            )
        )

        row = await cur.fetchone()

        return {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_expenses": float(row["total_expenses"]),
            "transaction_count": row["transaction_count"]
        }


# =========================================================
# SPENDING BY CATEGORY
# =========================================================

async def spending_by_category(
    user_id: str,
    start_date: str,
    end_date: str
):
    """Return spending grouped by category for one user."""

    async with pool.connection() as db:

        cur = await db.execute(
            """
            SELECT
                category,
                SUM(amount) AS total_amount,
                COUNT(*) AS transaction_count
            FROM expenses
            WHERE user_id = %s
            AND date BETWEEN %s AND %s
            GROUP BY category
            ORDER BY total_amount DESC
            """,
            (
                user_id,
                start_date,
                end_date
            )
        )

        rows = await cur.fetchall()

        return [
            {
                "category": row["category"],
                "total_amount": float(row["total_amount"]),
                "transaction_count": row["transaction_count"]
            }
            for row in rows
        ]


# =========================================================
# DAILY SUMMARY
# =========================================================

async def daily_summary(
    user_id: str,
    start_date: str,
    end_date: str
):
    """Return daily spending for one user."""

    async with pool.connection() as db:

        cur = await db.execute(
            """
            SELECT
                date,
                SUM(amount) AS total_amount,
                COUNT(*) AS transaction_count
            FROM expenses
            WHERE user_id = %s
            AND date BETWEEN %s AND %s
            GROUP BY date
            ORDER BY date ASC
            """,
            (
                user_id,
                start_date,
                end_date
            )
        )

        rows = await cur.fetchall()

        return [
            {
                "date": str(row["date"]),
                "total_amount": float(row["total_amount"]),
                "transaction_count": row["transaction_count"]
            }
            for row in rows
        ]


# =========================================================
# MONTHLY SUMMARY
# =========================================================

async def monthly_summary(
    user_id: str,
    year: int,
    month: int
):
    """Return monthly spending for one user."""

    if month < 1 or month > 12:
        return {
            "status": "error",
            "message": "Month must be between 1 and 12"
        }

    start_date = f"{year:04d}-{month:02d}-01"

    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    end_date = f"{next_year:04d}-{next_month:02d}-01"

    async with pool.connection() as db:

        cur = await db.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total_expenses,
                COUNT(*) AS transaction_count
            FROM expenses
            WHERE user_id = %s
            AND date >= %s
            AND date < %s
            """,
            (
                user_id,
                start_date,
                end_date
            )
        )

        row = await cur.fetchone()

        return {
            "user_id": user_id,
            "year": year,
            "month": month,
            "total_expenses": float(row["total_expenses"]),
            "transaction_count": row["transaction_count"]
        }


# =========================================================
# TOP EXPENSES
# =========================================================

async def top_expenses(
    user_id: str,
    start_date: str,
    end_date: str,
    limit: int = 5
):
    """Return largest expenses for one user."""

    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

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
            WHERE user_id = %s
            AND date BETWEEN %s AND %s
            ORDER BY amount DESC
            LIMIT %s
            """,
            (
                user_id,
                start_date,
                end_date,
                limit
            )
        )

        rows = await cur.fetchall()

        return [
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "date": str(row["date"]),
                "amount": float(row["amount"]),
                "category": row["category"],
                "subcategory": row["subcategory"],
                "note": row["note"]
            }
            for row in rows
        ]


# =========================================================
# COMPARE TWO PERIODS
# =========================================================

async def compare_periods(
    user_id: str,
    first_start: str,
    first_end: str,
    second_start: str,
    second_end: str
):
    """Compare spending between two periods for one user."""

    async with pool.connection() as db:

        # -------------------------------------------------
        # First period
        # -------------------------------------------------

        cur = await db.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total,
                COUNT(*) AS transaction_count
            FROM expenses
            WHERE user_id = %s
            AND date BETWEEN %s AND %s
            """,
            (
                user_id,
                first_start,
                first_end
            )
        )

        first = await cur.fetchone()

        # -------------------------------------------------
        # Second period
        # -------------------------------------------------

        cur = await db.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total,
                COUNT(*) AS transaction_count
            FROM expenses
            WHERE user_id = %s
            AND date BETWEEN %s AND %s
            """,
            (
                user_id,
                second_start,
                second_end
            )
        )

        second = await cur.fetchone()

        first_total = float(first["total"])
        second_total = float(second["total"])

        difference = second_total - first_total

        if first_total != 0:
            percentage_change = (
                difference / first_total
            ) * 100
        else:
            percentage_change = None

        return {
            "user_id": user_id,

            "first_period": {
                "start_date": first_start,
                "end_date": first_end,
                "total": first_total,
                "transactions": first["transaction_count"]
            },

            "second_period": {
                "start_date": second_start,
                "end_date": second_end,
                "total": second_total,
                "transactions": second["transaction_count"]
            },

            "difference": difference,
            "percentage_change": percentage_change
        }