"""Parse startup timing and flow observations."""

from datetime import datetime, timezone
import json
import re

from . import staged_startup__support as source


_TIMING_PREFIX = "ANECHOIC_STARTUP_TIMING "
_TIMING_PHASES = frozenset(
    {
        "worker_started",
        "scan_started",
        "scan_metrics",
        "non_archived_load_started",
        "model_ready",
        "structure_ready",
        "realization_graph_ready",
        "non_archived_load_ended",
        "archive_load_ended",
    }
)
_TIMING_NUMBERS = frozenset(
    {
        "census_ns",
        "guarded_read_ns",
        "stream_ns",
        "sha256_ns",
        "carrier_count",
        "bytes_read",
        "changed_paths",
        "comparison_ns",
        "checkpoint_validation_ns",
    }
)
_TIMING_MODES = frozenset(
    {
        "foreground_capture",
        "foreground_hashes",
        "built",
        "reused",
        "disabled",
        "full",
        "native_delta",
        "cold",
    }
)


def started_at_ns(value):
    match = re.fullmatch(
        r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d{1,9}))?Z", value
    )
    if not match:
        raise ValueError("Invalid Docker State.StartedAt: " + value)
    seconds = int(
        datetime.strptime(match[1], "%Y-%m-%dT%H:%M:%S")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )
    return seconds * 1_000_000_000 + int((match[2] or "").ljust(9, "0"))


def startup_events(logs, started):
    events = []
    for line in logs.splitlines():
        if len(line) > 8192 or not line.startswith(_TIMING_PREFIX):
            continue
        try:
            event = json.loads(line[len(_TIMING_PREFIX) :])
        except ValueError, TypeError:
            continue
        if (
            not isinstance(event, dict)
            or not isinstance(event.get("phase"), str)
            or event["phase"] not in _TIMING_PHASES
            or type(event.get("timestamp_ns")) is not int
            or event["timestamp_ns"] < started
        ):
            continue
        try:
            elapsed = (event["timestamp_ns"] - started) / 1_000_000_000
        except OverflowError:
            continue
        clean = {
            "phase": event["phase"],
            "timestamp_ns": event["timestamp_ns"],
            "launch_to_phase_seconds": elapsed,
        }
        for name in _TIMING_NUMBERS:
            value = event.get(name)
            if type(value) is int and 0 <= value <= 2**63 - 1:
                clean[name] = value
        if (
            isinstance(event.get("mode"), str)
            and event["mode"] in _TIMING_MODES
        ):
            clean["mode"] = event["mode"]
        if event.get("archive") in ("disabled", "none", "deferred"):
            clean["archive"] = event["archive"]
        events.append(clean)
    return source.scan_durations(
        sorted(events, key=lambda event: event["timestamp_ns"])
    )


def scan_durations(events):
    scans = {}
    for event in events:
        mode = event.get("mode")
        if mode and event["phase"] == "scan_started":
            scans[mode] = event["timestamp_ns"]
        elif mode and event["phase"] == "scan_metrics" and mode in scans:
            beginning = scans.pop(mode)
            if event["timestamp_ns"] >= beginning:
                event["scan_seconds"] = (
                    event["timestamp_ns"] - beginning
                ) / 1_000_000_000
    return events


def timing_summary(logs, started):
    events = source.startup_events(logs, source.started_at_ns(started))
    observed = {event["phase"] for event in events}
    core = (
        "scan_started",
        "non_archived_load_started",
        "model_ready",
        "structure_ready",
        "realization_graph_ready",
        "non_archived_load_ended",
        "archive_load_ended",
    )
    admission = next(
        (
            event
            for event in events
            if event["phase"] == "non_archived_load_ended"
        ),
        {},
    )
    archive = admission.get("archive")
    not_applicable = (
        {"archive_load_ended": archive}
        if archive in ("disabled", "none")
        else {}
    )
    return {
        "started_at": started,
        "events": events,
        "unobserved": [
            name
            for name in core
            if name not in observed and name not in not_applicable
        ],
        "not_applicable": not_applicable,
        "optional_phases": ["worker_started", "scan_metrics"],
    }


def cold_throughput(timing, live_atoms):
    events = timing["events"]
    begin = [
        row["timestamp_ns"]
        for row in events
        if row["phase"] == "non_archived_load_started"
    ]
    end = [
        row["timestamp_ns"]
        for row in events
        if row["phase"] == "non_archived_load_ended"
        and row.get("mode") == "full"
    ]
    result = {
        "live_atoms": live_atoms,
        "load_seconds": None,
        "live_atoms_per_load_second": None,
    }
    if len(begin) == len(end) == 1 and end[0] > begin[0]:
        result["load_seconds"] = (end[0] - begin[0]) / 1_000_000_000
        result["live_atoms_per_load_second"] = (
            live_atoms / result["load_seconds"]
        )
    else:
        result["unavailable"] = (
            "one positive-duration full foreground load interval was not "
            "observed"
        )
    return result


def startup_outcome(rows):
    triggers = [
        run
        for run, kind, name, *_ in rows
        if (kind, name) == ("trigger", "startup")
    ]
    if not triggers:
        return None
    if len(triggers) != 1:
        raise RuntimeError(
            "Multiple foreground startup flows in one container start"
        )
    run = triggers[0]
    current = [row[1:] for row in rows if row[0] == run]
    results = [
        (state, detail)
        for kind, name, state, detail in current
        if (kind, name) == ("output", "generation_result")
    ]
    if not results:
        return None
    if len(results) != 1:
        raise RuntimeError("Multiple foreground results in one startup flow")
    return _outcome_result(run, current, results[0])


def _outcome_result(run, current, result):
    state, raw = result
    detail = json.loads(raw)
    effects = {
        "worker_started",
        "generation_admission",
        "generation_reuse_check",
    }
    return {
        "run_id": run,
        "outcome": state,
        "kind": detail.get("kind"),
        "generation": detail.get("generation"),
        "delta_path_count": detail.get("delta_path_count"),
        "reason": {
            "trigger": "startup",
            "source": "C68 flow_events",
            "code": detail.get("code"),
            "effects": [
                [name, outcome, json.loads(payload)]
                for kind, name, outcome, payload in current
                if kind == "effect" and name in effects
            ],
        },
    }
