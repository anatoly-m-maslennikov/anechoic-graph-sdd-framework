"""Inventory candidate active Model source paths."""

from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CUSTOM_MODEL_DIRECTORY,
    PROJECT_CONFIG_DIRECTORY,
)


def _inventory_active_sources(reader, control, component):
    paths = []
    for directory in (
        component,
        component / "_SPEC",
        component / "_DES",
        component / "_DOM" / "CONT",
    ):
        if directory.exists() or directory.is_symlink():
            paths.extend(
                (path, False) for path in reader.inventory_shallow(directory)
            )
    for name in dict.fromkeys(
        (PROJECT_CONFIG_DIRECTORY, "__PROJECT_CONFIG", "002_PROJECT_CONFIG")
    ):
        custom = control / name / CUSTOM_MODEL_DIRECTORY
        if custom.exists() or custom.is_symlink():
            paths.extend(
                (path, True) for path in reader.inventory_shallow(custom)
            )
    return paths
