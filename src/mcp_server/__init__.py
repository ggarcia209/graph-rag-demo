"""MCP server layer for agentic RAG.

Exposes the retrieval pipeline as MCP tools so that AI agents
can query the knowledge graph and receive re-ranked results
directly — without the generation step.
"""

from src.mcp_server.server import create_mcp_server

__all__ = ["create_mcp_server"]
