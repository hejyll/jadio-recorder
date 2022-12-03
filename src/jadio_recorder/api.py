import argparse
import datetime
from typing import Any, Dict

from flask import Flask, jsonify

from jadio import Program

# from .database import Database
from jadio_recorder.database import Database


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

__args: argparse.Namespace


def _fix_db_data(data: Dict[str, Any]) -> Dict[str, Any]:
    data.pop("_id", None)
    data.pop("raw_data", None)
    for key, value in data.items():
        if isinstance(value, datetime.datetime):
            data[key] = value.strftime("%Y-%m-%d %H:%M")
    return data


@app.route("/fetched")
def fetched():
    with Database(host=__args.database_host) as db:
        programs = db.fetched_programs.find({})
        ret = [_fix_db_data(program) for program in programs[:10]]
    return jsonify(ret)


@app.route("/reserved")
def reserved():
    with Database(host=__args.database_host) as db:
        programs = db.reserved_programs.find({})
        ret = [_fix_db_data(program) for program in programs[:10]]
    return jsonify(ret)


@app.route("/recorded")
def recorded():
    with Database(host=__args.database_host) as db:
        programs = db.recorded_programs.find({})
        ret = [_fix_db_data(program) for program in programs[:10]]
    return jsonify(ret)


@app.route("/timestamp")
def timestamp():
    with Database(host=__args.database_host) as db:
        timestamps = db.timestamp.find({})
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

