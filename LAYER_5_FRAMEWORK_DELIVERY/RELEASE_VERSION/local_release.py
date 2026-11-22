
"""Direct local replacement workflow for the Project-owned framework release."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .release_image_provenance import release_image_provenance  # noqa: E402
from .release_inputs import read_release_selection  # noqa: E402
from .local_release_runner import LocalReleaseRun  # noqa: E402
from .local_release_safety import _new_staging_directory  # noqa: E402
from .release_support import (  # noqa: E402
    LocalReleaseError,
    _RUN_ID,
    _cleanup_staging,
    _image_manager,
    _root,
)


def build_image(project_root: Path | str, *, run_id: str) -> dict[str, object]:
    """Build the checked-out image without running the release workflow."""
    root = _root(project_root)
    if not isinstance(run_id, str) or _RUN_ID.fullmatch(run_id) is None:
        raise ValueError("release-run-id-invalid")
    selection = read_release_selection(root)
    provenance = release_image_provenance(root, selection)
    staging = _new_staging_directory(root, f"{run_id}-image-")
    try:
        manager = _image_manager(root, staging, project_root=root, build_provenance=provenance)
        identity = manager.identity(use_packaged_assets=True)
        image = manager.resolve(use_packaged_assets=True)
        if (not isinstance(image, str) or re.fullmatch(r"sha256:[0-9a-f]{64}", image) is None
                or manager.identity(use_packaged_assets=True) != identity):
            raise LocalReleaseError("local-release-packaged-image-mismatch")
        return {"outcome": "completed", "image_id": image, "fingerprint": identity.fingerprint,
                "version": identity.version, "run_id": run_id, "project_root": str(root)}
    finally:
        if _cleanup_staging(root, staging):
            raise LocalReleaseError("local-release-staging-cleanup-failed")


def run_local_release(project_root: Path | str, *, run_id: str,
                      runner: Callable[[tuple[str, ...], Path], Any] | None = None,
                      test_modules: tuple[str, ...] | None = None,
                      image_mode: str = "refresh") -> dict[str, object]:
    """Run the direct local release without candidate selection or recovery state."""
    return LocalReleaseRun(project_root, run_id, runner, test_modules, image_mode).run()
