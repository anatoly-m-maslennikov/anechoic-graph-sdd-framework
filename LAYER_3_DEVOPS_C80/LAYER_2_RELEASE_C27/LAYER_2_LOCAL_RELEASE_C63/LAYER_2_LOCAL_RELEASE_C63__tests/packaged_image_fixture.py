"""Report the Release identity of a Test Suite fixture."""

import argparse
import json
from pathlib import Path
import sys

from LAYER_1_RUNTIME_IMAGES_C81.image_builder.image_builder__shared import (
    ImageManager,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture_root", type=Path)
    root = parser.parse_args().fixture_root.resolve(strict=True)
    manager = ImageManager(root, project_root=root)
    try:
        identity = manager.identity(use_packaged_assets=True)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "fingerprint": identity.fingerprint,
                "manifest": identity.manifest,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
