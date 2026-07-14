"""Pydantic response models for MCP tool outputs.

These models define the structured data returned by MCP tools,
giving agents typed, predictable results to reason over.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class RetrievalResult(BaseModel):
    """A single retrieval result from the knowledge graph.

    Represents a node and its associated evidence text after
    hybrid retrieval (vector search + graph traversal) and re-ranking.
    """

    node_label: str = Field(description="The ontology node type label (e.g., 'Event', 'Company').")
    node_id: str = Field(description="The unique identifier of the node in the graph.")
    content: str = Field(description="The primary text content of the node.")
    evidence_text: str = Field(
        default="",
        description="Evidence text extracted from graph edges connecting this node.",
    )
    score: float = Field(
        default=0.0,
        description="Re-ranker relevance score (higher is more relevant).",
    )
    traversal_path: list[str] = Field(
        default_factory=list,
        description="The sequence of node labels traversed to reach this result.",
    )


class SchemaInfo(BaseModel):
    """Summary of a loaded ontology schema.

    Provides agents with enough information to understand the
    knowledge graph structure and formulate effective queries.
    """

    name: str = Field(description="Schema name identifier.")
    description: str = Field(default="", description="Human-readable schema description.")
    graph_name: str = Field(description="The FalkorDB graph name for this schema.")
    node_types: list[str] = Field(
        default_factory=list,
        description="Available node type labels in this ontology.",
    )
    edge_types: list[str] = Field(
        default_factory=list,
        description="Available edge/relationship type names.",
    )
    traversal_patterns: list[str] = Field(
        default_factory=list,
        description="Named traversal patterns available for graph queries.",
    )
