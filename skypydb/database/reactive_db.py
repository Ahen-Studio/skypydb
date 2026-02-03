"""
Reactive Database module for Skypydb.
"""

import sqlite3
from pathlib import Path
from typing import (
    List,
    Optional
)
from skypydb.security.encryption import EncryptionManager
from skypydb.database.reactive import (
    SysCreate,
    SysDelete,
    SysGet,
    AuditTable,
    Utils,
    Encryption,
    RSysAdd,
    RSysSearch,
    RSysDelete,
)

class ReactiveDatabase(SysCreate, SysDelete, SysGet, AuditTable, Utils, Encryption, RSysAdd, RSysSearch, RSysDelete):
    def __init__(
        self,
        path: str,
        encryption_key: Optional[str] = None,
        salt: Optional[bytes] = None,
        encrypted_fields: Optional[List[str]] = None,
    ):
        """
        Initialize reactive database with a single shared SQLite connection.

        Args:
            path: Path to SQLite database file
            encryption_key: Optional key for field-level encryption
            salt: Optional salt for encryption key derivation
            encrypted_fields: Optional List of field names to encrypt
        """

        self.path = path
        # Create directory if needed
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        # Create single shared connection (used by all mixins)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        # Setup encryption
        self.encryption_key = encryption_key
        self.salt = salt
        if encryption_key and encrypted_fields is None:
            raise ValueError(
                "encrypted_fields must be explicitly set when encryption_key is provided; "
                "use [] to disable encryption."
            )
        self.encrypted_fields = encrypted_fields if encrypted_fields is not None else []
        self.encryption = EncryptionManager(encryption_key=encryption_key, salt=salt)
        # Ensure system tables exist
        self.check_config_table()

    def close(
        self,
    ) -> None:
        """
        Close database connection.
        """

        if self.conn:
            self.conn.close()
