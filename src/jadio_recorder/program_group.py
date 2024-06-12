from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from dataclasses_json import DataClassJsonMixin
from dataclasses_json.core import Json

from .program_category import ProgramCategory
from .program_query import ProgramQuery

__all__ = [
    "ProgramGroup",
]


@dataclass
class ProgramGroup(DataClassJsonMixin):
    """Represents a grouping of radio programs.

    Attributes:
        query (`ProgramQuery`): Query for the program to be grouped.
        title (str): Title of the program group.
        description (str): Description of the program group.
        category (str or `ProgramCategory` or list): Category of the program
            group. Multiple categories can be specified.
        tags (str or list): Any tag attached to the program group.
        copyright (str): Copyright of the program group.
        link_url (str): URL of the program group link.
        image_url (str): URL of the program group image.
        author (str): Author of the program group.
        enable_record (bool): Whether to record programs that correspond to
            the program group or not.
        enable_feed (bool): Whether to feed the program group or not.
    """

    query: ProgramQuery
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Union[str, ProgramCategory, List[ProgramCategory]]] = None
    tags: Optional[Union[str, List[str]]] = None
    copyright: Optional[str] = None
    link_url: Optional[str] = None
    image_url: Optional[str] = None
    author: Optional[str] = None
    enable_record: bool = False
    enable_feed: bool = False

    def to_dict(self, encode_json: bool = False) -> Json:
        ret = super().to_dict(encode_json)
        return {key: value for key, value in ret.items() if value is not None}

    @classmethod
    def from_dict(cls, kvs: Json, *, infer_missing: bool = False) -> ProgramGroup:
        ret = super().from_dict(kvs, infer_missing=infer_missing)
        if ret.category is not None:
            ret.category = ProgramCategory.from_value(ret.category)
        return ret
