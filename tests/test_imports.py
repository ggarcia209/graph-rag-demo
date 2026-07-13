def test_imports():
    from src.config import settings
    from src.graph.client import get_graph_client
    from src.graph.queries import EVENT_IMPACT_SUBGRAPH_QUERY
    from src.retrieval.hybrid_retriever import HybridRetriever
    from src.generation.prompts import graph_rag_prompt
    from src.generation.generator import ResponseGenerator
    from src.pipeline import GraphRAGPipeline
    assert True


def test_schema_imports():
    from src.schema import (
        OntologySchema,
        NodeTypeDefinition,
        EdgeTypeDefinition,
        PropertyDefinition,
        TraversalPattern,
        load_schema,
    )
    assert True


def test_models_imports():
    from src.models import (
        BaseEmbeddingModel,
        BaseVisionLanguageModel,
        BaseReranker,
        BaseGenerationModel,
        ModelRegistry,
    )
    assert True


def test_ingestion_imports():
    from src.ingestion import BaseIngestor
    assert True

