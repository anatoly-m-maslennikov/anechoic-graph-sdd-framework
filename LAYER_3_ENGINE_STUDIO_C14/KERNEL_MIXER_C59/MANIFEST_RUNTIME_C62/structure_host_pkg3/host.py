"""Publish validated Structure snapshots received from the compiler."""

import os
from pathlib import Path
import sys

from .snapshot import read_structure


def main(path: Path, model_sha256: str) -> None:
    candidate = path.with_suffix(".pending")
    for line in sys.stdin.buffer:
        try:
            if line != b"publish\n":
                raise ValueError("invalid publication request")
            snapshot = read_structure(candidate)
            if snapshot.model_sha256 != model_sha256:
                raise ValueError("model hash mismatch")
        except (ValueError, UnicodeError):
            print("invalid", flush=True)
            continue
        os.replace(candidate, path)
        print("ready", flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2])
