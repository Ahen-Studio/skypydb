"""
Module containing Ollama embedding retrieval helpers and embedding factory.
"""

from typing import (
    Any,
    List,
    Callable,
    Optional
)

def _validate_remaining_config(
    provider: str,
    config: dict
) -> None:

    if config:
        unsupported_keys = ", ".join(sorted(config.keys()))
        raise ValueError(
            f"Unsupported embedding config keys for provider '{provider}': {unsupported_keys}"
        )

def get_embedding_function(
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    provider: str = "ollama",
    **config: Any
) -> Callable[[List[str]], List[List[float]]]:
    """
    Get an embedding function from supported providers.

    This is a convenience function that returns a callable
    embedding function for use with the vector database.

    Args:
        model: Model name. Backward-compatible with legacy Ollama usage.
        base_url: Base URL. Backward-compatible with legacy Ollama usage.
        provider: Embedding provider (ollama, openai, sentence-transformers)
        **config: Provider-specific configuration

    Returns:
        Callable that takes a list of texts and returns embeddings

    Example:
        embed_fn = get_embedding_function(
            provider="ollama",
            model="mxbai-embed-large"
        )
        embeddings = embed_fn(["Hello world", "How are you?"])
    """

    provider = provider.lower().strip().replace("_", "-")
    if provider == "ollama":
        from skypydb.embeddings.ollama import OllamaEmbedding

        model = config.pop(
            "model",
            config.pop("embedding_model", model or "mxbai-embed-large")
        )
        base_url = config.pop(
            "base_url",
            config.pop("ollama_base_url", base_url or "http://localhost:11434")
        )
        dimension = config.pop("dimension", None)
        _validate_remaining_config(provider, config)
        return OllamaEmbedding(model=model, base_url=base_url, dimension=dimension)
    if provider == "openai":
        from skypydb.embeddings.openai import OpenAIEmbedding

        api_key = config.pop("api_key", None)
        model = config.pop("model", model or "text-embedding-3-small")
        base_url = config.pop("base_url", base_url)
        organization = config.pop("organization", None)
        project = config.pop("project", None)
        timeout = config.pop("timeout", None)
        dimension = config.pop("dimension", None)
        _validate_remaining_config(provider, config)
        return OpenAIEmbedding(
            api_key=api_key,
            model=model,
            base_url=base_url,
            organization=organization,
            project=project,
            timeout=timeout,
            dimension=dimension
        )
    if provider in {"sentence-transformers", "sentence-transformer"}:
        from skypydb.embeddings.sentence_transformers import SentenceTransformerEmbedding

        model = config.pop("model", model or "all-MiniLM-L6-v2")
        device = config.pop("device", None)
        normalize_embeddings = config.pop("normalize_embeddings", False)
        dimension = config.pop("dimension", None)
        _validate_remaining_config(provider, config)
        return SentenceTransformerEmbedding(
            model=model,
            device=device,
            normalize_embeddings=normalize_embeddings,
            dimension=dimension
        )
    raise ValueError(
        f"Unsupported embedding provider '{provider}'. "
        "Supported providers: ollama, openai, sentence-transformers."
    )
