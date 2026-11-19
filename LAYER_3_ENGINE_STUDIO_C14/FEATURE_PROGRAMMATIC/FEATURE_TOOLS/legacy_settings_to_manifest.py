"""Convert supplied legacy Project Settings data to native Manifest fields."""

from __future__ import annotations

from copy import deepcopy
import math
import re
from typing import Any


def _check(value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} has a non-string key")
            _check(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _check(item, f"{path}[{index}]")
    elif type(value) not in {str, int, float, bool} or (type(value) is float and not math.isfinite(value)):
        raise ValueError(f"{path} cannot be represented in a native Manifest literal")



def legacy_settings_to_manifest(
    settings: dict[str, Any], *, runtime_settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Preserve each supplied value, moving the two identity fields to the Manifest.

    The result is data only. The caller must validate the full Manifest against
    the selected native model before using or writing it. Runtime Settings must
    contain only Project-owned values selected by the caller.
    """
    if not isinstance(settings, dict):
        raise ValueError("Project Settings must be a mapping")
    _check(settings, "settings")
    if runtime_settings is not None:
        if not isinstance(runtime_settings, dict):
            raise ValueError("Project runtime Settings must be a mapping")
        if "runtime" in settings:
            raise ValueError("Project Settings already contain a runtime key")
        _check(runtime_settings, "runtime")
    parameters = deepcopy(settings)
    if runtime_settings is not None:
        parameters["runtime"] = deepcopy(runtime_settings)
    project = parameters.get("project")
    artifacts = parameters.get("artifacts")
    identity = artifacts.get("identity") if isinstance(artifacts, dict) else None
    name = project.get("name") if isinstance(project, dict) else None
    prefix = identity.get("project_prefix") if isinstance(identity, dict) else None
    if not isinstance(name, str) or not name.strip() or name != name.strip():
        raise ValueError("project.name must be a non-empty exact name")
    if not isinstance(prefix, str) or re.fullmatch(r"[A-Z]+", prefix) is None:
        raise ValueError("artifacts.identity.project_prefix must contain uppercase letters")
    if len(parameters) + 2 > 20:
        raise ValueError("Project Settings exceed the native Manifest parameter limit")
    del project["name"]
    del identity["project_prefix"]
    return {"name": name, "prefix": prefix, "parameters": parameters}
