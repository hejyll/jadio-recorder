import argparse
import json
import logging

from jpradio_recorder import ProgramQueryList, entrypoints

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--queries-path",
        type=str,
        default="/data/jpradio-recorder/queries.json",
        help="Queries Json file path",
    )
    parser.add_argument(
        "--media-root", type=str, default="/data/media", help="Media root directory"
    )
    parser.add_argument(
        "--platform-config-path",
        type=str,
        default="/data/jpradio-recorder/config.json",
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
    args = parse_args()

    with open(args.platform_config_path, "r") as fh:
        platform_config = json.load(fh)

    entrypoints.record(
        ProgramQueryList.from_json(args.queries_path),
        media_root=args.media_root,
        platform_config=platform_config,
        database_host=args.database_host,
    )


if __name__ == "__main__":
    main()
