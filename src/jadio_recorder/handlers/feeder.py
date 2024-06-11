from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional, Union

import tqdm
from bson import ObjectId
from jadio import Program

from ..configs import FeedConfig
from ..podcast import PodcastRssFeedGenCreator
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

    def insert_config(self, config: FeedConfig, overwrite: bool = False) -> None:
        config = config.to_dict()
        if self.db.feed_configs.find_one({"query": config["query"]}):
            if not overwrite:
                logger.info(
                    "skip inserting config because the same query already exists"
                )
                return
            else:
                logger.info("overwrite config because the same query already exists")
                self.db.feed_configs.delete_one({"query": config["query"]})
        self.db.feed_configs.update_one(config, {"$set": config}, upsert=True)
        self._update_timestamp("insert_config")
        logger.info("Finish inserting config")

    def update_feed(
        self,
        config: FeedConfig,
        config_id: Union[str, ObjectId],
        pretty: bool = True,
    ) -> None:
        # fetch specified recorded programs
        logger.debug(f"update RSS feed: {config}")
        query = config.query.to_mongo_format()
        programs = self.db.recorded_programs.find(query)
        program_and_id_pairs = [
            (Program.from_dict(program), program["_id"]) for program in programs
        ]
        if len(program_and_id_pairs) == 0:
            logger.info("find no programs. RSS feed is not created")
            return
        logger.info(f"fetch {len(program_and_id_pairs)} program(s)")

        # create FeedGenerator
        feed_generator = PodcastRssFeedGenCreator(
            self._http_host, self._media_root
        ).create(program_and_id_pairs, channel=config.channel, remove_duplicates=True)

        # save RSS feed file
        rss_feed_path = self._rss_root / f"{str(config_id)}.xml"
        rss_feed_path.parent.mkdir(exist_ok=True)
        feed_generator.rss_file(rss_feed_path, pretty=pretty)
        logger.info(f"save RSS feed to {rss_feed_path}")

    def update_feeds(self, force: bool = False) -> List[FeedConfig]:
        last_timestamp = self.db.timestamp.find_one({"name": "update_feeds"})
        if last_timestamp:
            last_timestamp = last_timestamp["datetime"]

        configs = list(self.db.feed_configs.find({}))
        ret = []
        for config in tqdm.tqdm(configs):
            config_id = config.pop("_id")
            config = FeedConfig.from_dict(config)
            if isinstance(config.query.pub_date, list) and config.query.pub_date[1]:
                last_datetime = config.query.pub_date[1]
                if (
                    last_datetime < (last_timestamp or last_datetime)
                    and not force
                    and (self._rss_root / f"{str(config_id)}.xml").exists()
                ):
                    logger.debug(
                        f"skip updates to RSS feed of completed channels: {config.query}"
                    )
                    continue
            try:
                self.update_feed(config, config_id)
                ret.append(config)
            except Exception as err:
                logger.error(f"error: {err}\n{config}", stack_info=True)

        self._update_timestamp("update_feeds")
        logger.info(f"Finish updating {len(ret)} feeds")
        return ret
