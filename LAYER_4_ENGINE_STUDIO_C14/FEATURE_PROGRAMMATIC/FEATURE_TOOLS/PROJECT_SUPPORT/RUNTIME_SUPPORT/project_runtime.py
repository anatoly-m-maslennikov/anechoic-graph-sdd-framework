"""Resolve the Project boundary for operations that receive an input path."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import TemporaryBoundaryError  # fmt: skip


_NATIVE_ROOT = ContextVar("native_temporary_project_root", default=None)


@contextmanager
def bind_native_runtime(selection):
    "Use an explicitly selected native Project for shared filesystem effects."
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
        PROJECT_SUPPORT.PROJECT_SELECTION.\
        PROJECT_SELECTION__shared import (
        NativeProjectSelection,
    )

    if not isinstance(selection, NativeProjectSelection):
        raise TemporaryBoundaryError(
            "A validated native Project selection is required"
        )
    token = _NATIVE_ROOT.set(selection.root)
    try:
        yield
    finally:
        _NATIVE_ROOT.reset(token)


def repository_root(reference: Path | str) -> Path:
    """Resolve the nearest checkout or self-contained ANECHOIC Project.

    Installed and sealed Projects need not contain Git administration data.
    Their Settings and current Scope Unit Declarations identify the boundary.
    A lone folder name or runtime/scratch directory is not a Project marker.
    """

    candidate = Path(reference).expanduser().resolve()
    if not candidate.is_dir():
        candidate = candidate.parent
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.settings__shared import (
        bound_selection,
    )

    selection = bound_selection()
    if candidate == _NATIVE_ROOT.get() or (
        selection is not None and candidate == selection.root
    ):
        return candidate
    for root in (candidate, *candidate.parents):
        if (root / ".git").exists():
            return root
        for control in root.glob(".anechoic_*"):
            if control.is_symlink() or not control.is_dir():
                continue
            marker = control / "anechoic_project_settings.toml"
            if not marker.is_file() or marker.is_symlink():
                continue
            try:
                from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
                    PROJECT_SUPPORT.PROJECT_SELECTION.\
                    PROJECT_SELECTION__shared \
                    import resolve_project  # fmt: skip
                from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
                    ProjectSelectionError,
                )

                resolve_project(root, control.name)
            except ImportError, ProjectSelectionError:
                continue
            else:
                return root
    raise TemporaryBoundaryError(
        f"cannot resolve Project root from {candidate}"
    )
