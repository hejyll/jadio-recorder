from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeVar, Union

from dataclasses_json import DataClassJsonMixin

T = TypeVar("T")
ConditionT = Union[T, List[T]]

__all__ = [
    "ProgramQuery",
    "queries_to_mongo_format",
]


def _to_list(x: Union[T, List[T]]) -> List[T]:
    return [x] if not isinstance(x, list) else x


@dataclass
class ProgramQuery(DataClassJsonMixin):
    """Class for generating queries to find radio programs registered in MongoDB.

    Attributes:
        service_id (condition of (int or str)): Search condition for service ID(s).
        station_id (condition of (int or str)): Search condition for station ID(s).
        program_id (condition of (int or str)): Search condition for program ID(s).
        episode_id (condition of (int or str)): Search condition for episode ID(s).
        pub_date (condition of `datetime.datetime`): Search condition for publication date.
            The search condition changes as follows depending on how the value is given.
            * single value or [value]: condition <= value
            * [value0, value1]: value0 <= condition < value1
            * [None, value]: condition < value
            * [value, None]: value <= condition
        duration (condition of (int or float)): Search condition for duration.
            The search condition changes as follows depending on how the value is given.
            * single value or [value]: condition <= value
            * [value0, value1]: value0 <= condition < value1
            * [None, value]: condition < value
            * [value, None]: value <= condition
        keywords (condition of str): Search keywords.
        is_video (condition of bool): Search condition whether video or audio.
    """

    service_id: Optional[ConditionT[Union[int, str]]] = None
    station_id: Optional[ConditionT[Union[int, str]]] = None
    program_id: Optional[ConditionT[Union[int, str]]] = None
    episode_id: Optional[ConditionT[Union[int, str]]] = None
    pub_date: Optional[ConditionT[dt.datetime]] = None
    duration: Optional[ConditionT[Union[int, float]]] = None
    keywords: Optional[ConditionT[str]] = None
    is_video: Optional[ConditionT[bool]] = None

    def to_mongo_format(self) -> Dict[str, Any]:
        and_cond = []
        if self.service_id:
            and_cond.append({"service_id": {"$in": _to_list(self.service_id)}})
        if self.station_id:
            and_cond.append({"station_id": {"$in": _to_list(self.station_id)}})
        if self.program_id:
            and_cond.append({"program_id": {"$in": _to_list(self.program_id)}})
        if self.episode_id:
            and_cond.append({"episode_id": {"$in": _to_list(self.episode_id)}})
        if self.pub_date:
            key = "pub_date"
            queries = _to_list(self.pub_date)
            if len(queries) > 2:
                raise ValueError(f"len({key}) must be less than 2.")
            if len(queries) == 1:
                and_cond.append({key: {"$lte": queries[0]}})
            elif queries[0] is None and queries[1] is None:
                pass
            elif queries[0] is None:
                and_cond.append({key: {"$lt": queries[1]}})
            elif queries[1] is None:
                and_cond.append({key: {"$gte": queries[0]}})
            else:
                and_cond.append({key: {"$gte": queries[0], "$lt": queries[1]}})
        if self.duration:
            key = "duration"
            queries = _to_list(self.pub_date)
            if len(queries) > 2:
                raise ValueError(f"len({key}) must be less than 2.")
            if len(queries) == 1:
                and_cond.append({key: {"$lte": queries[0]}})
            elif queries[0] is None and queries[1] is None:
                pass
            elif queries[0] is None:
                and_cond.append({key: {"$lt": queries[0]}})
            elif queries[1] is None:
                and_cond.append({key: {"$gte": queries[0]}})
            else:
                and_cond.append({key: {"$gte": queries[0], "$lt": queries[1]}})
        if self.keywords:
            queries = _to_list(self.keywords)
            keys = ["performers", "guests"]
            cond = [{key: {"$in": queries}} for key in keys]
            keys = ["program_title", "episode_title", "description", "information"]
            cond = sum(
                [[{key: {"$regex": query}} for query in queries] for key in keys], cond
            )
            and_cond.append({"$or": cond})
        if not and_cond:
            return {}
        return {"$and": and_cond}


def queries_to_mongo_format(queries: List[ProgramQuery]) -> Dict[str, List[Any]]:
    return {"$or": [query.to_mongo_format() for query in queries]}
