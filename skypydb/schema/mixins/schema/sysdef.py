"""

"""

from typing import (
    List,
    Dict,
    Any,
    Optional
)
from skypydb.schema import (
    TableDefinition,
    Validator
)
from skypydb.schema.mixins.schema.sysschema import SysSchema

class SysDef:
    def __init__(
        self,
        columns: Dict[str, Validator],
        table_name: Optional[str] = None
    ):
        self.columns = columns
        self.indexes: List[Dict[str, Any]] = []
        self.table_name = table_name

def defineTable(
    columns: Dict[str, Validator]
) -> TableDefinition:
    """
    Define a table with its columns and types.

    Args:
        columns: Dictionary mapping column names to validators

    Returns:
        TableDefinition that can be configured with indexes

    Example:
        users = defineTable({
            "name": v.string(),
            "email": v.string(),
            "age": v.int64(),
            "active": v.boolean(),
            "bio": v.optional(v.string())
        })
        .index("by_email", ["email"])
        .index("by_age", ["age"])
    """

    return TableDefinition(columns)

def defineSchema(
    tables: Dict[str, TableDefinition]
) -> SysSchema:
    """
    Define a schema with multiple tables.

    Args:
        tables: Dictionary mapping table names to table definitions

    Returns:
        Schema object containing all tables

    Example:
        schema = defineSchema({
            "users": defineTable({
                "name": v.string(),
                "email": v.string()
            })
            .index("by_name", ["name"]),
            
            "posts": defineTable({
                "title": v.string(),
                "content": v.string()
            })
            .index("by_title", ["title"])
        })
    """

    # set table names in definitions
    for table_name, table_def in tables.items():
        table_def.table_name = table_name
    return SysSchema(tables)
