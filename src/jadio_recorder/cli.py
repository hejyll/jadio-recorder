import argparse
import json
import logging

from jadio_recorder.query import ProgramQuery
from jadio_recorder.recorder import Recorder

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s: %(message)s"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--queries-path",
        type=str,
        default="./svr/jadio-recorder/queries.json",
        help="Queries Json file path",
    )
    parser.add_argument(
        "--media-root", type=str, default="./media", help="Media root directory"
    )
    parser.add_argument(
        "--service-config-path",
        type=str,
        default="./svr/jadio-recorder/config.json",
        help="Radio service config Json file path",
    )
    parser.add_argument(
        "--database-host",
        type=str,
        default="mongodb://localhost:27017/",
        help="MongoDB host",
    )
    parser.add_argument(
        "--force-fetch",
        action="store_true",
        help="Force fetch programs from services",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    with open(args.service_config_path, "r") as fh:
        service_config = json.load(fh)
    with open(args.queries_path, "r") as fh:
        data = fh.read()
        queries = ProgramQuery.schema().loads(data, many=True)

    with Recorder(
        media_root=args.media_root,
        service_config=service_config,
        database_host=args.database_host,
    ) as recorder:
        recorder.fetch_programs(force=args.force_fetch)
        recorder.reserve_programs(queries)
        recorder.record_programs()


if __name__ == "__main__":
    main()
