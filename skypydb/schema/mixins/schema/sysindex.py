"""

"""

from typing import (
    List,
    Dict,
    Any
)
from skypydb.schema import (
    Validator,
    TableDefinition
)

class SysIndex:
    def __init__(
        self,
        columns: Dict[str, Validator],
    ):
        self.columns = columns
        self.indexes: List[Dict[str, Any]] = []

    def index(
        self,
        name: str,
        fields: List[str]
    ) -> "TableDefinition":
        """
        Add an index to the table definition.

        Args:
            name: Name of the index
            fields: List of column names to index

        Returns:
            Self for method chaining
        """

        # Validate that fields exist in columns
        for field in fields:
            if field not in self.columns:
                raise ValueError(
                    f"Cannot create index '{name}' on non-existent field '{field}'. "
                    f"Available fields: {list(self.columns.keys())}"
                )

        self.indexes.append({
            "name": name,
            "fields": fields
        })
        return self
