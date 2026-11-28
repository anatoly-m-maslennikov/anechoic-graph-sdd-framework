"""Validate the isolated container settings response."""

import json


def _settings_response(result, command):
    if result.returncode == 3:
        raise FileExistsError("container settings already exist")
    if result.returncode:
        raise ValueError("container settings invalid")
    settings = json.loads(result.stdout)
    if settings is not None and not isinstance(settings, dict):
        raise ValueError("container settings response invalid")
    if command == "create" and settings is None:
        raise ValueError("container settings response invalid")
    return settings
