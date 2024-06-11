import argparse
import json
import logging
from pathlib import Path

from .config import RecordConfig
from .recorder import Recorder

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s: %(message)s"
)


def add_argument_common(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--database-host",
        type=str,
        default="mongodb://localhost:27017/",
        help="MongoDB host",
    )


def add_argument_insert_config(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=insert_config)
    parser.add_argument(
        "record_config_path", type=Path, help="Record config file path (JSON)"
    )


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    name_and_fn_pairs = [
        ("insert-config", add_argument_insert_config),
        ("record-programs", add_argument_record_programs),
    ]
    for name, add_arument_fn in name_and_fn_pairs:
        sub_parser = subparsers.add_parser(name, help=f"see `{name} -h`")
        add_arument_fn(sub_parser)
        add_argument_common(sub_parser)

    return parser


def insert_config(args: argparse.Namespace) -> None:
    with open(args.record_config_path, "r") as fh:
        data = fh.read()
        try:
            configs = RecordConfig.schema().loads(data, many=True)
        except:
            configs = [RecordConfig.from_json(data)]

    with Recorder(
        database_host=args.database_host,
    ) as recorder:
        for config in configs:
            recorder.insert_config(config)


def record_programs(args: argparse.Namespace) -> None:
    with open(args.service_config_path, "r") as fh:
        service_config = json.load(fh)

    with Recorder(
        media_root=args.media_root,
        service_config=service_config,
        database_host=args.database_host,
    ) as recorder:
        recorder.fetch_programs(force=args.force_fetch)
        recorder.reserve_programs()
        recorder.record_programs()


def main():
    parser = parse_args()
    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
