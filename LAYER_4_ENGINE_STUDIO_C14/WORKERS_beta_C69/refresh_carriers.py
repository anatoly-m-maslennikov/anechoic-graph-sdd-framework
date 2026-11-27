"""Capture and validate the Carrier changes for a generation refresh."""

from pathlib import PurePosixPath
import re
from time import monotonic_ns

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    mark_startup_timing,
)  # fmt: skip

from .refresh_inputs import _domain_option, carrier_schema, digest
from .startup_inventory import changed_paths, folder_hashes


def _ticket_delta(binding, reuse, paths, capture_ticket_delta=None):
    if reuse is None:
        return None
    if capture_ticket_delta is None:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
            ADAPTERS_C30__shared import (
            capture_ticket_delta,
        )  # fmt: skip

    try:
        result = capture_ticket_delta(
            binding,
            paths,
            reuse.endpoints,
            include_hashes=True,
            **_domain_option(reuse),
        )
    except OSError, RuntimeError, TypeError, ValueError:
        return None
    if result is None:
        return None
    return {
        "base_generation": reuse.base_generation,
        "snapshot_sha256": digest(result),
        **result,
    }


def _valid_carrier_hashes(previous):
    return isinstance(previous, dict) and all(
        isinstance(path, str)
        and isinstance(value, str)
        and len(value) == 64
        and all(c in "0123456789abcdef" for c in value)
        for path, value in previous.items()
    )


def _startup_refresh(
    binding,
    reuse,
    before,
    watcher_guarded,
    witness,
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        ADAPTERS_C30__shared import (
        native_carrier_hashes,
    )  # fmt: skip

    previous = reuse.carrier_hashes
    if not _valid_carrier_hashes(previous):
        return None
    try:
        current = native_carrier_hashes(binding)
        paths = sorted(
            path
            for path in previous.keys() | current.keys()
            if previous.get(path) != current.get(path)
        )
        if len(paths) > 1024:
            return None
        delta = _ticket_delta(binding, reuse, paths) if paths else None
        if paths and (
            delta is None
            or delta.get("carrier_hashes")
            != {path: current[path] for path in paths if path in current}
        ):
            return None
        if (
            not watcher_guarded and native_carrier_hashes(binding) != current
        ) or witness(binding, reuse.graph_config) != before:
            return None
        return (
            delta
            if paths
            else {"base_generation": reuse.base_generation, "unchanged": True}
        )
    except OSError, RuntimeError, TypeError, ValueError:
        return None


def _scope_hashes(hashes, control, *, archive):
    def is_archive(name):
        parts = PurePosixPath(name).parts
        return (
            len(parts) > 2
            and parts[0] == control
            and "09_archived" in parts[1:-1]
        )

    return {
        name: value
        for name, value in hashes.items()
        if is_archive(name) == archive
    }


def _representable(binding, paths):
    pattern = re.compile(
        r"[A-Z][A-Z0-9]*-[STPC]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?[-.].*\.md\Z"
    )
    for value in paths:
        path = PurePosixPath(value)
        if (
            not pattern.fullmatch(path.name)
            or "-PROJECT_MANIFEST--" in path.name
        ):
            return False
        if len(path.parts) > 1 and path.parts[0] != binding["control_root"]:
            return False
    return True


def _startup_delta(binding, reuse, current, paths, *, archive):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        ADAPTERS_C30__shared import (
        capture_carrier_delta,
    )  # fmt: skip

    result = capture_carrier_delta(
        binding,
        paths,
        reuse.endpoints,
        include_hashes=True,
        **_domain_option(reuse),
    )
    if result["carrier_hashes"] != {
        path: current[path] for path in paths if path in current
    }:
        raise ValueError("Carrier changed during incremental capture")
    if archive and any(
        row["status_group"] != "Archived"
        for row in result["snapshot"]["atoms"]
    ):
        raise ValueError("Archive inventory contains a non-Archived Atom")
    return {
        "base_generation": reuse.base_generation,
        "snapshot_sha256": digest(result),
        **result,
    }


def _mark_load_start(foreground, archive, paths, validation_ns, comparison_ns):
    if foreground and not archive:
        mark_startup_timing(
            "non_archived_load_started",
            changed_paths=len(paths),
            checkpoint_validation_ns=validation_ns,
            comparison_ns=comparison_ns,
        )


def _startup_carriers(binding, reuse, foreground, archive_roots):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        ADAPTERS_C30__shared import (
        UnrepresentableCarrierDelta,
        native_carrier_hashes,
    )  # fmt: skip

    archive = archive_roots is not None
    schema = reuse.inputs.get("carrier_schema")
    if (
        not isinstance(schema, str)
        or not re.fullmatch(r"[0-9a-f]{64}", schema)
        or schema != carrier_schema()
    ):
        return None
    started = monotonic_ns()
    previous, folders = reuse.carrier_hashes, reuse.folder_hashes
    try:
        if folder_hashes(previous) != folders:
            return None
    except TypeError, ValueError:
        return None
    previous = (
        _scope_hashes(previous, binding["control_root"], archive=archive)
        if foreground or archive
        else previous
    )
    validation_ns = monotonic_ns() - started
    try:
        current = native_carrier_hashes(
            binding,
            foreground=foreground,
            archive_roots=archive_roots,
            watcher_guarded=True,
        )
    except OSError, UnrepresentableCarrierDelta:
        return None
    started = monotonic_ns()
    paths = changed_paths(previous, current)
    comparison_ns = monotonic_ns() - started
    _mark_load_start(foreground, archive, paths, validation_ns, comparison_ns)
    return current, paths
