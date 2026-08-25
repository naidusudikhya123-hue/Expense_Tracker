from fastmcp import FastMCP
import os
from crud import (add_expense,get_expense,list_expenses,update_expense,delete_expense
)

from analytics import(
    summarize,
    daily_summary,
    monthly_summary,
    spending_by_category,
    top_expenses,
    compare_periods
)

mcp = FastMCP("ExpenseTracker")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")


@mcp.tool
def add_expense_tool(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
):
    """
    Add a new expense.
    """
    return add_expense(
        date,
        amount,
        category,
        subcategory,
        note
    )


@mcp.tool
def get_expense_tool(id: int):
    """
    Get an expense by ID.
    """
    return get_expense(id)


@mcp.tool
def list_expenses_tool(
    start_date: str,
    end_date: str
):
    """
    List expenses between two dates.
    """
    return list_expenses(
        start_date,
        end_date
    )


@mcp.tool
def update_expense_tool(
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
    return update_expense(
        id,
        date,
        amount,
        category,
        subcategory,
        note
    )


@mcp.tool
def delete_expense_tool(id: int):
    """
    Delete an expense.
    """
    return delete_expense(id)

@mcp.tool
def summarize_expenses(start_date:str,end_date:str):
     """Summarize total expenses within a date range."""
     return summarize(start_date,end_date)

@mcp.tool
def get_spending_by_category(start_date: str, end_date: str):
    """Get spending grouped by category."""
    return spending_by_category(start_date, end_date)


@mcp.tool
def get_daily_summary(start_date: str, end_date: str):
    """Get daily spending summary."""
    return daily_summary(start_date, end_date)

@mcp.tool
def get_monthly_summary(year: int, month: int):
    """Get spending summary for a month."""
    return monthly_summary(year, month)

@mcp.tool
def get_top_expenses(
    start_date: str,
    end_date: str,
    limit: int = 5
):
    """Get the largest expenses."""
    return top_expenses(start_date, end_date, limit)


@mcp.tool
def compare_expense_periods(
    first_start: str,
    first_end: str,
    second_start: str,
    second_end: str
):
    """Compare spending between two periods."""
    return compare_periods(
        first_start,
        first_end,
        second_start,
        second_end
    )
    
    
@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8000)