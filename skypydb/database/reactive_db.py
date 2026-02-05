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
from skypydb.database.mixins.reactive import (
    SysCreate,
    SysDelete,
    SysGet,
    AuditTable,
    Utils,
    Encryption,
    RSysAdd,
    RSysSearch,
    RSysDelete
)

class ReactiveDatabase(
    AuditTable,
    Utils,
    SysCreate,
    SysDelete,
    SysGet,
    RSysAdd,
    RSysSearch,
    RSysDelete,
    Encryption
):
    def __init__(
        self,
        path: str,
        encryption_key: Optional[str] = None,
        salt: Optional[bytes] = None,
        encrypted_fields: Optional[List[str]] = None
    ):
        """
        Initialize reactive database with a single shared SQLite connection.

        Args:
            path: Path to SQLite database file
            encryption_key: Optional key for field-level encryption
            salt: Optional salt for encryption key derivation
            encrypted_fields: Optional List of field names to encrypt
        """

        super().__init__()

        self.path = path

        # create directory if needed
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        # create sqlite connection
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # initialize encryption
        self._init_encryption(path, encryption_key, salt, encrypted_fields)

        # initialize all components
        self._init_components()

        # ensure system tables exist
        self.check_config_table()

    def _init_encryption(
        self,
        path,
        encryption_key,
        salt,
        encrypted_fields
    ):
        """
        Initialize encryption components.
        """

        # setup encryption attributes
        self.encryption_key = encryption_key
        self.salt = salt
        if encryption_key and encrypted_fields is None:
            raise ValueError(
                "encrypted_fields must be explicitly set when encryption_key is provided; "
                "use [] to disable encryption."
            )
        self.encrypted_fields = encrypted_fields if encrypted_fields is not None else []
        self._encryption_manager = EncryptionManager(encryption_key=encryption_key, salt=salt)
        
        # initialize Encryption parent class for encrypt_data/decrypt_data methods
        Encryption.__init__(
            self,
            path=path,
            encryption_key=encryption_key,
            salt=salt,
            encrypted_fields=encrypted_fields
        )

    def _init_components(self):
        """
        Initialize all database components with the shared connection.
        """

        # initialize all parent classes with the shared connection
        # we pass conn=self.conn so all classes share the same connection
        AuditTable.__init__(self, conn=self.conn)
        Utils.__init__(self, conn=self.conn)
        SysCreate.__init__(self, conn=self.conn)
        SysDelete.__init__(self, conn=self.conn)
        SysGet.__init__(self, conn=self.conn, encryption=self)
        RSysAdd.__init__(self, conn=self.conn, encryption=self)
        RSysSearch.__init__(self, conn=self.conn, encryption=self)
        RSysDelete.__init__(self, conn=self.conn)

    def close(self) -> None:
        """
        Close database connection.
        """

        if self.conn:
            self.conn.close()
