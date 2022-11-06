from typing import List, Optional

from .query import ProgramQueryList
from .recorder import RecordedProgram, Recorder


def record(
    queries_path: str,
    media_root: Optional[str] = None,
    platform_config_path: Optional[str] = None,
    database_host: Optional[str] = None,
) -> List[RecordedProgram]:
    queries = ProgramQueryList.from_json(queries_path)
    with Recorder(
        media_root=media_root,
        platform_config_path=platform_config_path,
        database_host=database_host,
    ) as recorder:
        recorder.fetch_programs()
        recorder.reserve_programs(queries)
        programs = recorder.record_programs()
    return programs


def report(programs: List[RecordedProgram]) -> None:
    ...
