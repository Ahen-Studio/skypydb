"""
Input validation and sanitization module for Skypydb.
"""

import re
from skypydb.security.mixins.validation import (
    SysCheck,
    SysSanitize,
    SysValidation
)

class InputValidator(
    SysCheck,
    SysSanitize,
    SysValidation
):
    """
    Validates and sanitizes user inputs to prevent security vulnerabilities.
    """

    # patterns for validation
    TABLE_NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_-]*$')
    COLUMN_NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    # maximum lengths
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
