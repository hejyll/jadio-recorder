from __future__ import annotations

from typing import Optional

import pymongo
import pymongo.collation
import pymongo.database


class JadioDatabase:
    def __init__(
        self,
        host: Optional[str] = None,
        name: str = "jadio",
    ) -> None:
        host = host or "mongodb://localhost:27017/"
        self._client = pymongo.MongoClient(host)
        self._name = name

    def __enter__(self) -> JadioDatabase:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    @property
    def _database(self) -> pymongo.database.Database:
        return self._client.get_database(self._name)

    @property
    def record_configs(self) -> pymongo.collation.Collation:
        return self._database.get_collection("record_configs")

    @property
    def feed_configs(self) -> pymongo.collation.Collation:
        return self._database.get_collection("feed_configs")

    @property
    def fetched_programs(self) -> pymongo.collation.Collation:
        return self._database.get_collection("fetched_programs")

    @property
    def reserved_programs(self) -> pymongo.collation.Collation:
        return self._database.get_collection("reserved_programs")

    @property
    def recorded_programs(self) -> pymongo.collation.Collation:
        return self._database.get_collection("recorded_programs")

    @property
    def stations(self) -> pymongo.collation.Collation:
        return self._database.get_collection("stations")

    @property
    def timestamp(self) -> pymongo.collation.Collation:
        return self._database.get_collection("timestamp")
