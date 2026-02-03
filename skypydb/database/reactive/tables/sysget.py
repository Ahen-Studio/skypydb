"""
Module containing the SysGet class, which is used to get names in the database.
"""

import sqlite3
from typing import (
    List,
    Dict,
    Any
)
from skypydb.errors import TableNotFoundError
from skypydb.security.validation import InputValidator
from skypydb.database.reactive.tables.audit import AuditTable
from skypydb.database.reactive.encryption import Encryption

class SysGet:
    def __init__(
        self,
        path: str,
    ):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.audit = AuditTable(path)
        self.encryption = Encryption(path)

    def get_all_tables_names(
        self,
    ) -> List[str]:
        """
        Get list of all table names.
        """

        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != '_skypy_config'"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_table_columns_names(
        self,
        table_name: str,
    ) -> List[str]:
        """
        Get list of column names for a table.
        """

        # Validate table name
        table_name = InputValidator.validate_table_name(table_name)

        if not self.audit.table_exists(table_name):
            raise TableNotFoundError(f"Table '{table_name}' not found")

        cursor = self.conn.cursor()

        cursor.execute(f"PRAGMA table_info([{table_name}])")
        return [row[1] for row in cursor.fetchall()]

    def get_all_data(
        self,
        table_name: str,
    ) -> List[Dict[str, Any]]:
        """
        Get all data from a table.
        """

        # Validate table name
        table_name = InputValidator.validate_table_name(table_name)

        if not self.audit.table_exists(table_name):
            raise TableNotFoundError(f"Table '{table_name}' not found")

        cursor = self.conn.cursor()

        cursor.execute(f"SELECT * FROM [{table_name}]")

        results = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            decrypted_row = self.encryption.decrypt_data(row_dict)
            results.append(decrypted_row)

        return results
