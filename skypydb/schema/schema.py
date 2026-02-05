"""
Schema system for Skypydb.
"""

from typing import (
    List,
    Dict,
    Any,
    Optional
)
from .values import Validator
from skypydb.schema.mixins.schema.sysdef import SysDef
from skypydb.schema.mixins.schema.sysget import SysGet
from skypydb.schema.mixins.schema.sysschema import SysSchema
from skypydb.schema.mixins.schema.sysindex import SysIndex
from skypydb.schema.mixins.schema.sysvalidate import SysValidate

class TableDefinition(
    SysIndex,
    SysValidate,
    SysDef,
    SysGet,
    SysSchema
):
    """
    Definition of a table with columns and indexes.
    """

    def __init__(
        self,
        columns: Dict[str, Validator],
        table_name: Optional[str] = None
    ):
        """
        Initialize table definition.

        Args:
            columns: Dictionary mapping column names to validators
            table_name: Optional table name (can be used later)
        """

        super().__init__()

        self.columns = columns
        self.indexes: List[Dict[str, Any]] = []
        self.table_name = table_name
