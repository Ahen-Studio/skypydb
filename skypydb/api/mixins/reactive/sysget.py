"""
Module containing the SysGet class, which is used to get a table.
"""

from skypydb.errors import TableNotFoundError
from skypydb.table.table import Table
from skypydb.api.mixins.reactive.schema_loader import load_schema

class SysGet:
    def get_table(
        self,
        table_name: str
    ) -> Table:
        """
        Get an existing table by name.

        Args:
            table_name: Name of the table

        Returns:
            Table instance

        Raises:
            TableNotFoundError: If table doesn't exist

        Example:
            tables = client.create_table()
            users_table = tables["users"]
            
            # Later, get the table again:
            users = client.get_table("users")
        """

        if not self.db.table_exists(table_name):
            raise TableNotFoundError(f"Table '{table_name}' not found")
        return Table(self.db, table_name)

    def get_or_create_table(self) -> dict:
        """
        Get existing tables from schema or create them if missing.

        Returns:
            Dictionary mapping table names to Table instances

        Example:
            tables = client.get_or_create_table()
            users_table = tables["users"]
        """

        schema = load_schema()

        table_names = self.db.get_or_create_table(schema)
        return {
            name: Table(self.db, name)
            for name in table_names
        }