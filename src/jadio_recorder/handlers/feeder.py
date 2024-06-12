from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional, Union

import tqdm
from bson import ObjectId
from jadio import Program

from ..podcast import PodcastRssFeedGenCreator
from ..program_group import ProgramGroup
from .base import DatabaseHandler

logger = logging.getLogger(__name__)


class Feeder(DatabaseHandler):
    def __init__(
        self,
        rss_root: Union[str, Path] = ".",
        media_root: Union[str, Path] = ".",
        http_host: str = "http://localhost",
        db_host: Optional[str] = None,
        db_name: str = "jadio",
    ) -> None:
        super().__init__(db_host, db_name)
        self._rss_root = Path(rss_root)
        self._rss_root.mkdir(parents=True, exist_ok=True)
        self._media_root = Path(media_root)
        self._http_host = http_host

    def insert_program_group(self, program_group: ProgramGroup) -> None:
        logger.info("Start: insert_program_group")

        program_group.enable_feed = True

        program_group = program_group.to_dict()
        if self.db.program_groups.find_one(
            {"query": program_group["query"], "enable_feed": True}
        ):
            logger.warn("There is already a program group for the same query.")
        self.db.program_groups.update_one(
            program_group, {"$set": program_group}, upsert=True
        )

        self._update_timestamp("insert_program_group")
        logger.info("Finish: insert_program_group")

    def _feed_rss(
        self,
        program_group: ProgramGroup,
        object_id: Union[str, ObjectId],
        pretty: bool = True,
    ) -> None:
        # fetch specified recorded programs
        logger.debug(f"Feed RSS: {program_group}")
        programs = self.db.recorded_programs.find(program_group.query.to_mongo_format())
        program_and_id_pairs = [
            (Program.from_dict(program), program["_id"]) for program in programs
        ]
        if len(program_and_id_pairs) == 0:
            logger.debug("Find no programs. RSS feed is not created")
            return
        logger.debug(f"Fetch {len(program_and_id_pairs)} program(s)")

        # create FeedGenerator
        feed_generator = PodcastRssFeedGenCreator(
            self._http_host, self._media_root
        ).create(program_group, program_and_id_pairs, remove_duplicates=True)

        # save RSS feed file
        rss_feed_path = self._rss_root / f"{str(object_id)}.xml"
        rss_feed_path.parent.mkdir(exist_ok=True)
        feed_generator.rss_file(rss_feed_path, pretty=pretty)
        logger.debug(f"Save RSS feed to {rss_feed_path}")

    def feed_rss(self, force: bool = False) -> List[ProgramGroup]:
        logger.info("Start: feed_rss")

        last_timestamp = self.db.timestamp.find_one({"name": "feed_rss"})
        if last_timestamp:
            last_timestamp = last_timestamp["timestamp"]

        program_groups = list(self.db.program_groups.find({"enable_feed": True}))
        ret = []
        for program_group in tqdm.tqdm(program_groups):
            object_id = program_group.pop("_id")
            program_group = ProgramGroup.from_dict(program_group)
            if (
                isinstance(program_group.query.pub_date, list)
                and program_group.query.pub_date[1]
            ):
                last_datetime = program_group.query.pub_date[1]
                if (
                    last_datetime < (last_timestamp or last_datetime)
                    and not force
                    and (self._rss_root / f"{str(object_id)}.xml").exists()
                ):
                    logger.debug(
                        f"Skip: feed the RSS of completed channels: {str(object_id)}"
                    )
                    continue
            try:
                self._feed_rss(program_group, object_id)
                ret.append(program_group)
            except Exception as err:
                logger.error(f"Error: {err}\n{program_group}", stack_info=True)
                raise err

        self._update_timestamp("feed_rss")
        logger.info(f"Finis: feed_rss: {len(ret)} feeds")
        return ret
