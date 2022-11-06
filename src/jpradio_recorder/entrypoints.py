from typing import List

from jpradio_recorder import RecordedProgram, Recorder
from jpradio_recorder.reservation_conditions import load_reservation_conditions


def record(
    media_root: str,
    conditions_path: str,
) -> List[RecordedProgram]:
    conditions = load_reservation_conditions(conditions_path)
    with Recorder(media_root=media_root) as recorder:
        recorder.fetch_programs()
        recorder.reserve_programs(conditions)
        programs = recorder.record_programs()
    return programs


def report(programs: List[RecordedProgram]) -> None:
    ...