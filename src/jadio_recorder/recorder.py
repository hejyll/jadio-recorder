from __future__ import annotations

import datetime
import json
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

import tqdm
from jadio import Jadio, Program, ProgramQuery, ProgramQueryList, Station

from .database import RecorderDatabase as Database

logger = logging.getLogger(__name__)


class Recorder:
    def __init__(
        self,
        media_root: Union[str, Path] = ".",
        platform_config: Dict[str, str] = {},
        database_host: Optional[str] = None,
    ) -> None:
        self._media_root = Path(media_root)
        self._media_root.mkdir(exist_ok=True)

        self._platform = Jadio(platform_config)
        self._database = Database(database_host)

    @property
    def db(self) -> Database:
        return self._database

    def __enter__(self) -> Recorder:
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

    def record_programs(self) -> List[Program]:
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
                ext = Path(self._platform.get_default_filename(program)).suffix
                inserted_id = None
                try:
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        # download (record) media file to temporary dir
                        tmp_media_path = Path(tmp_dir) / f"media{ext}"
                        self._platform.download(program, str(tmp_media_path))

                        # insert recorded program to db
                        result = self.db.recorded_programs.insert_one(program.to_dict())
                        inserted_id = result.inserted_id

                        # move downloaded media file to specified media root
                        save_root = self._media_root.joinpath(
                            program.platform_id, program.station_id, str(inserted_id)
                        )
                        save_root.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(tmp_media_path), str(save_root / f"media{ext}"))

                        # save program information as JSON file
                        with open(str(save_root / f"program.json"), "w") as fh:
                            data = program.to_dict(serialize=True)
                            json.dump(data, fh, indent=2, ensure_ascii=False)

                        logger.info(f"Save media and program file to {save_root}")
                        ret.append(program)
                except Exception as err:
                    if inserted_id:
                        self.db.recorded_programs.delete_one({"_id": inserted_id})
                    logger.error(f"error: {err}\n{program}", stack_info=True)
            self.db.reserved_programs.delete_one({"_id": target_id})
        self._update_timestamp("record_programs")
        logger.info(f"Finish recording {len(ret)} program(s)")
        return ret
