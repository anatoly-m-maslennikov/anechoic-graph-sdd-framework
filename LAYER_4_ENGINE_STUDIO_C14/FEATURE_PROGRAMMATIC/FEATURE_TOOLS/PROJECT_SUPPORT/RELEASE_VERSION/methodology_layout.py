"""Read the current release places from Scope Unit Declarations."""

from __future__ import annotations

from collections.abc import Mapping
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from pathlib import Path


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    active_selection,
)


@dataclass(
    config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True),
    frozen=True,
)
class MethodologyLayout:
    source_root: str
    product_root: str
    source_copy_root: str
    applicable_root: str
    control_root: str
    installed_root: str
    declaration_sha256: str


def _place(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("Methodology place must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path == Path("."):
        raise ValueError("Methodology place must stay within the Project")
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("Methodology place must not traverse a symlink")
    current.resolve().relative_to(root)
    return path


def _scope_unit(rows: tuple[object, ...], name: str) -> Mapping[str, object]:
    matches = [
        row
        for row in rows
        if isinstance(row, Mapping) and row.get("scope_unit_name") == name
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Scope Unit Declarations must register exactly one {name}"
        )
    return matches[0]


def resolve_methodology_layout(project_root: Path | str) -> MethodologyLayout:
    root = Path(project_root).resolve(strict=True)
    selection = active_selection(root)
    control = selection.control_relative
    rows = selection.structure.get("scope_units")
    if not isinstance(rows, tuple):
        raise ValueError("Scope Unit Declarations must derive Scope Units")

    parent = "FRAMEWORK_METHODOLOGY"
    framework = _scope_unit(rows, parent)
    sources = _scope_unit(rows, "METHODOLOGY_SOURCES")
    applicable = _scope_unit(rows, "APPLICABLE_METHODOLOGY")
    if sources.get("parent") != parent or applicable.get("parent") != parent:
        raise ValueError(
            "Methodology source and applicable places must belong to "
            "FRAMEWORK_METHODOLOGY"
        )
    source = _place(root, sources.get("authority_path"))
    product = _place(root, framework.get("delivery_path"))
    copied = _place(root, sources.get("delivery_path"))
    compiled = _place(root, applicable.get("delivery_path"))
    installed = _place(root, (control / "000_ANECHOIC_framework").as_posix())
    if not source.is_relative_to(control) or source.is_relative_to(installed):
        raise ValueError(
            "Release sources must be Project authority, not installed "
            "Methodology"
        )
    if copied.parent != product or compiled.parent != product:
        raise ValueError(
            "Methodology source and applicable deliveries must be product "
            "children"
        )
    if product.is_relative_to(control) or source.is_relative_to(product):
        raise ValueError(
            "Methodology product must not enclose Project authority"
        )
    return MethodologyLayout(
        source.as_posix(),
        product.as_posix(),
        copied.as_posix(),
        compiled.as_posix(),
        control.as_posix(),
        installed.as_posix(),
        selection.declaration_digest,
    )
