"""
Module containing the SysDelete class, which is used to delete data from a table in the database.
"""

from skypydb.database.reactive_db import ReactiveDatabase

class SysDelete:
    def __init__(
        self,
        db: "ReactiveDatabase",
        table_name: str
    ):
        self.db = db
        self.table_name = table_name

    def delete(
        self,
        **filters
    ) -> int:
        """
        Delete data from the table based on filters.

        Args:
            **filters: Filters as keyword arguments (column name = value or list of values)

        Returns:
            Number of rows deleted

        Example:
            # Delete by ID
            table.delete(
                id="123"
            )

            # Delete by multiple criteria
            table.delete(
                user_id="user123",
                title="document"
            )

            # Delete with list values (uses IN clause)
            table.delete(
                title=["doc1", "doc2"]
            )
        """

        return self.db.delete(self.table_name, **filters)
