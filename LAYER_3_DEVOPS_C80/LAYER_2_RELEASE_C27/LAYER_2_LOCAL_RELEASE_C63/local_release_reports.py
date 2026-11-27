"""Receipt and failure report writing for a local Release."""

from pathlib import Path

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import LocalReleaseError
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import _project_path

from .local_release_state import atomic_write

_DEPLOYMENT_FIELDS = (
    ("version", "Version"),
    ("source_sha", "Source SHA"),
    ("accepted_source_sha", "Accepted source SHA"),
    ("image_build_sha", "Image build source SHA"),
    ("source_root", "Source root"),
    ("project_root", "Project root"),
    ("project_instance", "Project instance"),
    ("control_root", "Control root"),
    ("target_manifest_sha256", "Target Manifest SHA-256"),
    ("target_runtime_settings_sha256", "Target runtime settings SHA-256"),
    ("port", "Loopback port"),
    ("package_sha256", "Package SHA-256"),
    ("image_id", "Image ID"),
    ("fingerprint", "Image fingerprint"),
    ("container_id", "Production container ID"),
    ("readiness", "MCP readiness"),
    ("observed_at", "Readiness observed at"),
)
_TEST_STEPS = {
    "preflight_tests", "static_tests", "functional_tests", "verify_candidate_image", "verify_candidate_canary",
}


def receipt_path(root, run_id):
    receipt = _project_path(root, Path(".anechoic_runtime/simple_local_release/reports") / f"{run_id}.md",
                              label="simple-receipt")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    return receipt


def _test_logs(paths):
    return "".join(f"Complete {phase} test output: `{path}`\n\n" for phase, path in paths.items())


def _attempt_history(attempts):
    if not attempts:
        return ""
    return "## Previous failed attempts\n\n" + "".join(
        f"Stopped at `{attempt['phase']}` on source `{attempt['source_sha'] or 'unavailable'}`.\n\n"
        + _test_logs(attempt["logs"])
        for attempt in attempts
    )


def write_receipt(root, receipt, run_id, image_mode, test_scope, test_selection, canary_endpoint,
                  endpoint, test_log_paths, cleanup_note, staging_note, *, evidence=None):
    evidence = evidence or {}
    deployment = "".join(f"{label}: `{evidence[key]}`\n\n" for key, label in _DEPLOYMENT_FIELDS if key in evidence)
    verification = "".join(
        f"Verification source SHA for `{phase}`: `{proof['source_sha']}`\n\n"
        for phase, proof in evidence.get("verified_phases", {}).items()
    )
    elapsed = evidence.get("ready_seconds")
    timing = f"Seconds to readiness: `{elapsed}`\n\n" if elapsed is not None else ""
    if evidence.get("functional_suite") == "fast":
        if elapsed is None:
            timing = "Start-to-readiness time unavailable for this run.\n\n"
        else:
            timing += f"Fast path met the ideal 10-minute target: `{evidence['fast_target_met']}`\n\n"
            timing += f"Fast path met the mandatory 15-minute limit: `{evidence['fast_limit_met']}`\n\n"
    atomic_write(
        receipt,
        "# Simple local release receipt\n\n"
        f"Run: `{run_id}`\n\n"
        f"Image mode: `{image_mode}`\n\n"
        f"Test scope: `{test_scope}`\n\n"
        f"Selected test modules: {test_selection}\n\n"
        f"Canary endpoint: `{canary_endpoint}`\n\n"
        f"Endpoint: `{endpoint or 'not reported'}`\n\n"
        + deployment
        + timing
        + verification
        + _test_logs(test_log_paths)
        + f"Image cleanup: {cleanup_note}\n\n{staging_note}"
        + _attempt_history(evidence.get("failed_attempts", ())),
    )
    return receipt.relative_to(root).as_posix()


def record_receipt(run):
    run.receipt_path = write_receipt(
        run.root, receipt_path(run.root, run.run_id), run.run_id, run.image_mode,
        run.test_scope, run.test_selection, run.canary_endpoint, run.endpoint,
        run.test_log_paths, run.cleanup_note, "", evidence=run.journal.data["evidence"],
    )


def failure_path(root, run_id):
    relative = Path(".anechoic_runtime/simple_local_release/reports/failures") / f"{run_id}.md"
    return _project_path(root, relative, label="simple-report")


def write_failure(root, run_id, failed_step, image_mode, test_scope, test_selection,
                  error, test_log_paths, endpoint, cleanup_note, cleanup, staging_note):
    try:
        report = failure_path(root, run_id)
        report.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(
            report,
            "# Simple local release failed\n\n"
            f"Run: `{run_id}`\n\nStopped at: `{failed_step}`\n\n"
            f"Image mode: `{image_mode}`\n\n"
            f"Test scope: `{test_scope}`\n\n"
            f"Selected test modules: {test_selection}\n\n"
            f"Error class: `{type(error).__name__}`\n\n"
            + (f"{str(error)[:8500]}\n\n" if failed_step in _TEST_STEPS else "")
            + _test_logs(test_log_paths)
            + (f"MCP started at: `{endpoint}`\n\n" if endpoint is not None else "")
            + ("\n".join(getattr(error, "__notes__", ())) + "\n\n" if getattr(error, "__notes__", ()) else "")
            + "Manual action required: inspect the current project state before any retry.\n\n"
            + ("Docker cleanup:\n" + "\n".join([cleanup_note, *cleanup.notes]) + "\n\n" if cleanup is not None else "")
            + staging_note,
        )
        return report.relative_to(root).as_posix()
    except (LocalReleaseError, OSError):
        return None
