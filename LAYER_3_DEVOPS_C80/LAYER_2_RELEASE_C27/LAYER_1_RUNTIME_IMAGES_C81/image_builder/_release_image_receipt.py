"""Validate the launcher receipt for a selected Project."""

import json
import os
from pathlib import Path
import re
import stat

_IMAGE = re.compile(r"sha256:[0-9a-f]{64}\Z")


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def _receipt_path(root: Path, parts: tuple[str, ...]) -> Path | None:
    path = root
    for part in parts:
        path /= part
        if not os.path.lexists(path):
            return None
        if path.is_symlink() or not path.is_dir():
            raise ValueError("unsafe launcher receipt")
    path /= "ready.json"
    if not os.path.lexists(path):
        return None
    if path.is_symlink():
        raise ValueError("unsafe launcher receipt")
    return path


def ready_predecessor(selection) -> str | None:
    root, state = Path(selection.root), Path(selection.launcher_state)
    try:
        parts = state.relative_to(root).parts
        if (
            not root.is_absolute()
            or root.is_symlink()
            or root.resolve() != root
            or ".." in parts
        ):
            raise ValueError("unsafe launcher receipt")
        path = _receipt_path(root, parts)
        if path is None:
            return None
        fd = os.open(
            path,
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0),
        )
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
                raise ValueError("invalid launcher receipt")
            raw = stream.read(65537)
        if len(raw) > 65536:
            raise ValueError("invalid launcher receipt")
        payload = json.loads(raw, object_pairs_hook=_unique)
        image = payload.get("image_id") if isinstance(payload, dict) else None
        if (
            not isinstance(payload, dict)
            or payload.get("project_root") != str(root)
            or payload.get("control_root") != str(selection.control_root)
            or payload.get("project_id") != selection.instance_id
            or payload.get("readiness") is not True
            or not isinstance(image, str)
            or _IMAGE.fullmatch(image) is None
        ):
            raise ValueError(
                "launcher receipt does not match selected Project"
            )
        return image
    except (OSError, ValueError, UnicodeError, TypeError) as error:
        raise ValueError("invalid launcher receipt") from error
