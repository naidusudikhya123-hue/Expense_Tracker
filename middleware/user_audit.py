from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_access_token


class AuditMiddleware(Middleware):

    async def on_call_tool(
        self,
        context: MiddlewareContext,
        call_next,
    ):
        ctx = context.fastmcp_context

        if ctx is None:
            raise RuntimeError(
                "FastMCP context is not available"
            )

        # -----------------------------------------
        # Get verified FastMCP access token
        # -----------------------------------------

        auth = get_access_token()

        if auth is None:
            raise PermissionError(
                "Authentication required"
            )

        # -----------------------------------------
        # Get authenticated user ID
        # -----------------------------------------

        user_id = auth.subject

        # FastMCP's JWTVerifier version you're using
        # may not populate subject, so fall back
        # to the verified JWT claims.
        if not user_id and auth.claims:
            user_id = auth.claims.get("sub")

        if not user_id:
            raise PermissionError(
                "Authenticated token has no subject"
            )

        # -----------------------------------------
        # Store user ID in FastMCP state
        # -----------------------------------------

        await ctx.set_state(
            "user_id",
            user_id,
        )

        # -----------------------------------------
        # Audit
        # -----------------------------------------

        tool_name = context.message.name

        print(
            f"[AUDIT] user={user_id} "
            f"tool={tool_name}",
            flush=True,
        )

        return await call_next(context)