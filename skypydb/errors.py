"""
Custom exceptions for Skypydb.
"""

# base errors handling
class SkypydbError(Exception):
    """
    Base exception for all Skypydb errors.
    """

    CODE = "SKY001"
    default_message = "An error occurred."

    # initialize the SkypydbError instance for handling and formatting error messages
    def __init__(
        self,
        message=None,
    ):
        """
        Initialize the SkypydbError instance.

        Args:
            message (str, optional): The error message. Defaults to None.
        """

        self.message = message

        if self.message:
            formatted_message = f"[{self.CODE}] {self.message}"
        else:
            # Use a class-specific default message when provided, otherwise fall back
            # to the generic default_message defined on the base class.
            default_msg = getattr(self, "default_message", self.__class__.__name__)
            formatted_message = f"[{self.CODE}] {default_msg}"

        super().__init__(formatted_message)


# table not found error handling
class TableNotFoundError(SkypydbError):
    """
    Raised when a table is not found.
    """

    CODE = "SKY101"
    default_message = "Table not found."


# table already exists error handling
class TableAlreadyExistsError(SkypydbError):
    """
    Raised when trying to create a table that already exists.
    """

    CODE = "SKY102"
    default_message = "Table already exists."


# database errors handling
class DatabaseError(SkypydbError):
    """
    Raised when a database-level operation fails.
    """

    CODE = "SKY103"
    default_message = "Database operation failed."


# search errors handling
class InvalidSearchError(SkypydbError):
    """
    Raised when search parameters are invalid.
    """

    CODE = "SKY201"
    default_message = "Invalid search parameters."


# security errors handling
class SecurityError(SkypydbError):
    """
    Raised when a security operation fails.
    """

    CODE = "SKY301"
    default_message = "Security operation failed."


# validation errors handling
class ValidationError(SkypydbError):
    """
    Raised when input validation fails.
    """

    CODE = "SKY302"
    default_message = "Input validation failed."


# encryption errors handling
class EncryptionError(SkypydbError):
    """
    Raised when encryption/decryption operations fail.
    """

    CODE = "SKY303"
    default_message = "Encryption or decryption operation failed."


# collection not found error handling
class CollectionNotFoundError(SkypydbError):
    """
    Raised when a vector collection is not found.
    """

    CODE = "SKY401"
    default_message = "Collection not found."


# collection already exists error handling
class CollectionAlreadyExistsError(SkypydbError):
    """
    Raised when trying to create a collection that already exists.
    """

    CODE = "SKY402"
    default_message = "Collection already exists."


# embedding errors handling
class EmbeddingError(SkypydbError):
    """
    Raised when embedding generation fails.
    """

    CODE = "SKY403"
    default_message = "Embedding generation failed."


# vector search errors handling
class VectorSearchError(SkypydbError):
    """
    Raised when vector similarity search fails.
    """

    CODE = "SKY404"
    default_message = "Vector similarity search failed."
