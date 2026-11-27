"""Read a formal Spec carrier from a local tree for offline verification."""

import hashlib
from pathlib import Path

from .carrier_read__pub import parse_carrier


def read_spec_file(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if (
        path == root
        or path != root / relative
        or not path.is_relative_to(root)
    ):
        raise ValueError("invalid source path")
    raw = path.read_bytes()
    return parse_carrier(raw, path), hashlib.sha256(raw).hexdigest()
