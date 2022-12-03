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


def _fix_program(program: Dict[str, Any]) -> Dict[str, Any]:
    program.pop("_id")
    program.pop("raw_data")
    if isinstance(program["datetime"], datetime.datetime):
        program["datetime"] = program["datetime"].strftime("%Y-%m-%d %H:%M")
    return program


@app.route("/fetched")
def fetched():
    with Database(host=__args.database_host) as db:
        programs = db.fetched_programs.find({})
        ret = [_fix_program(program) for program in programs[:10]]
    return jsonify(ret)


@app.route("/reserved")
def reserved():
    with Database(host=__args.database_host) as db:
        programs = db.reserved_programs.find({})
        ret = [_fix_program(program) for program in programs[:10]]
    return jsonify(ret)


@app.route("/recorded")
def recorded():
    with Database(host=__args.database_host) as db:
        programs = db.recorded_programs.find({})
        ret = [_fix_program(program) for program in programs[:10]]
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

