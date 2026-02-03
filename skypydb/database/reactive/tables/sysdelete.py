"""
Module containing the SysDelete class, which is used to delete tables in the database.
"""

import sqlite3
from skypydb.security.validation import InputValidator
from skypydb.errors import TableNotFoundError
from skypydb.database.reactive.tables.audit import AuditTable

class SysDelete:
    def __init__(
        self,
        path: str,
    ):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.audit = AuditTable(path)

    def delete_table(
        self,
        table_name: str,
    ) -> None:
        """
        Delete a table.

        Args:
            table_name: Name of the table to delete

        Raises:
            TableNotFoundError: If table doesn't exist
            ValidationError: If table name is invalid
        """

        # Validate table name
        table_name = InputValidator.validate_table_name(table_name)

        if not self.audit.table_exists(table_name):
            raise TableNotFoundError(f"Table '{table_name}' not found")

        cursor = self.conn.cursor()

        cursor.execute(f"DROP TABLE [{table_name}]")
        self.conn.commit()
