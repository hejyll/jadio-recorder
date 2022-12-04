from typing import Optional

import pymongo
import pymongo.collation
import pymongo.database


class Database:
    def __init__(self, host: Optional[str] = None) -> None:
        host = host or "mongodb://localhost:27017/"
        self._client = pymongo.MongoClient(host)

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    @property
    def _database(self) -> pymongo.database.Database:
        return self._client.get_database("recorder")

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
