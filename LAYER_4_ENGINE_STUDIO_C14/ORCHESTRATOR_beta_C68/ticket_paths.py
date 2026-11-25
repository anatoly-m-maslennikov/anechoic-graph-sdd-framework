"""Identify bounded Ticket file changes."""
import re
import stat
from pathlib import Path

from .startup_checkpoint import MAX_DELTA_PATHS

TICKET_ROOTS = {"__TICKETS", "001_TICKETS", "__TKT"}


def ticket_delta_paths(binding, changes):
    root = Path(binding["root"])
    control = root / binding["control_root"]
    if not control.name.startswith(("_anechoic_", ".")) or not control.is_dir():
        return None
    ticket = re.compile(rf"{re.escape(binding['project_prefix'])}-T-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?[-.].*\.md\Z")
    paths = set()
    for change in changes:
        if not isinstance(change, dict) or change.get("is_directory") is not False:
            return None
        event = change.get("event_type")
        source, destination = change.get("old_path"), change.get("new_path")
        if event == "moved":
            if destination == source:
                return None
            endpoints = (source, destination)
        elif event in ("created", "deleted", "modified") and destination in (None, ""):
            endpoints = (source,)
        else:
            return None
        for value in endpoints:
            relative = _ticket_path(root, control, ticket, value)
            if relative is None:
                return None
            paths.add(relative)
            if len(paths) > MAX_DELTA_PATHS:
                return None
    return sorted(paths) or None


def _ticket_path(root, control, ticket, value):
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if (not path.is_absolute() or str(path) != value or ".." in path.parts
            or not ticket.fullmatch(path.name) or not path.is_relative_to(control)):
        return None
    parts = path.relative_to(control).parts
    relative = path.relative_to(root).as_posix()
    if len(parts) < 2 or parts[0] not in TICKET_ROOTS or "\\" in relative:
        return None
    try:
        if path.resolve() != path:
            return None
        if not stat.S_ISREG(path.lstat().st_mode):
            return None
    except FileNotFoundError:
        pass
    except (OSError, ValueError, RuntimeError):
        return None
    return relative
