import http.server
import threading
import webbrowser
import urllib.parse
import requests
import os
import jwt
from fastmcp.server.auth.providers.jwt import JWTVerifier

# =========================================================
# AUTH0 CONFIGURATION
# =========================================================

AUTH0_DOMAIN ="expense-tracker-mcp.us.auth0.com"

CLIENT_ID = "XHdscscc0xRNx2caDa9dL2318vCCfHGJ"

AUDIENCE = "https://expense-tracker-mcp"

REDIRECT_URI = "http://localhost:3000/callback"

CLIENT_SECRET="fFkbmSWEs5v_hZFYIpX1h7JPtsK6Z9r8_LgEZuSSsrMq7vGXQWfN4gjRcdX46mID"


SCOPES = (
    "openid profile email "
    "read:expenses "
    "write:expenses "
    "delete:expenses "
    "analytics:expenses"
)


# =========================================================
# CALLBACK SERVER
# =========================================================

authorization_code = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        global authorization_code

        parsed = urllib.parse.urlparse(self.path)

        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        query = urllib.parse.parse_qs(parsed.query)

        if "error" in query:
            error = query["error"][0]
            description = query.get(
                "error_description",
                ["No description"]
            )[0]

            print()
            print("Auth0 error:", error)
            print("Description:", description)

            self.send_response(400)
            self.end_headers()

            self.wfile.write(
                f"""
                <h2>Auth0 error: {error}</h2>
                <p>{description}</p>
                """.encode()
            )

            return
        authorization_code = query.get(
            "code",
            [None]
        )[0]

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html"
        )
        self.end_headers()

        self.wfile.write(
            b"""
            <html>
                <body>
                    <h2>Authentication successful.</h2>
                    <p>You can close this browser window.</p>
                </body>
            </html>
            """
        )

    def log_message(self, format, *args):
        pass


# =========================================================
# MAIN
# =========================================================

async def main():

    global authorization_code

    print("Starting OAuth test...")
    print()

    # -----------------------------------------------------
    # Start callback server
    # -----------------------------------------------------

    server = http.server.HTTPServer(
        ("localhost", 3000),
        CallbackHandler
    )

    thread = threading.Thread(
        target=server.handle_request
    )

    thread.start()

    # -----------------------------------------------------
    # Build Auth0 authorization URL
    # -----------------------------------------------------

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "audience": AUDIENCE,
        "scope": SCOPES,
    }

    authorization_url = (
        f"https://{AUTH0_DOMAIN}/authorize?"
        + urllib.parse.urlencode(params)
    )

    print("Opening Auth0 login...")
    print()

    webbrowser.open(
        authorization_url
    )

    # -----------------------------------------------------
    # Wait for callback
    # -----------------------------------------------------

    thread.join()

    server.server_close()

    if authorization_code is None:

        print()
        print("Authorization failed.")

        return

    print()
    print("Authorization code received.")
    print("Exchanging code for access token...")
    print()

    # -----------------------------------------------------
    # Exchange authorization code
    # -----------------------------------------------------

    token_url = (
        f"https://{AUTH0_DOMAIN}/oauth/token"
    )

    response = requests.post(
        token_url,
        json={
            "grant_type": "authorization_code",
            "client_secret":CLIENT_SECRET,
            "client_id": CLIENT_ID,
            "code": authorization_code,
            "redirect_uri": REDIRECT_URI,
        },
        timeout=30
    )

    print(
        "Token endpoint status:",
        response.status_code
    )

    if response.status_code != 200:

        print(response.text)

        return

    token_data = response.json()
    access_token = token_data["access_token"]
    print("access token",access_token)
# =========================================================
# TEST FASTMCP JWT VERIFICATION
# =========================================================

    verifier = JWTVerifier(
        jwks_uri="https://expense-tracker-mcp.us.auth0.com/.well-known/jwks.json",
        issuer="https://expense-tracker-mcp.us.auth0.com/",
        audience="https://expense-tracker-mcp",
        algorithm="RS256",
    )

    verified_token = await verifier.verify_token(access_token)
    print()
    print("FastMCP JWT verification:")
    print()

    if verified_token is None:
        print("❌ JWT verification FAILED")

    else:
        print("✅ JWT verification SUCCESSFUL")
        print()
        print("Subject:", verified_token.subject)
        print("Client ID:", verified_token.client_id)
        print("Scopes:", verified_token.scopes)
        print("Claims:")

        for key, value in verified_token.claims.items():
            print(f"  {key}: {value}")
    print()
    print("JWT claims:")
    print()

    claims = jwt.decode(
        access_token,
        options={
            "verify_signature": False
        }
    )

    for key, value in claims.items():
        print(f"{key}: {value}")

    print()
    print("Token received.")
    print()

    # -----------------------------------------------------
    # IMPORTANT
    # Don't print the actual access token.
    # -----------------------------------------------------

    print(
        "Token type:",
        token_data.get("token_type")
    )

    print(
        "Expires in:",
        token_data.get("expires_in")
    )

    print(
        "Scope returned:",
        token_data.get("scope")
    )

    print()

    print(
        "Access token received successfully."
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())