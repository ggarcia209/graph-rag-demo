"""Smoke tests verifying all package imports resolve correctly."""


def test_imports() -> None:
    from src.config import settings  # noqa: F401
    from src.generation.generator import ResponseGenerator  # noqa: F401
    from src.generation.prompts import graph_rag_prompt  # noqa: F401
    from src.graph.client import get_graph_client  # noqa: F401
    from src.graph.queries import EVENT_IMPACT_SUBGRAPH_QUERY  # noqa: F401
    from src.pipeline import GraphRAGPipeline  # noqa: F401
    from src.retrieval.hybrid_retriever import HybridRetriever  # noqa: F401


def test_schema_imports() -> None:
    from src.schema import (  # noqa: F401
        EdgeTypeDefinition,
        NodeTypeDefinition,
        OntologySchema,
        PropertyDefinition,
        TraversalPattern,
        load_schema,
    )


def test_models_imports() -> None:
    from src.models import (  # noqa: F401
        BaseEmbeddingModel,
        BaseGenerationModel,
        BaseReranker,
        BaseVisionLanguageModel,
        ModelRegistry,
    )


def test_ingestion_imports() -> None:
    from src.ingestion import BaseIngestor  # noqa: F401
