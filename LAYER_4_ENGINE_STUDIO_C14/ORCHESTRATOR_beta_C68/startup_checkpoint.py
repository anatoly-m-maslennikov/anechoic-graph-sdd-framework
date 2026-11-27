"""Validate and partition a persisted carrier checkpoint."""
from pathlib import PurePosixPath
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

MAX_DELTA_PATHS = 1024
CHECKPOINT_FIELDS = {"carrier_hashes", "folder_hashes", "archive_pending", "checkpoint_scope"}
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class ReuseRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    base_generation: str
    inputs: Any
    graph_config: Any
    endpoints: Any
    status_domains: dict[str, list[str]] | None = None
    carrier_hashes: Any = None
    folder_hashes: Any = None
    archive_pending: Any = None
    checkpoint_scope: Literal["foreground", "archive"] | None = None


def compatible_checkpoint(reuse):
    return (isinstance(reuse, dict) and isinstance(reuse.get("carrier_hashes"), dict)
            and isinstance(reuse.get("folder_hashes"), dict)
            and isinstance(inputs := reuse.get("inputs"), dict)
            and isinstance(value := inputs.get("carrier_schema"), str)
            and _SHA256.fullmatch(value) is not None)


def archive_checkpoint(reuse):
    return {**{key: value for key, value in reuse.items() if key not in CHECKPOINT_FIELDS},
            **{key: {path: digest for path, digest in reuse[key].items()
                     if "09_archived" in PurePosixPath(path).parts[1:]}
               for key in ("carrier_hashes", "folder_hashes")}}


def checkpoint_paths(paths):
    if not isinstance(paths, list) or not 0 < len(paths) <= MAX_DELTA_PATHS:
        return None
    result = []
    for pair in paths:
        if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(x, str) and x for x in pair):
            return None
        parent, name = pair
        path = PurePosixPath(parent) / name
        if ("\\" in parent or "\\" in name or path.is_absolute() or ".." in path.parts
                or path.parent.as_posix() != parent or path.name != name):
            return None
        result.append(pair)
    return result if result == sorted(result) and len({tuple(pair) for pair in result}) == len(result) else None
