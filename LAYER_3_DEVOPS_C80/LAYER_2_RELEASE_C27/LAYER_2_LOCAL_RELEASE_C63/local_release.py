
"""Direct local replacement workflow for the Project-owned framework release."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import LocalReleaseError

from .local_release_runner import LocalReleaseRun


def run_local_release(project_root: Path | str, *, run_id: str,
                      runner: Callable[[tuple[str, ...], Path], Any] | None = None,
                      test_modules: tuple[str, ...] | None = None,
                      image_mode: str = "refresh") -> dict[str, object]:
    """Run the direct local release without candidate selection or recovery state."""
    try:
        release = LocalReleaseRun(project_root, run_id, runner, test_modules, image_mode)
    except LocalReleaseError as error:
        if str(error) != "local-release-project-selection-invalid":
            raise
        return {
            "outcome": "failed", "failed_step": "validate_project_selection",
            "error_type": "LocalReleaseError", "error": "local-release-project-selection-invalid",
            "effects": [],
        }
    return release.run()
