import pymongo
import pymongo.collation
import pymongo.database


class Recorder:
    def __init__(self) -> None:
        self._client = pymongo.MongoClient("mongodb://localhost:27017/")

    def __enter__(self) -> "Recorder":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._client.close()

    @property
    def database(self) -> pymongo.database.Database:
        return self._client.get_database("recorder")

    @property
    def fetched_programs_collection(self) -> pymongo.collation.Collation:
        return self.database.get_collection("fetched_programs")

    @property
    def reserved_programs_collection(self) -> pymongo.collation.Collation:
        return self.database.get_collection("reserved_programs")

    @property
    def recorded_programs_collection(self) -> pymongo.collation.Collation:
        return self.database.get_collection("recorded_programs")
