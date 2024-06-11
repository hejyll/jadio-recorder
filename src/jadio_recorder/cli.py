import argparse
import json
import logging
from pathlib import Path

from .configs import FeedConfig, RecordConfig
from .handlers import Feeder, Recorder

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


def add_argument_insert_record_config(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=insert_record_config)
    parser.add_argument("config_path", type=Path, help="Record config file path (JSON)")


def add_argument_insert_feed_config(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=insert_feed_config)
    parser.add_argument("config_path", type=Path, help="Feed config file path (JSON)")


def add_argument_record_programs(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=record_programs)
    parser.add_argument(
        "--media-root", type=Path, default="./media", help="Media root directory"
    )
    parser.add_argument(
        "--force-fetch", action="store_true", help="Force fetch programs from services"
    )
    parser.add_argument(
        "--service-config-path",
        type=Path,
        default="./svr/jadio-recorder/config.json",
        help="Radio service config Json file path",
    )


def add_argument_update_feeds(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=update_feeds)
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

    name_and_fn_pairs = [
        ("insert-record-config", add_argument_insert_record_config),
        ("insert-feed-config", add_argument_insert_feed_config),
        ("record-programs", add_argument_record_programs),
        ("update-feeds", add_argument_update_feeds),
    ]
    for name, add_arument_fn in name_and_fn_pairs:
        sub_parser = subparsers.add_parser(name, help=f"see `{name} -h`")
        add_arument_fn(sub_parser)
        add_argument_common(sub_parser)

    return parser


def insert_record_config(args: argparse.Namespace) -> None:
    with open(args.config_path, "r") as fh:
        data = fh.read()
        try:
            configs = RecordConfig.schema().loads(data, many=True)
        except:
            configs = [RecordConfig.from_json(data)]

    with Recorder(db_host=args.db_host) as handler:
        for config in configs:
            handler.insert_config(config, overwrite=True)


def insert_feed_config(args: argparse.Namespace) -> None:
    with open(args.config_path, "r") as fh:
        data = fh.read()
        try:
            configs = FeedConfig.schema().loads(data, many=True)
        except:
            configs = [FeedConfig.from_json(data)]

    with Feeder(db_host=args.db_host) as handler:
        for config in configs:
            handler.insert_config(config, overwrite=True)


def record_programs(args: argparse.Namespace) -> None:
    with open(args.service_config_path, "r") as fh:
        service_config = json.load(fh)

    with Recorder(
        service_config=service_config,
        media_root=args.media_root,
        db_host=args.db_host,
    ) as handler:
        handler.fetch_programs(force=args.force_fetch)
        handler.reserve_programs()
        handler.record_programs()


def update_feeds(args: argparse.Namespace) -> None:
    with Feeder(
        rss_root=args.rss_root,
        media_root=args.media_root,
        http_host=args.http_host,
        db_host=args.db_host,
    ) as handler:
        handler.update_feeds()


def main():
    parser = parse_args()
    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
