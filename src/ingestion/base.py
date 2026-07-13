"""Abstract base class for all ingestion pathways.

Concrete implementations (TextIngestor, DocumentIngestor) process
different input types but produce the same output: a list of node/edge
dicts conforming to the loaded OntologySchema.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.schema.models import OntologySchema


class BaseIngestor(ABC):
    """Interface for all ingestion pathways.

    Implementations process a data source and return structured
    node/edge dicts that are validated against the ontology schema
    before being written to the graph database.
    """

    @abstractmethod
    def ingest(self, source: str, schema: OntologySchema) -> list[dict]:
        """Process a source and return a list of node/edge dicts.

        Args:
            source: The data source — a raw text string, file path,
                or URI depending on the concrete implementation.
            schema: The loaded ontology schema that defines valid
                node types, edge types, and properties.

        Returns:
            A list of dicts, each representing a node or edge to
            be written to the graph. Structure TBD by implementation.
        """
        ...
