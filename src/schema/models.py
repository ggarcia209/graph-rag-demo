"""Pydantic models representing a knowledge graph ontology schema.

These models are the core data structures that make the pipeline
schema-agnostic. An OntologySchema instance is loaded from a YAML
file at startup and injected into all downstream components.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PropertyDefinition(BaseModel):
    """Definition of a single property on a node or edge type."""

    type: str = Field(
        ...,
        description="Data type of the property (e.g., 'string', 'float', 'int', 'enum', 'datetime', '[]string', '[]float').",
    )
    required: bool = Field(
        default=False,
        description="Whether this property is required on every instance.",
    )
    embeddable: bool = Field(
        default=False,
        description="Whether this property should be used to generate vector embeddings.",
    )
    description: str = Field(
        default="",
        description="Human-readable description of the property.",
    )
    values: list[str] = Field(
        default_factory=list,
        description="Allowed values for enum-type properties.",
    )


class NodeTypeDefinition(BaseModel):
    """Definition of a node type (entity) in the ontology."""

    properties: dict[str, PropertyDefinition] = Field(
        default_factory=dict,
        description="Map of property name to its definition.",
    )
    description: str = Field(
        default="",
        description="Human-readable description of this node type.",
    )

    def embeddable_fields(self) -> list[str]:
        """Return property names marked as embeddable."""
        return [name for name, prop in self.properties.items() if prop.embeddable]

    def required_fields(self) -> list[str]:
        """Return property names marked as required."""
        return [name for name, prop in self.properties.items() if prop.required]


class EdgeTypeDefinition(BaseModel):
    """Definition of an edge type (relationship) in the ontology."""

    source: str = Field(
        ...,
        description="Source node type label.",
    )
    target: str = Field(
        ...,
        description="Target node type label.",
    )
    properties: dict[str, PropertyDefinition] = Field(
        default_factory=dict,
        description="Map of property name to its definition.",
    )
    description: str = Field(
        default="",
        description="Human-readable description of this edge type.",
    )


class TraversalPattern(BaseModel):
    """A named Cypher traversal pattern for common multi-hop queries."""

    description: str = Field(
        default="",
        description="Human-readable description of what this traversal does.",
    )
    pattern: str = Field(
        ...,
        description="Cypher pattern string (e.g., '(a:Event)-[:CAUSES]->(b:Event)').",
    )


class OntologySchema(BaseModel):
    """Top-level ontology schema for a knowledge graph domain.

    Loaded from a YAML file and injected into all pipeline components
    to drive schema-aware behavior at runtime.
    """

    name: str = Field(
        ...,
        description="Unique name for this ontology (e.g., 'gdelt_markets').",
    )
    version: str = Field(
        default="1.0",
        description="Schema version string.",
    )
    description: str = Field(
        default="",
        description="Human-readable description of the knowledge domain.",
    )
    graph_name: str = Field(
        ...,
        description="FalkorDB graph name to use for this ontology.",
    )
    node_types: dict[str, NodeTypeDefinition] = Field(
        default_factory=dict,
        description="Map of node type label to its definition.",
    )
    edge_types: dict[str, EdgeTypeDefinition] = Field(
        default_factory=dict,
        description="Map of edge type name to its definition.",
    )
    traversal_patterns: dict[str, TraversalPattern] = Field(
        default_factory=dict,
        description="Map of pattern name to its Cypher pattern definition.",
    )

    def get_embeddable_node_types(self) -> dict[str, list[str]]:
        """Return a mapping of node type label -> list of embeddable field names.

        Only includes node types that have at least one embeddable field.
        """
        result: dict[str, list[str]] = {}
        for label, node_type in self.node_types.items():
            fields = node_type.embeddable_fields()
            if fields:
                result[label] = fields
        return result

    def validate_node_label(self, label: str) -> bool:
        """Check if a node label is defined in this schema."""
        return label in self.node_types

    def validate_edge_type(self, edge_type: str) -> bool:
        """Check if an edge type is defined in this schema."""
        return edge_type in self.edge_types
