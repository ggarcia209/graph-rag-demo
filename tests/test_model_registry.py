"""Tests for the model abstraction layer — base classes and registry."""

from __future__ import annotations

import pytest

from src.models.base import (
    BaseEmbeddingModel,
    BaseGenerationModel,
    BaseReranker,
    BaseVisionLanguageModel,
)
from src.models.registry import ModelRegistry


# ---------------------------------------------------------------------------
# Concrete test doubles (minimal implementations for testing)
# ---------------------------------------------------------------------------


class StubEmbedding(BaseEmbeddingModel):
    """Minimal concrete embedding model for testing."""

    def __init__(self, base_url: str = "") -> None:
        self.base_url = base_url

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 3 for _ in texts]

    def embed_query(self, query: str) -> list[float]:
        return [0.0] * 3


class StubVLM(BaseVisionLanguageModel):
    """Minimal concrete VLM for testing."""

    def __init__(self, base_url: str = "") -> None:
        self.base_url = base_url

    def extract_text(self, image_path: str, prompt: str = "") -> str:
        return "extracted"

    def describe_image(self, image_path: str, prompt: str = "") -> str:
        return "described"


class StubReranker(BaseReranker):
    """Minimal concrete reranker for testing."""

    def __init__(self, base_url: str = "") -> None:
        self.base_url = base_url

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int = 10,
    ) -> list[tuple[int, float]]:
        return [(i, 1.0) for i in range(min(top_k, len(documents)))]


class StubGeneration(BaseGenerationModel):
    """Minimal concrete generation model for testing."""

    def __init__(self, base_url: str = "") -> None:
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        return "generated"

    def chat(self, messages: list[dict]) -> str:
        return "chatted"


class NotAModel:
    """A class that doesn't implement any model interface."""

    pass


# ---------------------------------------------------------------------------
# ABC enforcement tests
# ---------------------------------------------------------------------------


class TestAbstractInterfaces:
    """Verify that ABCs enforce method implementation."""

    def test_cannot_instantiate_base_embedding(self) -> None:
        with pytest.raises(TypeError):
            BaseEmbeddingModel()  # type: ignore[abstract]

    def test_cannot_instantiate_base_vlm(self) -> None:
        with pytest.raises(TypeError):
            BaseVisionLanguageModel()  # type: ignore[abstract]

    def test_cannot_instantiate_base_reranker(self) -> None:
        with pytest.raises(TypeError):
            BaseReranker()  # type: ignore[abstract]

    def test_cannot_instantiate_base_generation(self) -> None:
        with pytest.raises(TypeError):
            BaseGenerationModel()  # type: ignore[abstract]

    def test_stub_embedding_is_instance(self) -> None:
        model = StubEmbedding()
        assert isinstance(model, BaseEmbeddingModel)

    def test_stub_vlm_is_instance(self) -> None:
        model = StubVLM()
        assert isinstance(model, BaseVisionLanguageModel)

    def test_stub_reranker_is_instance(self) -> None:
        model = StubReranker()
        assert isinstance(model, BaseReranker)

    def test_stub_generation_is_instance(self) -> None:
        model = StubGeneration()
        assert isinstance(model, BaseGenerationModel)


# ---------------------------------------------------------------------------
# ModelRegistry tests
# ---------------------------------------------------------------------------


class TestModelRegistry:
    """Tests for ModelRegistry register/create lifecycle."""

    def setup_method(self) -> None:
        """Clear registry before each test."""
        ModelRegistry.clear()

    def teardown_method(self) -> None:
        """Clear registry after each test."""
        ModelRegistry.clear()

    # -- register + create round-trip --

    def test_register_and_create_embedding(self) -> None:
        ModelRegistry.register("embedding", "test", StubEmbedding)
        model = ModelRegistry.create("embedding", "test", base_url="http://localhost")
        assert isinstance(model, StubEmbedding)
        assert model.base_url == "http://localhost"

    def test_register_and_create_vlm(self) -> None:
        ModelRegistry.register("vlm", "test", StubVLM)
        model = ModelRegistry.create("vlm", "test")
        assert isinstance(model, StubVLM)

    def test_register_and_create_reranker(self) -> None:
        ModelRegistry.register("reranker", "test", StubReranker)
        model = ModelRegistry.create("reranker", "test")
        assert isinstance(model, StubReranker)

    def test_register_and_create_generation(self) -> None:
        ModelRegistry.register("generation", "test", StubGeneration)
        model = ModelRegistry.create("generation", "test")
        assert isinstance(model, StubGeneration)

    # -- error cases --

    def test_register_unknown_model_type(self) -> None:
        with pytest.raises(ValueError, match="unknown model_type"):
            ModelRegistry.register("unknown_type", "test", StubEmbedding)

    def test_register_wrong_base_class(self) -> None:
        with pytest.raises(ValueError, match="does not implement"):
            ModelRegistry.register("embedding", "test", StubGeneration)

    def test_register_non_model_class(self) -> None:
        with pytest.raises(ValueError, match="does not implement"):
            ModelRegistry.register("embedding", "test", NotAModel)

    def test_create_unregistered(self) -> None:
        with pytest.raises(ValueError, match="no implementation registered"):
            ModelRegistry.create("embedding", "nonexistent")

    # -- list + clear --

    def test_list_registered(self) -> None:
        ModelRegistry.register("embedding", "provider_a", StubEmbedding)
        ModelRegistry.register("vlm", "provider_b", StubVLM)
        registered = ModelRegistry.list_registered()
        assert ("embedding", "provider_a") in registered
        assert ("vlm", "provider_b") in registered
        assert len(registered) == 2

    def test_clear(self) -> None:
        ModelRegistry.register("embedding", "test", StubEmbedding)
        assert len(ModelRegistry.list_registered()) == 1
        ModelRegistry.clear()
        assert len(ModelRegistry.list_registered()) == 0

    # -- multiple providers for same model type --

    def test_multiple_providers_same_type(self) -> None:
        ModelRegistry.register("embedding", "provider_a", StubEmbedding)
        ModelRegistry.register("embedding", "provider_b", StubEmbedding)
        model_a = ModelRegistry.create("embedding", "provider_a", base_url="a")
        model_b = ModelRegistry.create("embedding", "provider_b", base_url="b")
        assert model_a.base_url == "a"
        assert model_b.base_url == "b"
