"""
Skypydb - Open-source reactive database for Python.
"""

from .api.client import Client
from .errors import (
    DatabaseError,
    InvalidSearchError,
    SkypydbError,
    TableAlreadyExistsError,
    TableNotFoundError,
)
from .security import (
    EncryptionManager,
    EncryptionError,
    create_encryption_manager,
)

__version__ = "0.1.6"

__all__ = [
    "Client",
    "SkypydbError",
    "DatabaseError",
    "TableNotFoundError",
    "TableAlreadyExistsError",
    "InvalidSearchError",
    "EncryptionManager",
    "EncryptionError",
    "create_encryption_manager",
]
