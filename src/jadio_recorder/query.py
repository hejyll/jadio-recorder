from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeVar, Union

from dataclasses_json import DataClassJsonMixin

T = TypeVar("T")
Condition = Optional[Union[T, Dict[str, Union[T, List[T]]]]]
MongoQueryDict = Dict[str, Union[Dict[str, Any], List[Dict[str, Any]]]]

__all__ = [
    "ProgramQuery",
    "queries_to_mongo_format",
]


@dataclass
class ProgramQuery(DataClassJsonMixin):
    service_id: Condition[str] = None
    station_id: Condition[str] = None
    program_id: Condition[int] = None
    episode_id: Condition[int] = None
    pub_date: Condition[dt.datetime] = None
    duration: Condition[int] = None
    program_title: Condition[str] = None
    episode_title: Condition[str] = None
    description: Condition[str] = None
    information: Condition[str] = None
    link_url: Condition[str] = None
    performers: Condition[List[str]] = None
    guests: Condition[List[str]] = None
    is_video: Condition[bool] = None

    def to_mongo_format(self) -> MongoQueryDict:
        ret = [{key: cond} for key, cond in self.to_dict().items() if cond]
        return {"$and": ret}


def queries_to_mongo_format(queries: List[ProgramQuery]) -> MongoQueryDict:
    return {"$or": [query.to_mongo_format() for query in queries]}
