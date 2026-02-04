"""
Module containing the SysAdd class, which is used to add data to a table in the database.
"""

from typing import List
from skypydb.database.reactive_db import ReactiveDatabase

class SysAdd:
    def __init__(
        self,
        db: "ReactiveDatabase",
        table_name: str
    ):
        self.db = db
        self.table_name = table_name

    def add(
        self,
        **kwargs
    ) -> List[str]:
        """
        Add data to the table.

        Each keyword argument can be a single value or a list.
        If a value is a list, multiple rows will be inserted.
        IDs and timestamps are automatically generated.

        Args:
            **kwargs: Column names and values (can be lists)

        Returns:
            List of IDs for inserted rows

        Example:
            table.add(
                title=["doc1", "doc2"],
                user_id=["user123"],
                content=["content1", "content2"]
            )
        """

        # handle "auto" for id field
        if 'id' in kwargs:
            if kwargs['id'] == ['auto'] or kwargs['id'] == 'auto':
                del kwargs['id']

        # determine number of rows to insert
        max_length = 1
        for key, value in kwargs.items():
            if isinstance(value, list):
                if not value:
                    raise ValueError(f"Empty list provided for '{key}'")
                max_length = max(max_length, len(value))

        # prepare data for each row
        inserted_ids = []
        for row_index in range(max_length):
            row_data = {}
            for key, value in kwargs.items():
                if isinstance(value, list):
                    row_data[key] = value[row_index] if row_index < len(value) else value[-1]
                else:
                    row_data[key] = value

            # validate data against table config
            validated_data = self.db.validate_data_with_config(self.table_name, row_data)

            # insert row with validated data
            row_id = self.db.add_data(self.table_name, validated_data, generate_id=True)

            inserted_ids.append(row_id)
        return inserted_ids
