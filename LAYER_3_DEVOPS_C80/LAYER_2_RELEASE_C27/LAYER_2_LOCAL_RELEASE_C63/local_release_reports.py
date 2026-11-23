"""Receipt and failure report writing for a local Release."""

from pathlib import Path

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import LocalReleaseError
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import _project_path


def receipt_path(root, run_id):
    receipt = _project_path(root, Path(".anechoic_runtime/simple_local_release/reports") / f"{run_id}.md",
                              label="simple-receipt")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    return receipt


def write_receipt(root, receipt, run_id, image_mode, test_scope, test_selection, canary_endpoint,
                  endpoint, test_log_paths, cleanup_note, staging_note):
    receipt.write_text(
        "# Simple local release receipt\n\n"
        f"Run: `{run_id}`\n\n"
        f"Image mode: `{image_mode}`\n\n"
        f"Test scope: `{test_scope}`\n\n"
        f"Selected test modules: {test_selection}\n\n"
        f"Canary endpoint: `{canary_endpoint}`\n\n"
        f"Endpoint: `{endpoint or 'not reported'}`\n\n"
        + "".join(f"Complete {phase} test output: `{path}`\n\n" for phase, path in test_log_paths.items())
        + f"Image cleanup: {cleanup_note}\n\n{staging_note}", encoding="utf-8",
    )
    return receipt.relative_to(root).as_posix()


def write_failure(root, run_id, failed_step, image_mode, test_scope, test_selection,
                  error, test_log_paths, endpoint, cleanup_note, cleanup, staging_note):
    relative = Path(".anechoic_runtime/simple_local_release/reports") / f"{run_id}.md"
    try:
        report = _project_path(root, relative, label="simple-report")
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(
            "# Simple local release failed\n\n"
            f"Run: `{run_id}`\n\nStopped at: `{failed_step}`\n\n"
            f"Image mode: `{image_mode}`\n\n"
            f"Test scope: `{test_scope}`\n\n"
            f"Selected test modules: {test_selection}\n\n"
            f"Error class: `{type(error).__name__}`\n\n"
            + (f"{str(error)[:8500]}\n\n" if failed_step in {"static_tests", "unit_tests", "verify_candidate_image"} else "")
            + "".join(f"Complete {phase} test output: `{path}`\n\n" for phase, path in test_log_paths.items())
            + (f"MCP started at: `{endpoint}`\n\n" if endpoint is not None else "")
            + ("\n".join(getattr(error, "__notes__", ())) + "\n\n" if getattr(error, "__notes__", ()) else "")
            + "Manual action required: inspect the current project state before any retry.\n\n"
            + ("Docker cleanup:\n" + "\n".join([cleanup_note, *cleanup.notes]) + "\n\n" if cleanup is not None else "")
            + f"{staging_note}", encoding="utf-8",
        )
        return relative.as_posix()
    except (LocalReleaseError, OSError):
        return None
