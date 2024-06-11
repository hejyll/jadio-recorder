from dataclasses import dataclass
from typing import Optional, Union

from dataclasses_json import DataClassJsonMixin

from .podcast import PodcastChannel
from .query import ProgramQuery


@dataclass
class RecordConfig(DataClassJsonMixin):
    query: ProgramQuery
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True


@dataclass
class FeedConfig(DataClassJsonMixin):
    query: ProgramQuery
    channel: Optional[PodcastChannel] = None
    enabled: bool = True

    @property
    def name(self) -> Union[str, None]:
        return self.channel.title if self.channel else None

    @property
    def description(self) -> Union[str, None]:
        return self.channel.description if self.channel else None
