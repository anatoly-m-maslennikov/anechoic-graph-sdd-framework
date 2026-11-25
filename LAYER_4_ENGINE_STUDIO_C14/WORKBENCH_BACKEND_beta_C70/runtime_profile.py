"""Resolve process-scoped Beta storage and archive settings."""

import os

_PROFILES = {
    "dev-local": ("memory", "files", "skip"),
    "dev-preprod": ("disk", "duckdb", "load"),
    "test": ("memory", "files", "load"),
    "prod": ("disk", "duckdb", "load"),
}
_KEYS = ("ANECHOIC_WORKBENCH_STORAGE", "ANECHOIC_JOURNAL_STORAGE", "ANECHOIC_ARCHIVES")
_PROFILE = "ANECHOIC_RUNTIME_PROFILE"


def resolve_runtime_profile(storage, journal_storage, environ=None):
    env = os.environ if environ is None else environ
    if not any(key in env for key in (_PROFILE, *_KEYS)):
        return storage, journal_storage, "load"
    profile = env.get(_PROFILE, "dev-preprod")
    if profile not in _PROFILES:
        raise ValueError("Invalid ANECHOIC_RUNTIME_PROFILE")
    values = tuple(env.get(key, default) for key, default in zip(_KEYS, _PROFILES[profile], strict=True))
    for key, value, allowed in zip(_KEYS, values, (("memory", "disk"), ("files", "duckdb"), ("load", "skip")), strict=True):
        if value not in allowed:
            raise ValueError(f"Invalid {key}")
    workbench, journal, archives = values
    if workbench == "disk" and archives == "skip" and profile != "dev-local":
        raise ValueError("Skipping archives with disk storage requires the dev-local profile")
    return workbench, journal, archives
