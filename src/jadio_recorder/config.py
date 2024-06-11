from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from .query import ProgramQuery


@dataclass
class RecordConfig(DataClassJsonMixin):
    query: ProgramQuery
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
