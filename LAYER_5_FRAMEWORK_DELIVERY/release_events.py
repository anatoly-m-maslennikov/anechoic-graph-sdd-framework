"""Plain, nonblocking Journal recording for host release invocations."""

# CA-M-347@19

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def record_release_event(
    root: Path,
    operation: str,
    run_id: str,
    event: str,
    preceding: str | None,
    outcome: str | None = None,
    *,
    selection=None,
) -> tuple[str | None, str | None]:
    try:
        from work_journal import append_record, event_record

        extra = {}
        if selection is not None:
            if selection.root != root:
                raise ValueError("Native Project selection does not match the release root")
            timezone = selection.parameters.get("artifact_timestamps", {}).get("timezone", "local")
            moment = datetime.now().astimezone() if timezone == "local" else datetime.now(
                UTC if timezone == "UTC" else ZoneInfo(timezone)
            )
            extra["occurred_at"] = moment.strftime("%Y-%m-%d %H:%M:%S %z")
        record = event_record(
            root=root,
            event=event,
            action_id=run_id,
            kind="workflow",
            scope="project",
            operation=operation,
            session_id=run_id,
            subjects=[],
            outputs=[],
            preceding_event=preceding,
            details={"outcome": outcome} if outcome is not None else {},
            **extra,
        )
        if selection is None:
            append_record(root, record)
        else:
            from work_journal import append_sealed_events, journal_storage

            canonical = (selection.control_relative / "_journal").as_posix()
            journal_root = selection.parameters.get("paths", {}).get("journal_root", canonical)
            if journal_root != canonical:
                raise ValueError("Native Journal root contradicts the selected control root")
            append_sealed_events(root, [record], author="src-work-journal",
                                 local_date=record["occurred_at"][:10], timezone=timezone,
                                 journal_root=journal_root, storage=journal_storage(selection.parameters))
        event_id = record.get("event_id")
        return event_id if isinstance(event_id, str) else None, None
    except (AttributeError, ImportError, OSError, RuntimeError, TypeError, ValueError, ZoneInfoNotFoundError) as error:
        return None, f"Release {event} recording failed: {error}"


def run_recorded_release(
    root: Path,
    operation: str,
    run_id: str,
    invoke: Callable[[], dict[str, object]],
    *,
    selection=None,
) -> dict[str, object]:
    recording_options = {"selection": selection} if selection is not None else {}
    try:
        started, start_error = record_release_event(root, operation, run_id, "started", None, **recording_options)
    except KeyboardInterrupt:
        result: dict[str, object] = {
            "outcome": "failed",
            "failed_step": "invocation",
            "error_type": "KeyboardInterrupt",
            "run_id": run_id,
            "project_root": str(root),
        }
        try:
            _, terminal_error = record_release_event(
                root, operation, run_id, "failed", None, "failed", **recording_options
            )
        except KeyboardInterrupt:
            terminal_error = "Release failed recording interrupted"
        errors = ["Release started recording interrupted"]
        if terminal_error is not None:
            errors.append(terminal_error)
        result["recording_error"] = "; ".join(errors)
        return result
    try:
        result = invoke()
    except KeyboardInterrupt:
        result = {
            "outcome": "failed",
            "failed_step": "invocation",
            "error_type": "KeyboardInterrupt",
        }
    except (AttributeError, ImportError, OSError, RuntimeError, TypeError, ValueError) as error:
        result = {
            "outcome": "failed",
            "failed_step": "invocation",
            "error_type": type(error).__name__,
        }
    observed_outcome = result.get("outcome", "failed")
    outcome = observed_outcome if isinstance(observed_outcome, str) else "failed"
    event = "completed" if outcome == "completed" else "failed"
    try:
        _, terminal_error = record_release_event(
            root, operation, run_id, event, started, outcome, **recording_options
        )
    except KeyboardInterrupt:
        terminal_error = f"Release {event} recording interrupted"
        result["error_type"] = "KeyboardInterrupt"
    result.update(run_id=run_id, project_root=str(root))
    errors = [error for error in (start_error, terminal_error) if error is not None]
    if errors:
        result["recording_error"] = "; ".join(errors)
    return result
