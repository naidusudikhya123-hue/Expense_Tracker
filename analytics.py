from database import get_db

#summarize expenses

def summarize(start_date:str,end_date:str):
    """Return total spending and transaction count within a date range"""
    
    with get_db() as db:
        curr=db.execute(
            """
            select
                  coalesce(sum(amount),0) as total_expenses,
                  count(*) as transaction_count
            from expenses
            where date between ? and ?
            """,
            (start_date,end_date)
            
        )
        row=curr.fetchone()
        return{
            "start_date":start_date,
            "end_date":end_date,
            "total_expenses": row["total_expenses"],
            "transaction_count": row["transaction_count"]
            
        }
        
#spending by category
def spending_by_category(start_date:str,end_date:str):
    """Return total spending grouped by category."""
    with get_db() as db:
        curr=db.execute(
            """
            select
                  category,
                  sum(amount) as total_amount,
                  count(*) as transaction_count
            from expenses
            where date between ? and ?
            group by category
            order by total_amount desc
            """,
            (start_date,end_date)
            
        )
        rows=curr.fetchall()
        return [dict(row) for row in rows]

#daily summary
def daily_summary(start_date:str,end_date:str):
    """Return total spending grouped by date."""
    with get_db() as db:
        curr=db.execute(
            """
            select
                  category,
                  sum(amount) as total_amount,
                  count(*) as transaction_count
            from expenses
            where date between ? and ?
            group by date
            order by date asc
            """,
            (start_date,end_date)
            
        )
        rows=curr.fetchall()
        return [dict(row) for row in rows]


#monthly summary
def monthly_summary(year:str,month:str):
    """Return total spending and transaction count for a specific month."""
    
    # First day of the requested month
    start_date = f"{year:04d}-{month:02d}-01"
    
    #calculate next month
    if month==12:
        next_year=year+1
        next_month=1
    else:
        next_year=year
        next_month=month+1
    end_date=f"{next_year:04d}-{next_month:02d}-01"
    with get_db() as db:
        curr=db.execute(
            """
            select
                  coalesce(sum(amount),0) as total_expenses,
                  count(*) as transaction_count
            from expenses
            where date>=? and date<?
            """,
            (start_date,end_date)
            
        )
        row=curr.fetchone()
        return {
            "year": year,
            "month": month,
            "total_expenses": row["total_expenses"],
            "transaction_count": row["transaction_count"]
        }
    
    
#top expenses

def top_expenses(start_date:str,end_date:str,limit:int=5):
    """Return the largest expenses within a date range."""
    
    #prevent invalid limits
    if limit<1:
        limit=1
    if limit>100:
        limit=100
    
    with get_db() as db:
        curr=db.execute(
            """
            select
                  id,
                  date,
                  amount,
                  category,
                  subcategory,
                  note
            from expenses
            where date between ? and ?
            order by amount desc
            limit ?
            """,
            (start_date,end_date,limit)
            
        )
        rows=curr.fetchall()
        return[dict(row) for row in rows]
    


#  COMPARE TWO PERIODS

def compare_periods(
    first_start: str,
    first_end: str,
    second_start: str,
    second_end: str
):
    """
    Compare total spending between two date ranges.
    """

    with get_db() as db:

        # First period
        cur = db.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total,
                COUNT(*) AS transaction_count
            FROM expenses
            WHERE date BETWEEN ? AND ?
            """,
            (
                first_start,
                first_end
            )
        )

        first = cur.fetchone()

        # Second period
        cur = db.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total,
                COUNT(*) AS transaction_count
            FROM expenses
            WHERE date BETWEEN ? AND ?
            """,
            (
                second_start,
                second_end
            )
        )

        second = cur.fetchone()

        first_total = first["total"]
        second_total = second["total"]

        difference = second_total - first_total

        # Avoid division by zero
        if first_total != 0:
            percentage_change = (
                difference / first_total
            ) * 100
        else:
            percentage_change = None

        return {
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