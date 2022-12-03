import datetime
import logging
import os
from typing import Any, Dict, List, Optional

import tqdm
from jpradio import Jpradio, Program, ProgramQuery, ProgramQueryList, Station

from .database import Database
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


class Recorder:
    def __init__(
        self,
        media_root: str = ".",
        platform_config: Dict[str, str] = {},
        database_host: Optional[str] = None,
    ) -> None:
        self._media_root = media_root

        self._platform = Jpradio(platform_config)
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
        self._platform.login()

    def close(self) -> None:
        self._platform.close()
        self.db.close()

    def _update_timestamp(self, name: str) -> None:
        timestamp = datetime.datetime.now()
        self.db.timestamp.update_one(
            {"name": name}, {"$set": {"datetime": timestamp}}, upsert=True
        )

    def fetch_stations(self) -> None:
        stations = self._platform.get_stations()
        self.db.stations.delete_many({})
        self.db.stations.insert_many([s.to_dict() for s in stations])
        self._update_timestamp("fetch_stations")

    def get_stations(self) -> List[Station]:
        ret = [Station.from_dict(s) for s in self.db.stations.find({})]
        if not ret:
            self.fetch_stations()
            return self.get_stations()
        return ret

    def fetch_programs(self, force: bool = False, interval_days: int = 1) -> None:
        timestamp = self.db.timestamp.find_one({"name": "fetch_programs"})
        if not timestamp:
            force = True
        else:
            timestamp = timestamp["datetime"]
        now = datetime.datetime.now()
        if not force and timestamp + datetime.timedelta(days=interval_days) > now:
            return

        logger.info("Start fetching programs")
        programs = self._platform.get_programs()
        self.db.fetched_programs.delete_many({})
        self.db.fetched_programs.insert_many([p.to_dict() for p in programs])
        self._update_timestamp("fetch_programs")
        logger.info(f"Finish fetching {len(programs)} programs")

    def reserve_programs(self, queries: ProgramQueryList) -> List[Program]:
        logger.info("Start reserving programs")
        self.db.reserved_programs.delete_many({})
        query = queries.to_query()
        ret: List[Program] = []
        for program in self.db.fetched_programs.find(query):
            program.pop("_id")
            find_keys = [
                "id",
                "station_id",
                "name",
                "episode_id",
                "episode_name",
                "ascii_name",
            ]
            find_query = {key: program[key] for key in find_keys}
            if not self.db.reserved_programs.find_one(find_query):
                if not self.db.recorded_programs.find_one(find_query):
                    ret.append(Program.from_dict(program))
                    self.db.reserved_programs.insert_one(program)
        self._update_timestamp("reserve_programs")
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
                    self._platform.id(program),
                    program.station_id,
                    fix_to_path(program.name),
                    self._platform.get_default_filename(program),
                )
                # if os.path.exists(filename):
                #     # TODO: remove duplicated programs from reserved_programs
                #     continue
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                try:
                    self._platform.download(program, filename)
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
        self._update_timestamp("record_programs")
        logger.info(f"Finish recording {len(ret)} program(s)")
        return ret
