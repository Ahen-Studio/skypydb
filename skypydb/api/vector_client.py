"""
Vector Client API for Skypydb.
"""

import os
from typing import (
    Any,
    Dict,
    Optional
)
from skypydb.database.vector_db import VectorDatabase
from skypydb.embeddings import get_embedding_function
from skypydb.api.collection import Collection
from skypydb.database.database_linker import DatabaseLinker
from skypydb.api.mixins.vector import (
    SysCreate,
    SysGet,
    SysList,
    SysDelete,
    Utils
)

class VectorClient(
    SysCreate,
    SysGet,
    SysList,
    SysDelete,
    Utils
):
    """
    Vector client for interacting with Skypydb.
    """

    def __init__(
        self,
        path: str = "./db/_generated/vector.db",
        embedding_provider: str = "ollama",
        embedding_model_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Vector Client.

        Args:
            path: Path to the database file. Defaults to ./db/_generated/vector.db
            embedding_provider: Embedding provider (ollama, openai, sentence-transformers)
            embedding_model_config: Provider-specific config dictionary.

        Example:
            # Basic usage with defaults
            client = skypydb.VectorClient()

            # With explicit provider config
            client = skypydb.VectorClient(
                embedding_provider="openai",
                embedding_model_config={
                    "api_key": "your-openai-api-key",
                    "model": "text-embedding-3-small"
                }
            )
        """

        # constant to define the path to the database file
        DB_PATH = path

        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self.path = DB_PATH
        if embedding_model_config is not None and not isinstance(embedding_model_config, dict):
            raise TypeError("embedding_model_config must be a dictionary when provided.")

        provider = embedding_provider.lower().strip().replace("_", "-")
        model_config: Dict[str, Any] = dict(embedding_model_config or {})

        # set up embedding function
        self._embedding_function = get_embedding_function(
            provider=provider,
            **model_config
        )

        self.database_linker = DatabaseLinker()

        # initialize vector database
        self._db = VectorDatabase(
            path=DB_PATH,
            embedding_function=self._embedding_function
        )
        self.database_linker.ensure_db_link_metadata(DB_PATH, db_type="vector")

        # cache for collection instances
        self._collections: Dict[str, Collection] = {}

    def close(
        self,
    ) -> None:
        """
        Close the database connection.
        """

        self._db.close()
        self._collections.clear()
