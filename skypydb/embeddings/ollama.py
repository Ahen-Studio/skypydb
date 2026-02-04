"""
Ollama embedding functions for vector operations.
"""

from typing import Optional
from skypydb.embeddings.mixins import (
    Utils,
    EmbeddingsFn,
    SysGet
)

class OllamaEmbedding(
    EmbeddingsFn,
    Utils,
    SysGet
):
    def __init__(
        self,
        model: str = "mxbai-embed-large",
        base_url: str = "http://localhost:11434",
        dimension: Optional[int] = None
    ):
        """
        Initialize Ollama embedding function.

        Args:
            model: Name of the Ollama embedding model to use
            base_url: Base URL for Ollama API (default: http://localhost:11434)
        """

        self.model = model
        self.base_url = base_url.rstrip("/")
        self._dimension: Optional[int] = None
