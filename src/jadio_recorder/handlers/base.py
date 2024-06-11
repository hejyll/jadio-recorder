from __future__ import annotations

import abc
import datetime
import logging
from typing import Optional

from ..database import JadioDatabase

logger = logging.getLogger(__name__)


class DatabaseHandler(abc.ABC):
    def __init__(
        self,
        db_host: Optional[str] = None,
        db_name: str = "jadio",
    ) -> None:
        self._database = JadioDatabase(db_host, name=db_name)

    @property
    def db(self) -> JadioDatabase:
        return self._database

    def __enter__(self) -> DatabaseHandler:
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def login(self) -> None: ...

    def close(self) -> None:
        self.db.close()

    def _update_timestamp(self, name: str) -> None:
        timestamp = datetime.datetime.now()
        self.db.timestamp.update_one(
            {"name": name}, {"$set": {"timestamp": timestamp}}, upsert=True
        )
