"""
Module containing the RSysAdd class, which is used to add data to a table.
"""

import sqlite3
from typing import Dict, Any
import uuid
from datetime import datetime
from skypydb.security.validation import InputValidator
from skypydb.errors import TableNotFoundError
from skypydb.database.reactive.tables.audit import AuditTable
from skypydb.database.reactive.encryption import Encryption

class RSysAdd:
    def __init__(
        self,
        path: str,
    ):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.audit = AuditTable(path)
        self.encryption = Encryption(path)

    def add_data(
        self,
        table_name: str,
        data: Dict[str, Any],
        generate_id: bool = True,
    ) -> str:
        """
        Insert data into a table.

        Args:
            table_name: Name of the table
            data: Dictionary of column names and values
            generate_id: Whether to generate UUID automatically

        Returns:
            The ID of the inserted row

        Raises:
            ValidationError: If input data is invalid
        """

        # Validate table name
        table_name = InputValidator.validate_table_name(table_name)

        # Validate data dictionary
        data = InputValidator.validate_data_dict(data)

        if not self.audit.table_exists(table_name):
            raise TableNotFoundError(f"Table '{table_name}' not found")

        # Generate ID if needed
        if generate_id:
            data["id"] = str(uuid.uuid4())

        # Add created_at timestamp
        if "created_at" not in data:
            data["created_at"] = datetime.now().isoformat()

        # Ensure columns exist
        columns_to_add = [col for col in data.keys() if col not in ("id", "created_at")]
        if columns_to_add:
            self.audit.add_columns_if_needed(table_name, columns_to_add)

        # Encrypt sensitive data before storing
        encrypted_data = self.encryption.encrypt_data(data)

        # Build INSERT query
        columns = list(encrypted_data.keys())
        placeholders = ", ".join(["?" for _ in columns])
        column_names = ", ".join([f"[{col}]" for col in columns])

        cursor = self.conn.cursor()

        cursor.execute(
            f"INSERT INTO [{table_name}] ({column_names}) VALUES ({placeholders})",
            [str(encrypted_data[col]) for col in columns],
        )
        self.conn.commit()

        return data["id"]
