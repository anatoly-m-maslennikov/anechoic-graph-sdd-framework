"""Build a runtime image from the selected project."""
import re
from pathlib import Path
from .release_image_provenance import release_image_provenance
from .release_inputs import read_release_selection
from .local_release_safety import _new_staging_directory
from .release_package_files import _root
from .runtime_support import LocalReleaseError, _RUN_ID, _cleanup_staging, _image_manager, _native_release_sources

def build_image(project_root: Path | str, *, run_id: str) -> dict[str, object]:
    """Build the checked-out image without running the release workflow."""
    root = _root(project_root)
    if not isinstance(run_id, str) or _RUN_ID.fullmatch(run_id) is None:
        raise ValueError("release-run-id-invalid")
    selection = read_release_selection(root)
    provenance = release_image_provenance(root, selection)
    staging = _new_staging_directory(root, f"{run_id}-image-")
    try:
        manager = _image_manager(root, staging, project_root=root, build_provenance=provenance,
                                 source_provider=lambda: _native_release_sources(selection))
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
