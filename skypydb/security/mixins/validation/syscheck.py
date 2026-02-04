"""
Module containing the SysCheck class, which is used to check SQL queries for potential SQL injection patterns.
"""

import re
from skypydb.security.validation import InputValidator

class SysCheck:
    def __init__(
        self,
        input_validator: InputValidator
    ):
        self.input_validator = input_validator

    def _contains_sql_injection(
        self,
        value: str
    ) -> bool:
        """
        Check if a value contains potential SQL injection patterns.

        Args:
            value: String to check

        Returns:
            True if potentially dangerous patterns detected
        """

        value_upper = value.upper()

        for pattern in self.input_validator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False
