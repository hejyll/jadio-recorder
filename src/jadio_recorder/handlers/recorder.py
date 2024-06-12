from __future__ import annotations

import datetime
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

import tqdm
from jadio import Jadio, Program

from ..program_group import ProgramGroup
from ..program_query import ProgramQuery, queries_to_mongo_format
from .base import DatabaseHandler

logger = logging.getLogger(__name__)


class Recorder(DatabaseHandler):
    def __init__(
        self,
        service_config: Dict[str, str] = {},
        media_root: Union[str, Path] = ".",
        db_host: Optional[str] = None,
        db_name: str = "jadio",
    ) -> None:
        super().__init__(db_host, db_name)
        self._media_root = Path(media_root)
        self._media_root.mkdir(parents=True, exist_ok=True)
        self._service = Jadio(service_config)

    def login(self) -> None:
        self._service.login()

    def close(self) -> None:
        super().close()
        self._service.close()

    def insert_program_group(
        self,
        program_group: ProgramGroup,
        enable_feed: bool = True,
    ) -> None:
        logger.info("Start: insert_program_group")

        program_group.enable_record = True
        program_group.enable_feed = enable_feed

        program_group = program_group.to_dict()
        if self.db.program_groups.find_one(
            {"query": program_group["query"], "enable_record": True}
        ):
            logger.info("There is already a program group for the same query.")
        self.db.program_groups.update_one(
            program_group, {"$set": program_group}, upsert=True
        )

        self._update_timestamp("insert_program_group")
        logger.info("Finish: insert_program_group")

    def fetch_programs(self, force: bool = False, interval_days: int = 1) -> None:
        logger.info("Start: fetch_programs")

        timestamp = self.db.timestamp.find_one({"name": "fetch_programs"})
        if not timestamp:
            force = True
        else:
            timestamp = timestamp["timestamp"]
        now = datetime.datetime.now()
        if not force and timestamp + datetime.timedelta(days=interval_days) > now:
            logger.info("Skipped: fetch_programs")
            return

        programs = self._service.get_programs()
        self.db.fetched_programs.delete_many({})
        self.db.fetched_programs.insert_many([p.to_dict() for p in programs])

        self._update_timestamp("fetch_programs")
        logger.info(f"Finish: fetch_programs: {len(programs)} programs")

    def search_programs(self) -> List[Program]:
        logger.info("Start: search_programs")

        self.db.reserved_programs.delete_many({})
        program_groups = list(self.db.program_groups.find({"enable_record": True}))
        if len(program_groups) == 0:
            return []
        program_groups = [
            ProgramGroup.from_dict(program_group) for program_group in program_groups
        ]
        query = queries_to_mongo_format(
            [program_group.query for program_group in program_groups]
        )
        ret: List[Program] = []
        for program in self.db.fetched_programs.find(query):
            program.pop("_id")
            find_keys = [
                "service_id",
                "station_id",
                "program_id",
                "episode_id",
                "program_title",
                "episode_title",
            ]
            find_query = {key: program[key] for key in find_keys}
            if not self.db.reserved_programs.find_one(find_query):
                if not self.db.recorded_programs.find_one(find_query):
                    ret.append(Program.from_dict(program))
                    self.db.reserved_programs.insert_one(program)

        self._update_timestamp("search_programs")
        logger.info(f"Finish: search_programs: {len(ret)} program(s)")
        return ret

    def record_programs(self) -> List[Program]:
        logger.info("Start: record_programs")

        # Only programs that have completed broadcasting can be downloaded.
        lt_date = datetime.datetime.now() - datetime.timedelta(hours=2)
        date_query = ProgramQuery(pub_date=[None, lt_date])
        target_programs = self.db.reserved_programs.find(date_query.to_mongo_format())

        ret = []
        for program in tqdm.tqdm(list(target_programs)):
            target_id = program.pop("_id")
            if not self.db.recorded_programs.find_one(program):
                program = Program.from_dict(program)
                ext = Path(self._service._get_default_file_path(program)).suffix
                inserted_id = None
                try:
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        # download (record) media file to temporary dir
                        tmp_media_path = Path(tmp_dir) / f"media{ext}"
                        self._service.download(program, str(tmp_media_path))

                        # insert recorded program to db
                        result = self.db.recorded_programs.insert_one(program.to_dict())
                        inserted_id = result.inserted_id

                        # move downloaded media file to specified media root
                        save_root = self._media_root.joinpath(
                            program.service_id, program.program_id, str(inserted_id)
                        )
                        save_root.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(tmp_media_path), str(save_root / f"media{ext}"))

                        # save program information as JSON file
                        with open(str(save_root / f"program.json"), "w") as fh:
                            fh.write(program.to_json(indent=2, ensure_ascii=False))

                        logger.debug(f"Save media and program file to {save_root}")
                        ret.append(program)
                except Exception as err:
                    if inserted_id:
                        self.db.recorded_programs.delete_one({"_id": inserted_id})
                    logger.error(f"error: {err}\n{program}", stack_info=True)
            self.db.reserved_programs.delete_one({"_id": target_id})

        self._update_timestamp("record_programs")
        logger.info(f"Finish: record_programs: {len(ret)} program(s)")
        return ret
