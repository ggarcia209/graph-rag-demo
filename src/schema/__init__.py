"""Ontology schema layer for the Graph RAG pipeline.

Provides Pydantic models and YAML loading for interchangeable
knowledge graph ontology definitions.
"""

from src.schema.loader import load_schema
from src.schema.models import (
    EdgeTypeDefinition,
    NodeTypeDefinition,
    OntologySchema,
    PropertyDefinition,
    TraversalPattern,
)

__all__ = [
    "EdgeTypeDefinition",
    "NodeTypeDefinition",
    "OntologySchema",
    "PropertyDefinition",
    "TraversalPattern",
    "load_schema",
]
