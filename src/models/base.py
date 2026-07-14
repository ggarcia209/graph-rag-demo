"""Abstract base classes for all model types in the pipeline.

Each interface defines the contract that concrete model implementations
(e.g., llama.cpp, HuggingFace) must fulfill. Pipeline components depend
on these interfaces, not on concrete implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEmbeddingModel(ABC):
    """Interface for text embedding models.

    Implementations convert text into dense vector representations
    for semantic similarity search.
    """

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of text strings into vectors.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors, one per input text.
        """
        ...

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """Embed a single query string.

        Args:
            query: The query text to embed.

        Returns:
            A single embedding vector.
        """
        ...


class BaseVisionLanguageModel(ABC):
    """Interface for OCR / Vision-Language models.

    Implementations extract text or generate descriptions
    from images and document pages.
    """

    @abstractmethod
    def extract_text(self, image_path: str, prompt: str = "") -> str:
        """Extract text content from an image or document page.

        Args:
            image_path: Path to the image file.
            prompt: Optional prompt to guide extraction.

        Returns:
            Extracted text content.
        """
        ...

    @abstractmethod
    def describe_image(self, image_path: str, prompt: str = "") -> str:
        """Generate a natural-language description of an image.

        Args:
            image_path: Path to the image file.
            prompt: Optional prompt to guide description.

        Returns:
            Natural-language description of the image.
        """
        ...


class BaseReranker(ABC):
    """Interface for re-ranking models.

    Implementations re-score a set of candidate documents by their
    relevance to a query, improving precision after initial retrieval.
    """

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int = 10,
    ) -> list[tuple[int, float]]:
        """Re-rank documents by relevance to query.

        Args:
            query: The query text.
            documents: List of candidate document texts.
            top_k: Number of top results to return.

        Returns:
            List of (original_index, score) tuples sorted by score descending.
        """
        ...


class BaseGenerationModel(ABC):
    """Interface for text generation / chat models.

    Implementations generate natural-language responses from prompts
    or chat message histories.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a completion for the given prompt.

        Args:
            prompt: The input prompt text.

        Returns:
            Generated text response.
        """
        ...

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        """Generate a response for a chat message list.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.

        Returns:
            Generated text response.
        """
        ...
