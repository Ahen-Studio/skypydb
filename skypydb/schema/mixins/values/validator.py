"""
Module containing the Validator class, which is used to validate type values.
"""

from typing import Any

class Validator:
    """
    Base class for type validators.
    """

    def validate(
        self,
        value: Any
    ) -> bool:
        """
        Validate a value.

        Args:
            value: Value to validate

        Returns:
            True if value is valid
        """

        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError
