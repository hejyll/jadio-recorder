import argparse
import datetime
from enum import Enum
from typing import Any, Dict

from flask import Flask, jsonify, request

# from .database import Database
from jadio_recorder.database import Database

DEFAULT_ITEMS_PER_PAGE = 20


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

__args: argparse.Namespace


class ProgramStatus(Enum):
    FETCHED = "fetched"
    RESERVED = "reserved"
    RECORDED = "recorded"


def _fix_db_data(data: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in data.items():
        if isinstance(value, datetime.datetime):
            data[key] = value.strftime("%Y-%m-%d %H:%M")
    return data


@app.route("/stations", methods=["GET"])
def stations():
    with Database(host=__args.database_host) as db:
        stations = list(db.stations.find({}, projection={"_id": False}))
    return jsonify(stations)


@app.route("/programs", methods=["GET"])
def programs():
    # parse query parameters
    args = request.args
    page = args.get("page", default=0, type=int)
    items = args.get("items", default=DEFAULT_ITEMS_PER_PAGE, type=int)
    status = args.get("status", default=ProgramStatus.RECORDED.value, type=str)
    status = ProgramStatus(status)

    # construct arguments for Mongo find
    sort_key = "recorded_datetime" if status == ProgramStatus.RECORDED else "datetime"
    find_args = dict(
        filter={},
        projection={"_id": False, "raw_data": False},
        sort=[(sort_key, -1)],
        skip=items * page,
        limit=items,
    )

    # pickup programs
    programs = []
    with Database(host=__args.database_host) as db:
        if status == ProgramStatus.FETCHED:
            programs += db.fetched_programs.find(**find_args)
            for program in programs:
                find_filter = {
                    "station_id": program["station_id"],
                    "episode_id": program["episode_id"],
                }
                if db.recorded_programs.find_one(find_filter):
                    program["status"] = ProgramStatus.RECORDED.value
                elif db.reserved_programs.find_one(find_filter):
                    program["status"] = ProgramStatus.RESERVED.value
                else:
                    program["status"] = ProgramStatus.FETCHED.value
        elif status == ProgramStatus.RESERVED:
            programs += db.reserved_programs.find(**find_args)
            for program in programs:
                program["status"] = ProgramStatus.RESERVED.value
        elif status == ProgramStatus.RECORDED:
            programs += db.recorded_programs.find(**find_args)
            for program in programs:
                program["status"] = ProgramStatus.RECORDED.value
    programs = [_fix_db_data(program) for program in programs]
    return jsonify(programs)


@app.route("/timestamp", methods=["GET"])
def timestamp():
    with Database(host=__args.database_host) as db:
        timestamps = db.timestamp.find({}, projection={"_id": False})
        ret = [_fix_db_data(timestamp) for timestamp in timestamps[:10]]
    return jsonify(ret)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--app-host",
        type=str,
        default=None,
        help="App host",
    )
    parser.add_argument(
        "--app-port",
        type=int,
        default=5000,
        help="App port number",
    )
    parser.add_argument(
        "--media-root", type=str, default="/data/media", help="Media root directory"
    )
    parser.add_argument(
        "--platform-config-path",
        type=str,
        default="/data/jadio-recorder/config.json",
        help="Radio platform config Json file path",
    )
    parser.add_argument(
        "--database-host",
        type=str,
        default="mongodb://localhost:27017/",
        help="MongoDB host",
    )
    args = parser.parse_args()
    return args


def main():
    global __args
    __args = parse_args()
    app.run(host=__args.app_host, port=__args.app_port)


if __name__ == "__main__":
    main()
