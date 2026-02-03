"""
Module containing the SysCreate class, which is used to create tables in the database.
"""

import sqlite3
from skypydb.errors import TableAlreadyExistsError
from skypydb.security.validation import InputValidator
from skypydb.schema.schema import TableDefinition
from skypydb.database.reactive.tables.audit import AuditTable
from skypydb.database.reactive.utils import Utils

class SysCreate:
    def __init__(
        self,
        path: str,
    ):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.audit = AuditTable(path)
        self.utils = Utils(path)

    def create_table(
        self,
        table_name: str,
        table_def: TableDefinition,
    ) -> None:
        """
        Create a table based on a TableDefinition from the schema system.

        Args:
            table_name: Name of the table to create
            table_def: TableDefinition containing columns and indexes

        Raises:
            TableAlreadyExistsError: If table already exists
            ValidationError: If table definition is invalid

        Example:
            table_def = defineTable({
                "name": v.string(),
                "email": v.string()
            })
            .index("by_email", ["email"])

            database.create_table("users", table_def)
        """

        # Validate table name
        table_name = InputValidator.validate_table_name(table_name)

        # Validate column names
        for col_name in table_def.columns.keys():
            InputValidator.validate_column_name(col_name)

        if self.audit.table_exists(table_name):
            raise TableAlreadyExistsError(f"Table '{table_name}' already exists")

        cursor = self.conn.cursor()

        # Get SQL column definitions from table definition
        sql_columns = table_def.get_sql_columns()
        columns_sql = ", ".join(sql_columns)

        # Create table
        cursor.execute(
            f"""
            CREATE TABLE [{table_name}] (
                {columns_sql}
            )
            """
        )

        # Create indexes
        for index_sql in table_def.get_sql_indexes():
            cursor.execute(index_sql)

        # Save table definition as configuration
        config = self.utils.table_def_to_config(table_def)
        self.utils.save_table_config(table_name, config)
        self.conn.commit()
