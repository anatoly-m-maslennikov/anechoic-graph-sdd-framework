"""Small real-carrier fixture helpers shared by Workbench integration tests."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
from unittest.mock import patch

from watchdog.observers.polling import PollingObserver


def polling_source_watcher():
    "Use filesystem snapshots for transport fixtures that run in a sandbox."
    return patch(
        (
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.source_watcher__p"
            "ub.NativeObserver"
        ),
        PollingObserver,
    )


def extension_directory(root: Path) -> Path:
    """Use the suite-prepared DuckPGQ cache, overridable for local runs."""
    return Path(
        os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            root / ".anechoic_tmp" / "workbench" / "extensions",
        )
    )


def write_settings(root: Path) -> Path:
    control = root / ".anechoic_anechoic"
    control.mkdir()
    (control / "anechoic_project_settings.toml").write_text(
        '[project]\nname = "fixture"\n[artifacts.identity]\nproject_prefix = "CA"\n'
        '[paths]\ncontrol_root = ".anechoic_anechoic"\n',
        encoding="utf-8",
    )
    return control


def write_atom(
    path: Path,
    atom_id: str,
    *,
    status: str = "Active",
    version: int = 1,
    relations: str = "{}",
    subjects: str = "{}",
    body: str = "# Summary\n\nFixture source.\n",
    extra: str = "",
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f'atom_id: "{atom_id}"\n'
        'role: "Requirement"\n'
        'form: "Definition"\n'
        f'status: "{status}"\n'
        f"version: {version}\n"
        'updated_at: "2026-11-04 00:00:00 +0000"\n'
        f"subjects: {subjects}\n"
        f"relations: {relations}\n"
        f"{extra}"
        "---\n" + body,
        encoding="utf-8",
    )
    return path


def source_path(
    declarations: dict[str, dict[str, Any]], scope: str, role: str, name: str
) -> Path:
    relative = Path(name)
    if not re.match(r"^[A-Za-z0-9_]+-[A-Z]-", relative.name):
        name = str(relative.with_name("CA-R-" + relative.name))
    return Path(declarations[scope]["authority_path"]) / role / name
