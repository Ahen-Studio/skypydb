"""
Custom exceptions for Skypydb.
"""

# base errors handling
class SkypydbError(Exception):
    """
    Base exception for all Skypydb errors.
    """

    pass


# database errors handling
class TableNotFoundError(SkypydbError):
    """
    Raised when a table is not found.
    """

    pass


class TableAlreadyExistsError(SkypydbError):
    """
    Raised when trying to create a table that already exists.
    """

    pass


class DatabaseError(SkypydbError):
    """
    Raised when a database operation fails.
    """

    pass


class InvalidSearchError(SkypydbError):
    """
    Raised when search parameters are invalid.
    """

    pass


# security errors handling
class SecurityError(SkypydbError):
    """
    Raised when a security operation fails.
    """

    pass

class ValidationError(SkypydbError):
    """
    Raised when input validation fails.
    """
    
    pass

class EncryptionError(SkypydbError):
    """
    Raised when encryption/decryption operations fail.
    """
    
    pass
