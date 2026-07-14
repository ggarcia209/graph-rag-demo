"""Ingestion layer for the Graph RAG pipeline.

Provides the abstract ingestion interface and concrete implementations
for raw text and document ingestion pathways.
"""

from src.ingestion.base import BaseIngestor

__all__ = [
    "BaseIngestor",
]
