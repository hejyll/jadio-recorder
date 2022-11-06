import dataclasses
import json
from typing import Any, Dict, List, Optional, TypeVar, Union

T = TypeVar("T")
Condition = Optional[Union[T, Dict[str, T]]]


@dataclasses.dataclass
class ReservationConditions:
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
    def from_dict(cls, data: Dict[str, Any]) -> "ReservationConditions":
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
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

    def to_query(self) -> Dict[str, List[Dict[str, Any]]]:
        ret = []
        for key, condition in self.to_dict().items():
            if condition:
                ret.append({key.replace("program_", ""): condition})
        return {"$and": ret}


def load_reservation_conditions_file(filename: str) -> List[ReservationConditions]:
    with open(filename, "r") as fh:
        conditions = json.load(fh)
    return [ReservationConditions.from_dict(cond) for cond in conditions]
