"""
Module containing the RSysDelete class, which is used to delete data from a table.
"""

import sqlite3
from skypydb.security.validation import InputValidator
from skypydb.errors import TableNotFoundError
from skypydb.database.reactive.tables.audit import AuditTable

class RSysDelete:
    def __init__(
        self,
        path: str,
    ):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.audit = AuditTable(path)

    def delete(
        self,
        table_name: str,
        **filters,
    ) -> int:
        """
        Delete data from a table based on filters.

        Args:
            table_name: Name of the table
            **filters: Filters as keyword arguments (column name = value)

        Returns:
            Number of rows deleted

        Example:
            db.delete(
                table_name="my_table",
                id="123"
            )
            db.delete(
                table_name="my_table",
                user_id="user123",
                title="document"
            )
 
        Raises:
            ValidationError: If input parameters are invalid
        """

        # Validate table name
        table_name = InputValidator.validate_table_name(table_name)

        # Validate filters
        if filters:
            filters = InputValidator.validate_filter_dict(filters)

        if not self.audit.table_exists(table_name):
            raise TableNotFoundError(f"Table '{table_name}' not found")

        if not filters:
            # Safety check - don't allow deleting all rows without explicit filters
            raise ValueError("Cannot delete without filters. Use filters to specify which rows to delete.")

        conditions = []
        params = []

        # Build WHERE clause from filters
        for column, value in filters.items():
            # Handle list values - use IN clause
            if isinstance(value, list) and len(value) > 0:
                placeholders = ", ".join(["?" for _ in value])
                conditions.append(f"[{column}] IN ({placeholders})")
                params.extend([str(v) for v in value])
            else:
                conditions.append(f"[{column}] = ?")
                params.append(str(value))

        # Build DELETE query
        where_clause = " AND ".join(conditions)
        query = f"DELETE FROM [{table_name}] WHERE {where_clause}"

        cursor = self.conn.cursor()

        cursor.execute(query, params)
        self.conn.commit()

        return cursor.rowcount
