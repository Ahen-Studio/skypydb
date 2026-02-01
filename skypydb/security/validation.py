"""
Input validation and sanitization module for Skypydb.
Provides protection against injection attacks and ensures data integrity.
"""

import re
from typing import Any, Dict, Optional
from skypydb.errors import ValidationError


# main class for input validation and sanitization
class InputValidator:
    """
    Validates and sanitizes user inputs to prevent security vulnerabilities.
    """

    # Patterns for validation
    TABLE_NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_-]*$')
    COLUMN_NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    # Maximum lengths
    MAX_TABLE_NAME_LENGTH = 64
    MAX_COLUMN_NAME_LENGTH = 64
    MAX_STRING_LENGTH = 10000

    # SQL injection patterns to detect
    SQL_INJECTION_PATTERNS = [
        r';\s*DROP\s+TABLE',
        r';\s*DELETE\s+FROM',
        r';\s*UPDATE\s+',
        r';\s*INSERT\s+INTO',
        r'--',
        r'/\*',
        r'\*/',
        r'xp_',
        r'sp_',
        r'EXEC\s*\(',
        r'EXECUTE\s*\(',
        r'UNION\s+SELECT',
        r'INTO\s+OUTFILE',
        r'LOAD_FILE',
    ]


    # validate a table name
    @classmethod
    def validate_table_name(
        cls,
        table_name: str,
    ) -> str:
        """
        Validate a table name.

        Args:
            table_name: Name of the table to validate

        Returns:
            Validated table name

        Raises:
            ValidationError: If table name is invalid
        """

        if not table_name:
            raise ValidationError("Table name cannot be empty")

        if not isinstance(table_name, str):
            raise ValidationError("Table name must be a string")

        if len(table_name) > cls.MAX_TABLE_NAME_LENGTH:
            raise ValidationError(
                f"Table name too long (max {cls.MAX_TABLE_NAME_LENGTH} characters)"
            )

        if not cls.TABLE_NAME_PATTERN.match(table_name):
            raise ValidationError(
                "Table name must start with a letter or underscore and contain only "
                "alphanumeric characters, underscores, and hyphens"
            )

        # Check for SQL injection patterns
        if cls._contains_sql_injection(table_name):
            raise ValidationError("Table name contains potentially dangerous characters")

        return table_name


    # validate a column name
    @classmethod
    def validate_column_name(
        cls,
        column_name: str,
    ) -> str:
        """
        Validate a column name.

        Args:
            column_name: Name of the column to validate

        Returns:
            Validated column name

        Raises:
            ValidationError: If column name is invalid
        """

        if not column_name:
            raise ValidationError("Column name cannot be empty")

        if not isinstance(column_name, str):
            raise ValidationError("Column name must be a string")

        if len(column_name) > cls.MAX_COLUMN_NAME_LENGTH:
            raise ValidationError(
                f"Column name too long (max {cls.MAX_COLUMN_NAME_LENGTH} characters)"
            )

        if not cls.COLUMN_NAME_PATTERN.match(column_name):
            raise ValidationError(
                "Column name must start with a letter or underscore and contain only "
                "alphanumeric characters and underscores"
            )

        # Check for SQL injection patterns
        if cls._contains_sql_injection(column_name):
            raise ValidationError("Column name contains potentially dangerous characters")

        return column_name


    # validate a string value
    @classmethod
    def validate_string_value(
        cls,
        value: str,
        max_length: Optional[int] = None,
    ) -> str:
        """
        Validate a string value.

        Args:
            value: String value to validate
            max_length: Optional maximum length (defaults to MAX_STRING_LENGTH)

        Returns:
            Validated string value

        Raises:
            ValidationError: If string value is invalid
        """

        if not isinstance(value, str):
            raise ValidationError("Value must be a string")

        max_len = max_length or cls.MAX_STRING_LENGTH

        if len(value) > max_len:
            raise ValidationError(
                f"String value too long (max {max_len} characters)"
            )

        return value


    # validate a data dictionary
    @classmethod
    def validate_data_dict(
        cls,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate a dictionary of data.

        Args:
            data: Dictionary containing data to validate

        Returns:
            Validated data dictionary

        Raises:
            ValidationError: If data is invalid
        """

        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")

        validated_data = {}

        for key, value in data.items():
            # Validate column name
            validated_key = cls.validate_column_name(key)

            # Validate value based on type
            if isinstance(value, str):
                validated_value = cls.sanitize_string(value)
            elif isinstance(value, (int, float, bool)):
                validated_value = value
            elif value is None:
                validated_value = None
            else:
                # Convert to string for other types
                validated_value = cls.sanitize_string(str(value))

            validated_data[validated_key] = validated_value

        return validated_data


    # sanitize a string value
    @classmethod
    def sanitize_string(
        cls,
        value: str,
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

        # Remove null bytes
        value = value.replace('\x00', '')

        # Note: We don't strip SQL characters here because data should be
        # parameterized in queries, but we do basic sanitization

        return value


    # check if a value contains potential SQL injection patterns
    @classmethod
    def _contains_sql_injection(
        cls,
        value: str,
    ) -> bool:
        """
        Check if a value contains potential SQL injection patterns.

        Args:
            value: String to check

        Returns:
            True if potentially dangerous patterns detected
        """

        value_upper = value.upper()

        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True

        return False


    # validate parameters
    @classmethod
    def validate_filter_dict(
        cls,
        filters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate filter parameters for search/delete operations.

        Args:
            filters: Dictionary containing filter parameters

        Returns:
            Validated filter dictionary

        Raises:
            ValidationError: If filters are invalid
        """

        if not isinstance(filters, dict):
            raise ValidationError("Filters must be a dictionary")

        validated_filters = {}

        for key, value in filters.items():
            # Validate column name
            validated_key = cls.validate_column_name(key)

            # Validate value(s)
            if isinstance(value, list):
                validated_value = [
                    cls.sanitize_string(str(v)) if not isinstance(v, (int, float, bool, type(None)))
                    else v
                    for v in value
                ]
            elif isinstance(value, str):
                validated_value = cls.sanitize_string(value)
            elif isinstance(value, (int, float, bool)):
                validated_value = value
            elif value is None:
                validated_value = None
            else:
                validated_value = cls.sanitize_string(str(value))

            validated_filters[validated_key] = validated_value

        return validated_filters


    # validate a table configuration
    @classmethod
    def validate_config(
        cls,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate a table configuration dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            Validated configuration

        Raises:
            ValidationError: If configuration is invalid
        """

        if not isinstance(config, dict):
            raise ValidationError("Configuration must be a dictionary")

        validated_config = {}

        for table_name, table_config in config.items():
            # Validate table name
            validated_table_name = cls.validate_table_name(table_name)

            if not isinstance(table_config, dict):
                raise ValidationError(
                    f"Configuration for table '{table_name}' must be a dictionary"
                )

            validated_table_config = {}

            for column_name, column_type in table_config.items():
                # Validate column name
                validated_column_name = cls.validate_column_name(column_name)

                # Validate column type
                valid_types = [str, int, float, bool, "str", "int", "float", "bool", "auto"]

                if column_type not in valid_types:
                    raise ValidationError(
                        f"Invalid type for column '{column_name}': {column_type}. "
                        f"Valid types are: {valid_types}"
                    )

                validated_table_config[validated_column_name] = column_type

            validated_config[validated_table_name] = validated_table_config

        return validated_config


# validate a table name
def validate_table_name(table_name: str) -> str:
    """
    Convenience function to validate a table name.

    Args:
        table_name: Name to validate

    Returns:
        Validated table name
    """

    return InputValidator.validate_table_name(table_name)


# validate a column name
def validate_column_name(column_name: str) -> str:
    """
    Convenience function to validate a column name.

    Args:
        column_name: Name to validate

    Returns:
        Validated column name
    """

    return InputValidator.validate_column_name(column_name)


# sanitize input
def sanitize_input(value: Any) -> Any:
    """
    Convenience function to sanitize an input value.

    Args:
        value: Value to sanitize

    Returns:
        Sanitized value
    """

    if isinstance(value, str):
        return InputValidator.sanitize_string(value)
    return value
