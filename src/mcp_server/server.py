"""MCP server for agentic RAG.

Exposes the RAG pipeline's retrieval layer as MCP tools.
Agents query the knowledge graph and receive re-ranked results
directly — the generation step is intentionally skipped so
the agent's own LLM can synthesize answers from structured evidence.

Supports both ``stdio`` and ``http`` transports.
"""

from __future__ import annotations

import glob
import os
from typing import TYPE_CHECKING

from fastmcp import FastMCP

from src.mcp_server.models import RetrievalResult, SchemaInfo
from src.schema.loader import load_schema

if TYPE_CHECKING:
    from src.schema.models import OntologySchema

# Default directory for ontology YAML files.
_SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "schemas")


def _resolve_schemas_dir() -> str:
    """Return the absolute path to the schemas directory.

    Respects the ``SCHEMAS_DIR`` environment variable if set,
    otherwise falls back to the repository-level ``schemas/`` directory.
    """
    return os.path.abspath(os.environ.get("SCHEMAS_DIR", _SCHEMAS_DIR))


def _list_schema_files(schemas_dir: str) -> list[str]:
    """Return sorted basenames (without extension) of YAML files in *schemas_dir*."""
    pattern = os.path.join(schemas_dir, "*.yaml")
    return sorted(
        os.path.splitext(os.path.basename(f))[0] for f in glob.glob(pattern)
    )


def _load_schema_by_name(name: str, schemas_dir: str) -> OntologySchema:
    """Load and validate an ontology schema by its basename (no extension)."""
    path = os.path.join(schemas_dir, f"{name}.yaml")
    return load_schema(path)


def create_mcp_server(name: str = "graph-rag") -> FastMCP:
    """Create and return a configured :class:`FastMCP` server.

    The server registers three tools:

    * ``retrieve`` — hybrid retrieval (embed → vector search → graph
      traversal → re-rank) returning structured results.  The
      generation step is **skipped**.
    * ``list_schemas`` — enumerate available ontology schemas.
    * ``get_schema_info`` — return node types, edge types, and traversal
      patterns for a given schema.

    Args:
        name: Human-readable server name shown in MCP discovery.

    Returns:
        A configured :class:`FastMCP` instance ready to be started
        via ``.run()``.
    """
    mcp = FastMCP(name)

    # ------------------------------------------------------------------
    # Tool: retrieve
    # ------------------------------------------------------------------
    @mcp.tool()
    def retrieve(
        query: str,
        schema_name: str,
        top_k: int = 10,
    ) -> list[RetrievalResult]:
        """Query the knowledge graph and return re-ranked retrieval results.

        Executes the full hybrid retrieval pipeline:
        1. Embed the query
        2. Vector similarity search for entry nodes
        3. Graph traversal from entry nodes (BFS/DFS, N hops)
        4. Re-rank evidence by relevance

        The generation step is intentionally skipped — the agent
        receives structured evidence to synthesize its own response.

        Args:
            query: The natural-language search query.
            schema_name: Name of the ontology schema to use (without .yaml extension).
            top_k: Maximum number of results to return (default 10).

        Returns:
            A list of RetrievalResult objects with node info,
            evidence text, and relevance scores.
        """
        schemas_dir = _resolve_schemas_dir()

        # Validate schema exists.
        _load_schema_by_name(schema_name, schemas_dir)

        # TODO: Wire up HybridRetriever once concrete model
        # implementations are available.  For now, return an
        # empty list to satisfy the tool contract.
        _ = query
        _ = top_k
        return []

    # ------------------------------------------------------------------
    # Tool: list_schemas
    # ------------------------------------------------------------------
    @mcp.tool()
    def list_schemas() -> list[str]:
        """List available ontology schemas.

        Scans the schemas directory for YAML files and returns
        their names (without the .yaml extension).  Agents can
        use these names with ``retrieve`` and ``get_schema_info``.

        Returns:
            A list of schema name strings.
        """
        schemas_dir = _resolve_schemas_dir()
        return _list_schema_files(schemas_dir)

    # ------------------------------------------------------------------
    # Tool: get_schema_info
    # ------------------------------------------------------------------
    @mcp.tool()
    def get_schema_info(schema_name: str) -> SchemaInfo:
        """Get structural information about an ontology schema.

        Returns the node types, edge types, and traversal patterns
        defined in the schema.  Agents can use this to understand
        the knowledge graph structure before querying.

        Args:
            schema_name: Name of the schema (without .yaml extension).

        Returns:
            A SchemaInfo object describing the ontology.
        """
        schemas_dir = _resolve_schemas_dir()
        schema = _load_schema_by_name(schema_name, schemas_dir)
        return SchemaInfo(
            name=schema.name,
            description=schema.description,
            graph_name=schema.graph_name,
            node_types=list(schema.node_types.keys()) if schema.node_types else [],
            edge_types=list(schema.edge_types.keys()) if schema.edge_types else [],
            traversal_patterns=(
                list(schema.traversal_patterns.keys()) if schema.traversal_patterns else []
            ),
        )

    return mcp
