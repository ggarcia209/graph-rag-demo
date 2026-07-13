"""Model registry for instantiating concrete model implementations.

The registry maps (model_type, provider) tuples to concrete classes,
enabling configuration-driven model selection at startup.
"""

from __future__ import annotations

from typing import Any, Type

from src.models.base import (
    BaseEmbeddingModel,
    BaseGenerationModel,
    BaseReranker,
    BaseVisionLanguageModel,
)

# Map model type names to their abstract base class for validation.
_MODEL_TYPE_MAP: dict[str, Type] = {
    "embedding": BaseEmbeddingModel,
    "vlm": BaseVisionLanguageModel,
    "reranker": BaseReranker,
    "generation": BaseGenerationModel,
}


class ModelRegistry:
    """Factory registry that maps (model_type, provider) to concrete classes.

    Usage::

        ModelRegistry.register("embedding", "llama_cpp", LlamaCppEmbeddingModel)
        model = ModelRegistry.create("embedding", "llama_cpp", base_url="http://localhost:8081/v1")
    """

    _registry: dict[tuple[str, str], Type] = {}

    @classmethod
    def register(cls, model_type: str, provider: str, model_cls: Type) -> None:
        """Register a concrete model class for a (model_type, provider) pair.

        Args:
            model_type: One of 'embedding', 'vlm', 'reranker', 'generation'.
            provider: Provider identifier (e.g., 'llama_cpp', 'hf_cross_encoder').
            model_cls: The concrete class to register.

        Raises:
            ValueError: If model_type is unknown or model_cls doesn't implement
                the expected base class.
        """
        if model_type not in _MODEL_TYPE_MAP:
            raise ValueError(
                f"ModelRegistry.register: unknown model_type '{model_type}'. "
                f"Must be one of {list(_MODEL_TYPE_MAP.keys())}"
            )

        expected_base = _MODEL_TYPE_MAP[model_type]
        if not issubclass(model_cls, expected_base):
            raise ValueError(
                f"ModelRegistry.register: {model_cls.__name__} does not implement "
                f"{expected_base.__name__}"
            )

        cls._registry[(model_type, provider)] = model_cls

    @classmethod
    def create(cls, model_type: str, provider: str, **kwargs: Any) -> Any:
        """Instantiate a registered model.

        Args:
            model_type: One of 'embedding', 'vlm', 'reranker', 'generation'.
            provider: Provider identifier (e.g., 'llama_cpp').
            **kwargs: Arguments forwarded to the model constructor.

        Returns:
            An instance of the registered concrete model class.

        Raises:
            ValueError: If no class is registered for the given (model_type, provider).
        """
        key = (model_type, provider)
        if key not in cls._registry:
            raise ValueError(
                f"ModelRegistry.create: no implementation registered for "
                f"model_type='{model_type}', provider='{provider}'"
            )

        model_cls = cls._registry[key]
        return model_cls(**kwargs)

    @classmethod
    def list_registered(cls) -> list[tuple[str, str]]:
        """Return all registered (model_type, provider) pairs."""
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        """Remove all registrations. Primarily for testing."""
        cls._registry.clear()
