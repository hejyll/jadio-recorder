from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeVar, Union

from dataclasses_json import DataClassJsonMixin

T = TypeVar("T")
Condition = Optional[Union[T, Dict[str, T]]]


__all__ = [
    "ProgramQuery",
    "to_query",
]


@dataclass
class ProgramQuery(DataClassJsonMixin):
    service_id: Condition[str] = None
    station_id: Condition[str] = None
    program_id: Condition[int] = None
    episode_id: Condition[int] = None
    pub_date: Condition[datetime.datetime] = None
    duration: Condition[int] = None
    program_title: Condition[str] = None
    episode_title: Condition[str] = None
    description: Condition[str] = None
    information: Condition[str] = None
    link_url: Condition[str] = None
    performers: Condition[List[str]] = None
    guests: Condition[List[str]] = None
    is_video: Condition[bool] = None

    def to_query(self) -> Dict[str, List[Dict[str, Any]]]:
        ret = []
        for key, condition in self.to_dict().items():
            if condition is None:
                continue
            ret.append({key: condition})
        return {"$and": ret}


def to_query(queries: List[ProgramQuery]) -> Dict[str, Dict[str, Any]]:
    return {"$or": [query.to_query() for query in queries]}
