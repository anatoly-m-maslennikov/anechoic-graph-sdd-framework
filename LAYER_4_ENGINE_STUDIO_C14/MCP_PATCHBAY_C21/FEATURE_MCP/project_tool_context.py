
"""Validate the optional single-Project MCP envelope without selecting Projects."""

from __future__ import annotations

from pathlib import Path
from typing import Any



def native_arguments(
    arguments: Any, selection: Any, root: Path,
) -> Any:
    """Accept only the bound host/container root, then remove the outer assertion."""
    if not isinstance(arguments, dict) or "project_root" not in arguments:
        return arguments
    value = arguments["project_root"]
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ValueError("project_root must be a canonical bound Project root")
    try:
        path = Path(value)
    except (TypeError, ValueError) as error:
        raise ValueError("project_root must be a canonical bound Project root") from error
    if not path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise ValueError("project_root must be a canonical bound Project root")
    allowed = {str(root if selection is None else selection.root)}
    if selection is not None and getattr(selection, "host_root", None) is not None:
        allowed.add(str(selection.host_root))
    if value not in allowed:
        raise ValueError("project_root does not match the bound Project")
    return {key: item for key, item in arguments.items() if key != "project_root"}


__all__ = ["native_arguments"]
