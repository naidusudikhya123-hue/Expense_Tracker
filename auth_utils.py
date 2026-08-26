# from fastmcp import Context


# def get_current_user(ctx: Context) -> str:
#     """
#     Return the authenticated user's ID.
#     """

#     request = ctx.request_context.request

#     if request is None:
#         raise RuntimeError("No HTTP request available")

#     if not request.user.is_authenticated:
#         raise PermissionError("Authentication required")

#     access_token = request.user.access_token

#     if access_token is None:
#         raise PermissionError("No access token available")

#     user_id = access_token.subject

#     if not user_id:
#         raise PermissionError("Authenticated token has no subject")

#     return user_id


from fastmcp import Context


async def get_current_user(ctx: Context) -> str:
    user_id = await ctx.get_state("user_id")

    if not user_id:
        raise ValueError("Authenticated user ID not found")

    return user_id