"""Source path exclusion rules."""

from pathlib import PurePosixPath


_EXCLUDED_PARTS = frozenset(
    {
        ".anechoic_archive",
        ".anechoic_install",
        ".anechoic_legacy",
        ".anechoic_runtime",
        ".anechoic_tmp",
        ".anechoic_anechoic",
        ".cache",
        ".git",
        ".hg",
        ".mypy_cache",
        ".nox",
        ".pytest_cache",
        ".ruff_cache",
        ".runtime",
        ".svn",
        ".tox",
        ".venv",
        "__pycache__",
        "archive",
        "archives",
        "build",
        "coverage",
        "dist",
        "dist-packages",
        "env",
        "generated",
        "gen",
        "history",
        "node_modules",
        "out",
        "migration-evidence",
        "site-packages",
        "target",
        "temp",
        "tmp",
        "vendor",
        "venv",
    }
)


def excluded_source_path(relative: str, *, directory: bool = False) -> bool:
    parts = PurePosixPath(relative).parts
    folder_parts = parts if directory else parts[:-1]
    return any(
        part.startswith((".", "_anechoic_")) for part in folder_parts
    ) or any(part.casefold() in _EXCLUDED_PARTS for part in parts)
