import datetime
import os
from typing import Dict, List

from jpradio import Hibiki, Onsen, Program, Radiko, Station
from jpradio.platforms.base import Platform
from jpradio.util import load_config

from .database import Database
from .documents import RecordedProgram, ReservationConditions
from .util import fix_to_path


class Recorder:
    def __init__(self, media_root: str = ".") -> None:
        self._media_root = media_root

        config = load_config()
        self._platforms: Dict[str, Platform] = {
            Radiko.id: Radiko(**config.get(Radiko.id, {})),
            Onsen.id: Onsen(**config.get(Onsen.id, {})),
            Hibiki.id: Hibiki(**config.get(Hibiki.id, {})),
        }
        self._database = Database()

    @property
    def db(self) -> Database:
        return self._database

    def __enter__(self) -> "Recorder":
        for platform in self._platforms.values():
            platform.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        for platform in self._platforms.values():
            platform.close()
        self.db.close()

    def reset_fetched_programs(self) -> None:
        self.db.fetched_programs.delete_many({})

    def reset_reserved_programs(self) -> None:
        self.db.reserved_programs.delete_many({})

    def reset_recorded_programs(self) -> None:
        self.db.recorded_programs.delete_many({})

    def reset_timestamp(self) -> None:
        self.db.timestamp.delete_many({})

    def fetch_stations(self) -> None:
        stations = sum([p.get_stations() for p in self._platforms.values()], [])
        self.db.stations.delete_many({})
        self.db.stations.insert_many([s.to_dict() for s in stations])

    def get_stations(self) -> List[Station]:
        ret = [Station.from_dict(s) for s in self.db.stations.find({})]
        if not ret:
            self.fetch_stations()
            return self.get_stations()
        return ret

    def fetch_programs(self, force: bool = False, interval_days: int = 1) -> None:
        timestamp_name = "fetch"
        timestamp = self.db.timestamp.find_one({"name": timestamp_name})
        timestamp = timestamp["datetime"]
        now = datetime.datetime.now()
        if not force and timestamp + datetime.timedelta(days=interval_days) > now:
            return

        programs = sum([p.get_programs() for p in self._platforms.values()], [])
        self.db.fetched_programs.insert_many([p.to_dict() for p in programs])
        self.db.timestamp.insert_one({"name": timestamp_name, "datetime": now})

    def reserve_programs(
        self, conditions: List[ReservationConditions]
    ) -> List[Program]:
        query = {"$or": [c.to_query() for c in conditions]}
        ret = []
        for program in self.db.fetched_programs.find(query):
            program.pop("_id")
            res = self.db.reserved_programs.find_one(program)
            if not res:
                res = self.db.recorded_programs.find_one(program)
                if not res:
                    ret.append(Program.from_dict(program))
                    self.db.reserved_programs.insert_one(program)
        return ret

    def record_programs(self) -> List[RecordedProgram]:
        station_id_platform_map = {
            station.id: self._platforms[station.platform_id]
            for station in self.get_stations()
        }

        # Only programs that have completed broadcasting can be downloaded.
        date_condition = ReservationConditions(
            datetime={"$lt": datetime.datetime.now() - datetime.timedelta(hours=2)},
        )
        target_programs = self.db.reserved_programs.find(date_condition.to_query())

        ret = []
        for program in target_programs:
            target_id = program.pop("_id")
            res = self.db.recorded_programs.find_one(program)
            if not res:
                program = Program.from_dict(program)
                platform = station_id_platform_map[program.station_id]
                filename = platform.get_default_filename(program)
                filename = os.path.join(
                    self._media_root,
                    platform.id,
                    program.station_id,
                    fix_to_path(program.name),
                    filename,
                )
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                try:
                    platform.download(program, filename)
                    recorded = RecordedProgram.from_dict(
                        {
                            **program.to_dict(),
                            "filename": filename,
                            "recorded_datetime": datetime.datetime.now(),
                        }
                    )
                    ret.append(recorded)
                    self.db.recorded_programs.insert_one(recorded.to_dict())
                except Exception:
                    pass
            self.db.reserved_programs.delete_one({"_id": target_id})
        return ret
