"""
Module containing the SysSearch class, which is used to search data from a table in the database.
"""

from typing import (
    Optional,
    List,
    Dict,
    Any
)
from skypydb.database.reactive_db import ReactiveDatabase

class SysSearch:
    def __init__(
        self,
        db: "ReactiveDatabase",
        table_name: str
    ):
        self.db = db
        self.table_name = table_name

    def search(
        self,
        index: Optional[str] = None,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Search for data in the table.

        Args:
            index: Value to search for in the index column (primary search key)
            **filters: Additional filters as keyword arguments (column name = value or list of values)

        Returns:
            List of dictionaries containing matching rows

        Example:
            # Search by index and a single filter
            results = table.search(
                index="user123",
                title="document"
            )

            # Search with multiple criteria
            results = table.search(
                index="user123",
                status="active",
                category="news",
            )

            # Search with list values (e.g. uses IN clause in underlying DB)
            results = table.search(
                index="user123",
                title=["doc1", "doc2"]
            )
        """

        # pass filters directly; list values are handled explicitly by the database layer
        return self.db.search(self.table_name, index=index, **filters)
