"""Expose mounted settings to Setup and Release through a process boundary."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("read", "create"))
    parser.add_argument("mounted_root", type=Path)
    args = parser.parse_args(argv)

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        settings.container_settings__pub import (
        CONTAINER_SETTINGS_FILENAME,
        parse_container_settings,
        read_container_settings,
    )  # fmt: skip
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        settings.settings_carrier__pub import (
        write_settings_carrier,
    )  # fmt: skip

    try:
        config = read_container_settings(args.mounted_root)
        if args.action == "create":
            if config is not None:
                raise FileExistsError("Mounted container settings exist")
            fields = json.loads(sys.stdin.read(4097))
            config = parse_container_settings({"container": fields})
            content = "schema_version = 1\n\n[container]\n" + "".join(
                f"{key} = {json.dumps(value, ensure_ascii=False)}\n"
                for key, value in asdict(config).items()
                if value is not None
            )
            write_settings_carrier(
                args.mounted_root / CONTAINER_SETTINGS_FILENAME,
                content,
                validate=parse_container_settings,
                replace_existing=False,
            )
        print(json.dumps(asdict(config) if config is not None else None))
    except FileExistsError as error:
        print(str(error), file=sys.stderr)
        return 3
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
