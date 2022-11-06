from typing import Dict, List, Optional

from .query import ProgramQueryList
from .recorder import RecordedProgram, Recorder


def record(
    queries: ProgramQueryList,
    media_root: Optional[str] = None,
    platform_config: Dict[str, str] = {},
    database_host: Optional[str] = None,
) -> List[RecordedProgram]:
    with Recorder(
        media_root=media_root,
        platform_config=platform_config,
        database_host=database_host,
    ) as recorder:
        recorder.fetch_programs()
        recorder.reserve_programs(queries)
        programs = recorder.record_programs()
    return programs


def report(programs: List[RecordedProgram]) -> None:
    ...
