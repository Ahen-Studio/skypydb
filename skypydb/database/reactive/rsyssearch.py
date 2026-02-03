"""
Module containing the RSysSearch class, which is used to search tables in the database.
"""

import sqlite3
from typing import (
    Any,
    Dict,
    List,
    Optional
)
from skypydb.errors import TableNotFoundError
from skypydb.security.validation import (
    InputValidator,
    ValidationError
)
from skypydb.database.reactive.tables.audit import AuditTable
from skypydb.database.reactive.tables.sysget import SysGet
from skypydb.database.reactive.encryption import Encryption

class RSysSearch:
    def __init__(
        self,
        path: str,
    ):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.audit = AuditTable(path)
        self.sysget = SysGet(path)
        self.encryption = Encryption(path)

    def search(
        self,
        table_name: str,
        index: Optional[str] = None,
        **filters,
    ) -> List[Dict[str, Any]]:
        """
        Search a table for rows matching an optional free-text index value and/or column filters.
        
        Searches the table for rows where the optional index value matches any non-standard column (columns other than `id` and `created_at`) using OR across those columns, and applies any additional filters as AND conditions. Filter values that are lists are translated to SQL IN clauses. Returned rows have encrypted fields decrypted.
        
        Parameters:
            table_name (str): Name of the target table.
            index (Optional[str]): Value to search across all non-standard columns; ignored if None.
            **filters: Column-value pairs to filter results. If a value is a list, it is used with an IN clause (empty lists are invalid).
        
        Returns:
            List[Dict[str, Any]]: Matching rows as dictionaries with sensitive fields decrypted.
        
        Raises:
            ValidationError: If table name, index, or filters fail validation, or an empty list is provided for a filter.
            TableNotFoundError: If the specified table does not exist.
        """

        # Validate table name
        table_name = InputValidator.validate_table_name(table_name)

        # Validate filters
        if filters:
            filters = InputValidator.validate_filter_dict(filters)

        # Sanitize index value
        if index is not None:
            index = InputValidator.sanitize_string(str(index))

        if not self.audit.table_exists(table_name):
            raise TableNotFoundError(f"Table '{table_name}' not found")

        conditions = []
        params = []

        # Add index condition if provided
        # Index searches across all non-standard columns (OR condition)
        if index is not None:
            columns = self.sysget.get_table_columns_names(table_name)
            non_standard_columns = [
                col for col in columns if col not in ("id", "created_at")
            ]

            if non_standard_columns:
                # Search index value in any of the non-standard columns
                index_conditions = []
                for col in non_standard_columns:
                    index_conditions.append(f"[{col}] = ?")
                    params.append(str(index))
                conditions.append(f"({' OR '.join(index_conditions)})")

        # Add additional filters (AND conditions)
        for column, value in filters.items():
            # Handle list values - use IN clause
            if isinstance(value, list):
                if not value:
                    raise ValidationError(f"Empty list provided for filter '{column}'")
                placeholders = ", ".join(["?" for _ in value])
                conditions.append(f"[{column}] IN ({placeholders})")
                params.extend([str(v) for v in value])
            else:
                conditions.append(f"[{column}] = ?")
                params.append(str(value))

        # Build query
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM [{table_name}] WHERE {where_clause}"

        cursor = self.conn.cursor()

        cursor.execute(query, params)

        # Convert rows to dictionaries and decrypt sensitive data
        results = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            decrypted_row = self.encryption.decrypt_data(row_dict)
            results.append(decrypted_row)

        return results
