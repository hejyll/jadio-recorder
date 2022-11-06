from typing import List

from jpradio_recorder import ProgramQueryList, RecordedProgram, Recorder


def record(
    media_root: str,
    queries_path: str,
) -> List[RecordedProgram]:
    queries = ProgramQueryList.from_json(queries_path)
    with Recorder(media_root=media_root) as recorder:
        recorder.fetch_programs()
        recorder.reserve_programs(queries)
        programs = recorder.record_programs()
    return programs


def report(programs: List[RecordedProgram]) -> None:
    ...
