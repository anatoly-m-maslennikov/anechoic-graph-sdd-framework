"""Publish the validated Structure for the Model bound by Kernel."""

import os
from pathlib import Path

from .structure_host_CS3__pub import read_structure


def publish_structure(path: Path, model_sha256: str, payload: bytes) -> None:
    """Replace the active snapshot only after validation."""
    candidate = path.with_suffix(".pending")
    try:
        candidate.write_bytes(payload)
        if read_structure(candidate).model_sha256 != model_sha256:
            raise ValueError("Structure Model fingerprint mismatch")
        os.replace(candidate, path)
    finally:
        candidate.unlink(missing_ok=True)
