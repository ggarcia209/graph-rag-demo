"""Model abstraction layer for the Graph RAG pipeline.

Provides abstract base classes for all model types and a registry
for instantiating concrete implementations by provider name.
"""

from src.models.base import (
    BaseEmbeddingModel,
    BaseGenerationModel,
    BaseReranker,
    BaseVisionLanguageModel,
)
from src.models.registry import ModelRegistry

__all__ = [
    "BaseEmbeddingModel",
    "BaseGenerationModel",
    "BaseReranker",
    "BaseVisionLanguageModel",
    "ModelRegistry",
]
