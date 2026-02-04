"""
Module containing the SysSanitize class, which is used to sanitize data in the database.
"""

from typing import Any

class SysSanitize:
    def sanitize_string(
        self,
        value: str
    ) -> str:
        """
        Sanitize a string value by removing potentially dangerous characters.

        Args:
            value: String to sanitize

        Returns:
            Sanitized string
        """

        if not isinstance(value, str):
            return str(value)

        # remove null bytes
        value = value.replace('\x00', '')

        # note: We don't strip SQL characters here because data should be
        # parameterized in queries, but we do basic sanitization
        return value

def sanitize_input(
    self,
    value: Any
) -> Any:
    """
    Convenience function to sanitize an input value.

    Args:
        value: Value to sanitize
        sys_sanitize: SysSanitize instance to use for sanitization

    Returns:
        Sanitized value
    """

    if isinstance(value, str):
        return self.sanitize_string(value)
    return value
