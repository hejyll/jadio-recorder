import argparse
import json
import logging
from pathlib import Path

from .handlers import Feeder, Recorder
from .program_group import ProgramGroup

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s: %(message)s"
)


def add_argument_common(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--db-host",
        type=str,
        default="mongodb://localhost:27017/",
        help="MongoDB host",
    )


def add_argument_record_program_group(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=record_program_group)
    parser.add_argument(
        "config_path", type=Path, help="Record program group config file path (JSON)"
    )


def add_argument_feed_program_group(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=feed_program_group)
    parser.add_argument(
        "config_path", type=Path, help="Feed program group config file path (JSON)"
    )


def add_argument_record_programs(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=record_programs)
    parser.add_argument(
        "--force-fetch", action="store_true", help="Force fetch programs from services"
    )
    parser.add_argument(
        "--service-config-path",
        type=Path,
        # TODO: fix default path
        default="./svr/jadio-recorder/config.json",
        help="Radio service config Json file path",
    )
    parser.add_argument(
        "--media-root", type=Path, default="./media", help="Media root directory"
    )


def add_argument_feed_rss(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=feed_rss)
    parser.add_argument(
        "--rss-root", type=Path, default="./rss", help="RSS root directory"
    )
    parser.add_argument(
        "--media-root", type=Path, default="./media", help="Media root directory"
    )
    parser.add_argument(
        "--http-host",
        type=str,
        default="http://localhost",
        help="HTTP host for RSS feed",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    commands = [
        (
            "reserve",
            add_argument_record_program_group,
            "Reserve radio program recordings.",
        ),
        (
            "record",
            add_argument_record_programs,
            "Record reserved radio programs.",
        ),
        (
            "group",
            add_argument_feed_program_group,
            "Group recorded radio programs to compose Podcast RSS feeds.",
        ),
        (
            "feed",
            add_argument_feed_rss,
            "Create Podcast RSS feeds of recorded radio programs.",
        ),
    ]
    for name, add_arument_fn, help in commands:
        sub_parser = subparsers.add_parser(name, help=help)
        add_arument_fn(sub_parser)
        add_argument_common(sub_parser)

    return parser


def record_program_group(args: argparse.Namespace) -> None:
    with open(args.config_path, "r") as fh:
        data = fh.read()
        try:
            program_groups = ProgramGroup.schema().loads(data, many=True)
        except:
            program_groups = [ProgramGroup.from_json(data)]

    with Recorder(db_host=args.db_host) as handler:
        for program_group in program_groups:
            handler.insert_program_group(program_group)


def feed_program_group(args: argparse.Namespace) -> None:
    with open(args.config_path, "r") as fh:
        data = fh.read()
        try:
            program_groups = ProgramGroup.schema().loads(data, many=True)
        except:
            program_groups = [ProgramGroup.from_json(data)]

    with Feeder(db_host=args.db_host) as handler:
        for program_group in program_groups:
            handler.insert_program_group(program_group)


def record_programs(args: argparse.Namespace) -> None:
    with open(args.service_config_path, "r") as fh:
        service_config = json.load(fh)

    with Recorder(
        service_config=service_config,
        media_root=args.media_root,
        db_host=args.db_host,
    ) as handler:
        handler.fetch_programs(force=args.force_fetch)
        handler.search_programs()
        handler.record_programs()


def feed_rss(args: argparse.Namespace) -> None:
    with Feeder(
        rss_root=args.rss_root,
        media_root=args.media_root,
        http_host=args.http_host,
        db_host=args.db_host,
    ) as handler:
        handler.feed_rss()


def main():
    parser = parse_args()
    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
