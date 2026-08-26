from fastmcp.server.auth import AuthProvider, AccessToken


class DevAuthProvider(AuthProvider):

    async def verify_token(
        self,
        token: str
    ) -> AccessToken | None:

        users = {
            "token-user-a": {
                "user_id": "user-a",
                "scopes": [
                    "read:expenses",
                    "write:expenses",
                    "delete:expenses",
                    "analytics:expenses",
                ],
            },

            "token-user-b": {
                "user_id": "user-b",
                "scopes": [
                    "read:expenses",
                    "write:expenses",
                    "analytics:expenses",
                ],
            },
        }

        user = users.get(token)

        if user is None:
            return None

        user_id = user["user_id"]
        scopes = user["scopes"]

        return AccessToken(
            token=token,
            client_id="expense-tracker-client",
            scopes=scopes,
            subject=user_id,
            expires_at=None,
            claims={
                "sub": user_id
            }
        )