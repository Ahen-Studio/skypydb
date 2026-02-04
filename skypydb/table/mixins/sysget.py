"""
Module containing the SysGet class, which is used to get all the data from a table in the database.
"""

from typing import (
    List,
    Dict,
    Any
)
from skypydb.database.reactive_db import ReactiveDatabase

class SysGet:
    def __init__(
        self,
        db: "ReactiveDatabase",
        table_name: str
    ):
        self.db = db
        self.table_name = table_name

    def get_all(
        self
    ) -> List[Dict[str, Any]]:
        """
        Get all data from the table.
        """

        return self.db.get_all_data(self.table_name)
