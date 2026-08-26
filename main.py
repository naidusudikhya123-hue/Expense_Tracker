import os
from contextlib import asynccontextmanager

from fastmcp import FastMCP, Context

from auth import DevAuthProvider
from auth_utils import get_current_user

from database import init_db, close_db
from crud import (
    add_expense,
    get_expense,
    list_expenses,
    update_expense,
    delete_expense
)

from analytics import (
    summarize,
    spending_by_category,
    daily_summary,
    monthly_summary,
    top_expenses,
    compare_periods
)

from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from fastmcp.server.middleware.error_handling import RetryMiddleware
from middleware.user_audit import AuditMiddleware
from fastmcp.server.auth import require_scopes

from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier

auth0_verifier = JWTVerifier(
    jwks_uri="https://expense-tracker-mcp.us.auth0.com/.well-known/jwks.json",
    issuer="https://expense-tracker-mcp.us.auth0.com/",
    audience="https://expense-tracker-mcp",
    algorithm="RS256",
)
auth_provider = RemoteAuthProvider(
    token_verifier=auth0_verifier,
    authorization_servers=[
        "https://expense-tracker-mcp.us.auth0.com/"
    ],
    base_url="http://localhost:8000",
    scopes_supported=[
        "read:expenses",
        "write:expenses",
        "delete:expenses",
        "analytics:expenses",
    ],
    resource_name="Expense Tracker MCP",
)

# =========================================================
# SERVER LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(server):
    """
    Manage the PostgreSQL connection pool
    for the lifetime of the MCP server.
    """

    print("Starting Expense Tracker...", flush=True)

    await init_db()

    print("PostgreSQL pool ready", flush=True)
    print("Expense Tracker started", flush=True)

    try:
        yield

    finally:
        print("Shutting down Expense Tracker...", flush=True)

        await close_db()

        print("PostgreSQL pool closed", flush=True)


# =========================================================
# MCP SERVER
# =========================================================

mcp = FastMCP(
    "ExpenseTracker",

    auth=auth_provider,

    lifespan=lifespan,
    
)


mcp.add_middleware(
    ErrorHandlingMiddleware(
        include_traceback=True,
        transform_errors=True,
    )
)
mcp.add_middleware(
    RetryMiddleware(
        max_retries=3,
        retry_exceptions=(ConnectionError,TimeoutError)
    )
)
mcp.add_middleware(
    TimingMiddleware()
)
mcp.add_middleware(
    AuditMiddleware()
)
mcp.add_middleware(
    LoggingMiddleware(
        include_payloads=True,
        max_payload_length=1000
    )
)

# =========================================================
# DEBUG / AUTHENTICATION
# =========================================================

@mcp.tool
async def debug_context(ctx: Context):
    """
    Inspect authenticated user information.
    """

    request = ctx.request_context.request

    if request is None:
        return {
            "error": "No HTTP request"
        }

    user = request.user

    return {
        "authenticated": user.is_authenticated,

        "user_type": type(user).__name__,

        "user_attributes": {
            key: str(value)
            for key, value in vars(user).items()
            if key != "token"
        },

        "auth_attributes": {
            key: str(value)
            for key, value in vars(request.auth).items()
            if key != "token"
        }
    }


@mcp.tool(auth=require_scopes("read:expenses"))
async def get_current_user_id(ctx: Context):
    """
    Return the authenticated user's ID.
    """

    user_id = await get_current_user(ctx)

    return {
        "authenticated": True,
        "user_id": user_id
    }


# =========================================================
# CREATE
# =========================================================
@mcp.tool(auth=require_scopes("write:expenses"))
async def create_expense(
    date: str,
    amount: float,
    category: str,
    ctx: Context,
    subcategory: str = "",
    note: str = "",
    
):
    """
    Create an expense for the authenticated user.
    """

    user_id = await get_current_user(ctx)

    return await add_expense(
        user_id,
        date,
        amount,
        category,
        subcategory,
        note
    )


# =========================================================
# READ ONE
# =========================================================

@mcp.tool(auth=require_scopes("read:expenses"))
async def get_expense_by_id(
    id: int,
    ctx: Context
):
    """
    Get an expense belonging to the authenticated user.
    """

    user_id = await get_current_user(ctx)

    return await get_expense(
        user_id,
        id
    )


# =========================================================
# READ MANY
# =========================================================

@mcp.tool(auth=require_scopes("read:expenses"))
async def get_expenses(
    start_date: str,
    end_date: str,
    ctx: Context
):
    """
    Get expenses belonging to the authenticated user
    within a date range.
    """

    user_id = await get_current_user(ctx)

    return await list_expenses(
        user_id,
        start_date,
        end_date
    )


# =========================================================
# UPDATE
# =========================================================

@mcp.tool(auth=require_scopes("write:expenses"))
async def edit_expense(
    id: int,
    date: str,
    amount: float,
    category: str,
    ctx: Context,
    subcategory: str = "",
    note: str = "",
    
):
    """
    Update an expense belonging to the authenticated user.
    """

    user_id = await get_current_user(ctx)

    return await update_expense(
        id,
        user_id,
        date,
        amount,
        category,
        subcategory,
        note
    )


# =========================================================
# DELETE
# =========================================================

@mcp.tool(auth=require_scopes("delete:expenses"))
async def remove_expense(
    id: int,
    ctx: Context
):
    """
    Delete an expense belonging to the authenticated user.
    """

    user_id = await get_current_user(ctx)

    return await delete_expense(
        user_id,
        id
    )


# =========================================================
# ANALYTICS
# =========================================================

@mcp.tool(auth=require_scopes("analytics:expenses"))
async def get_expense_summary(
    start_date: str,
    end_date: str,
    ctx: Context
):
    """
    Get total spending and transaction count
    for the authenticated user.
    """

    user_id = await get_current_user(ctx)

    return await summarize(
        user_id,
        start_date,
        end_date
    )


@mcp.tool(auth=require_scopes("analytics:expenses"))
async def get_spending_by_category(
    start_date: str,
    end_date: str,
    ctx: Context
):
    """
    Get spending grouped by category
    for the authenticated user.
    """

    user_id = await get_current_user(ctx)

    return await spending_by_category(
        user_id,
        start_date,
        end_date
    )


@mcp.tool(auth=require_scopes("analytics:expenses"))
async def get_daily_summary(
    start_date: str,
    end_date: str,
    ctx: Context
):
    """
    Get daily spending summary
    for the authenticated user.
    """

    user_id = await get_current_user(ctx)

    return await daily_summary(
        user_id,
        start_date,
        end_date
    )


@mcp.tool(auth=require_scopes("analytics:expenses"))
async def get_monthly_summary(
    year: int,
    month: int,
    ctx: Context
):
    """
    Get monthly spending summary
    for the authenticated user.
    """

    user_id = await get_current_user(ctx)

    return await monthly_summary(
        user_id,
        year,
        month
    )


@mcp.tool(auth=require_scopes("analytics:expenses"))
async def get_top_expenses(
    start_date: str,
    end_date: str,
    ctx: Context,
    limit: int = 5,
    
):
    """
    Get the largest expenses
    belonging to the authenticated user.
    """

    user_id = await get_current_user(ctx)

    return await top_expenses(
        user_id,
        start_date,
        end_date,
        limit
    )


@mcp.tool(auth=require_scopes("analytics:expenses"))
async def compare_expense_periods(
    first_start: str,
    first_end: str,
    second_start: str,
    second_end: str,
    ctx: Context
):
    """
    Compare spending between two periods
    for the authenticated user.
    """

    user_id = await get_current_user(ctx)

    return await compare_periods(
        user_id,
        first_start,
        first_end,
        second_start,
        second_end
    )


# =========================================================
# RESOURCE
# =========================================================

CATEGORIES_PATH = os.path.join(
    os.path.dirname(__file__),
    "categories.json"
)


@mcp.resource(
    "expense://categories",
    mime_type="application/json"
)
def categories():
    """
    Return available expense categories.
    """

    with open(
        CATEGORIES_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()