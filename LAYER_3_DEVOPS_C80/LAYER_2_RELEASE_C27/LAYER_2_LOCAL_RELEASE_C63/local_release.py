"Direct local replacement workflow for the Project-owned framework release."

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _RUN_ID,
    _project_path,
    _root,
)

from .local_release_delivery import abort_lock
from .local_release_reports import failure_path
from .local_release_runner import LocalReleaseRun
from .local_release_state import (
    PHASES,
    _RUNS,
    _checked,
    _current_delivery,
    _delivery_record,
    _read,
    abort_request_path,
    atomic_write,
)


def run_local_release(
    project_root: Path | str,
    *,
    run_id: str | None,
    runner: Callable[[tuple[str, ...], Path], Any] | None = None,
    test_modules: tuple[str, ...] | None = None,
    image_mode: str | None = None,
    resume: bool = False,
    functional_suite: Literal["full", "fast"] | None = None,
    started_at: float | None = None,
    mode: Literal["release", "status", "prepare", "abort"] = "release",
) -> dict[str, object]:
    """Start, continue, inspect or prepare a Local Release."""
    if mode in {"status", "abort"}:
        try:
            return _control_run(_root(project_root), run_id, mode)
        except LocalReleaseError as error:
            return {"outcome": "failed", "run_id": run_id, "error": str(error)}
    if mode == "prepare":
        from .prepare_test_environment import prepare_test_environment

        return prepare_test_environment(project_root)
    if mode != "release":
        raise LocalReleaseError("local-release-mode-invalid")
    try:
        release = LocalReleaseRun(
            project_root,
            run_id,
            runner,
            test_modules,
            image_mode,
            resume=resume,
            functional_suite=functional_suite,
            started_at=started_at,
        )
    except LocalReleaseError as error:
        if str(error) != "local-release-project-selection-invalid":
            raise
        return {
            "outcome": "failed",
            "failed_step": "validate_project_selection",
            "error_type": "LocalReleaseError",
            "error": "local-release-project-selection-invalid",
            "effects": [],
        }
    return release.run()


def _open_run_id(root, delivery):
    runs = _project_path(root, _RUNS, label="resume-journal")
    ids = []
    for path in sorted(runs.glob("*/state.json")):
        run_id = path.parent.name
        data = _checked(
            _read(
                _project_path(
                    root, path.relative_to(root), label="resume-journal"
                )
            ),
            run_id,
        )
        if (
            data["binding"][:1] == [str(root)]
            and not data.get("result")
            and (not delivery or _current_delivery(data, delivery))
        ):
            ids.append(run_id)
    if len(ids) != 1:
        raise LocalReleaseError(
            "local-release-select-run: " + (", ".join(ids) or "no open run")
        )
    return ids[0]


def _control_run(root, run_id, mode):
    _, delivery = _delivery_record(root)
    if run_id is None:
        run_id = _open_run_id(root, delivery)
    if not isinstance(run_id, str) or _RUN_ID.fullmatch(run_id) is None:
        raise LocalReleaseError("local-release-run-id-invalid")
    path = _project_path(
        root, _RUNS / run_id / "state.json", label="resume-journal"
    )
    if not path.exists():
        return {
            "outcome": "failed",
            "run_id": run_id,
            "error": "local-release-resume-run-missing",
        }
    data = _checked(_read(path), run_id)
    if data["binding"][:1] != [str(root)]:
        raise LocalReleaseError("local-release-resume-binding-changed")
    if mode == "abort":
        return _request_abort(root, run_id, path)
    return _recorded_status(
        root, data, delivery, abort_request_path(root, path).exists()
    )


def _request_abort(root, run_id, journal_path):
    with abort_lock(root, journal_path):
        data = _checked(_read(journal_path), run_id)
        _, delivery = _delivery_record(root)
        if data.get("result") or (
            delivery and not _current_delivery(data, delivery)
        ):
            raise LocalReleaseError("local-release-abort-run-closed")
        if (
            data.get("delivery") is not None
            or delivery.get("run_id") == run_id
        ):
            raise LocalReleaseError("local-release-abort-delivery-started")
        atomic_write(abort_request_path(root, journal_path), "abort\n")
    return {"outcome": "completed", "run_id": run_id, "abort_requested": True}


def _recorded_status(root, data, delivery, abort_requested):
    run_id = data["run_id"]
    failures = data.get("failures", [])
    latest = failures[-1] if failures else {}
    result = data.get("result") or {}
    report = result.get("receipt_path") or result.get("report_path")
    if report is None and latest:
        failure = failure_path(root, run_id)
        if failure.is_file():
            report = failure.relative_to(root).as_posix()
    return {
        "outcome": "completed",
        "run_id": run_id,
        "project_root": str(root),
        "working_phase": data.get("working"),
        "completed_phases": data["done"],
        "next_phase": next(
            (phase for phase in PHASES if phase not in data["done"]), None
        ),
        "docker_context": data.get("docker_context"),
        "functional_suite": data.get("functional_suite", "full"),
        "source_root": (data.get("source_binding") or [None])[0],
        "source_revision": data.get("accepted_source_sha"),
        "delivery_started": data.get("delivery") is not None,
        "abort_requested": abort_requested,
        "image_id": data.get("image_id"),
        "canary_endpoint": data.get("canary"),
        "endpoint": data.get("endpoint"),
        "test_log_paths": data["logs"],
        "failure_count": len(failures),
        "last_failure": {
            key: latest.get(key)
            for key in ("phase", "error_type", "source_sha")
        }
        if latest
        else None,
        "release_outcome": result.get("outcome"),
        "report_path": report,
        "superseded": bool(delivery) and not _current_delivery(data, delivery),
    }
