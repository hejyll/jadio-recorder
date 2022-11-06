import dataclasses
import json
from typing import Any, Dict, List, Optional, TypeVar, Union

T = TypeVar("T")
Condition = Optional[Union[T, Dict[str, T]]]


@dataclasses.dataclass
class ProgramQuery:
    station_id: Condition[str] = None
    program_id: Condition[int] = None
    program_name: Condition[str] = None
    program_url: Condition[str] = None
    description: Condition[str] = None
    information: Condition[str] = None
    performers: Condition[List[str]] = None
    episode_id: Condition[int] = None
    episode_name: Condition[str] = None
    datetime: Condition[Any] = None
    duration: Condition[int] = None
    ascii_name: Condition[str] = None
    guests: Condition[List[str]] = None
    is_video: Condition[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgramQuery":
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        ret = {
            "station_id": self.station_id,
            "program_id": self.program_id,
            "program_name": self.program_name,
            "program_url": self.program_url,
            "description": self.description,
            "information": self.information,
            "performers": self.performers,
            "episode_id": self.episode_id,
            "episode_name": self.episode_name,
            "datetime": self.datetime,
            "duration": self.duration,
            "ascii_name": self.ascii_name,
            "guests": self.guests,
            "is_video": self.is_video,
        }
        return {key: value for key, value in ret.items() if value}

    def to_query(self) -> Dict[str, List[Dict[str, Any]]]:
        ret = []
        for key, condition in self.to_dict().items():
            ret.append({key.replace("program_", ""): condition})
        return {"$and": ret}


class ProgramQueryList:
    def __init__(self, queries: List[ProgramQuery]) -> None:
        self._queries = queries

    def to_dict(self) -> List[Dict[str, Any]]:
        return [query.to_dict() for query in self._queries]

    def to_query(self) -> Dict[str, Dict[str, Any]]:
        return {"$or": [query.to_query() for query in self._queries]}

    def to_json(self, filename: str) -> None:
        with open(filename, "w") as fh:
            json.dump(self.to_dict(), fh, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, filename: str) -> "ProgramQueryList":
        with open(filename, "r") as fh:
            queries = json.load(fh)
        return cls([ProgramQuery.from_dict(query) for query in queries])
