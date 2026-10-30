"""
CORS for streamable HTTP MCP apps.

Browsers send an OPTIONS preflight for cross-origin POST/GET with custom headers.
The MCP streamable HTTP transport only implements GET, POST, DELETE and returns 405
for OPTIONS, so we must handle CORS before requests reach that app. Starlette's
CORSMiddleware answers preflight and adds response headers on the actual request.

Credentials + expose_headers match typical MCP Inspector needs so cross-origin
fetch can follow mcp-session-id and related headers on responses.
"""

from starlette.middleware.cors import CORSMiddleware


# Let browser JS read MCP response headers (session, protocol version, SSE resume).
_MCP_EXPOSE_HEADERS = (
    "mcp-session-id",
    "mcp-protocol-version",
    "last-event-id",
)


def add_cors_middleware(app):
    """Wrap an ASGI app with CORS suitable for MCP Inspector in a browser."""
    return CORSMiddleware(
        app,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=list(_MCP_EXPOSE_HEADERS),
    )
