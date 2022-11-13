import datetime
import logging
import os
from typing import Any, Dict, List, Optional

import tqdm
from jpradio import Hibiki, Onsen, Program, Radiko, Station
from jpradio.platforms.base import Platform

from .database import Database
from .query import ProgramQuery, ProgramQueryList
from .util import fix_to_path

logger = logging.getLogger(__name__)


class RecordedProgram(Program):
    filename: Optional[str] = None
    recorded_datetime: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        ret = super().to_dict()
        return {
            **ret,
            "filename": self.filename,
            "recorded_datetime": self.recorded_datetime,
        }


def _get_all_platforms_cls() -> List[Platform]:
    return [Radiko, Onsen, Hibiki]


class RadioPlatforms(Platform):
    def __init__(self, configs: Dict[str, Any]) -> None:
        super().__init__()
        all_platform_cls = _get_all_platforms_cls()
        self._platforms = {
            cls.id: cls(**configs.get(cls.id, {})) for cls in all_platform_cls
        }
        self._station_id_platform_map = {
            station.id: self._platforms[station.platform_id]
            for station in self.get_stations()
        }

    def id(self, program: Program) -> str:
        return self.get_platform(program).id

    def name(self, program: Program) -> str:
        return self.get_platform(program).name

    def ascii_name(self, program: Program) -> str:
        return self.get_platform(program).ascii_name

    def url(self, program: Program) -> str:
        return self.get_platform(program).url

    def login(self) -> None:
        for platform in self._platforms.values():
            platform.login()

    def close(self) -> None:
        for platform in self._platforms.values():
            platform.close()

    def get_platform(self, program: Program) -> Platform:
        return self._station_id_platform_map[program.station_id]

    def get_stations(self) -> List[Station]:
        return sum([p.get_stations() for p in self._platforms.values()], [])

    def get_programs(
        self, filters: Optional[List[str]] = None, **kwargs
    ) -> List[Program]:
        return sum([p.get_programs(filters) for p in self._platforms.values()], [])

    def download_media(self, program: Program, filename: str) -> None:
        self.get_platform(program).download_media(program, filename)

    def get_default_filename(self, program: Program) -> str:
        return self.get_platform(program).get_default_filename(program)


class Recorder:
    def __init__(
        self,
        media_root: str = ".",
        platform_config: Dict[str, str] = {},
        database_host: Optional[str] = None,
    ) -> None:
        self._media_root = media_root

        self._platforms = RadioPlatforms(platform_config)
        self._database = Database(database_host)

    @property
    def db(self) -> Database:
        return self._database

    def __enter__(self) -> "Recorder":
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def login(self) -> None:
        self._platforms.login()

    def close(self) -> None:
        self._platforms.close()
        self.db.close()

    def fetch_stations(self) -> None:
        stations = self._platforms.get_stations()
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
        if not timestamp:
            force = True
        else:
            timestamp = timestamp["datetime"]
        now = datetime.datetime.now()
        if not force and timestamp + datetime.timedelta(days=interval_days) > now:
            return

        logger.info("Start fetching programs")
        programs = self._platforms.get_programs()
        logger.info(f"Finish fetching {len(programs)} programs")
        self.db.reset_fetched_programs()
        self.db.fetched_programs.insert_many([p.to_dict() for p in programs])
        self.db.timestamp.insert_one({"name": timestamp_name, "datetime": now})

    def reserve_programs(self, queries: ProgramQueryList) -> List[Program]:
        logger.info("Start reserving programs")
        query = queries.to_query()
        ret: List[Program] = []
        for program in self.db.fetched_programs.find(query):
            program.pop("_id")
            if not self.db.reserved_programs.find_one(program):
                if not self.db.recorded_programs.find_one(program):
                    ret.append(Program.from_dict(program))
                    self.db.reserved_programs.insert_one(program)
        logger.info(f"Finish reserving {len(ret)} program(s)")
        return ret

    def record_programs(self) -> List[RecordedProgram]:
        logger.info("Start recording programs")

        # Only programs that have completed broadcasting can be downloaded.
        date_query = ProgramQuery(
            datetime={"$lt": datetime.datetime.now() - datetime.timedelta(hours=2)},
        )
        target_programs = self.db.reserved_programs.find(date_query.to_query())

        ret = []
        for program in tqdm.tqdm(list(target_programs)):
            target_id = program.pop("_id")
            if not self.db.recorded_programs.find_one(program):
                program = Program.from_dict(program)
                filename = os.path.join(
                    self._media_root,
                    self._platforms.id(program),
                    program.station_id,
                    fix_to_path(program.name),
                    self._platforms.get_default_filename(program),
                )
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                try:
                    self._platforms.download(program, filename)
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
        logger.info(f"Finish recording {len(ret)} program(s)")
        return ret
