from fastmcp.server.auth.providers.jwt import JWTVerifier


auth0_verifier = JWTVerifier(
    jwks_uri="https://expense-tracker-mcp.us.auth0.com/.well-known/jwks.json",
    issuer="https://expense-tracker-mcp.us.auth0.com/",
    audience="https://expense-tracker-mcp",
    algorithm="RS256",
)