"""Entry point for running the MCP server.

Usage::

    # stdio transport (default — for local agent integration)
    python -m src.mcp_server

    # HTTP transport (for remote agents)
    python -m src.mcp_server --transport http --port 8090
"""

from __future__ import annotations

import argparse
import sys

from src.mcp_server.server import create_mcp_server


def main() -> None:
    """Parse CLI args and start the MCP server."""
    parser = argparse.ArgumentParser(
        description="Graph RAG MCP Server — agentic retrieval over knowledge graphs.",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode (default: stdio).",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the HTTP server to (default: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8090,
        help="Port for the HTTP transport (default: 8090).",
    )
    args = parser.parse_args()

    server = create_mcp_server()

    if args.transport == "stdio":
        server.run(transport="stdio")
    elif args.transport == "http":
        server.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        print(f"Unknown transport: {args.transport}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
