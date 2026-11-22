"""Select authored legacy Project data for migration rejection tests."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.project_selection import resolve_project


def select_legacy_project(root, control_root):
    return resolve_project(root, control_root)
