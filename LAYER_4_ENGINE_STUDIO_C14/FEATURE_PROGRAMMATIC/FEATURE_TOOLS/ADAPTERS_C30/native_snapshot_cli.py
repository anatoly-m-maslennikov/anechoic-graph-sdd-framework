"""Capture a pinned native snapshot for the Beta worker CLI."""

import json
import sys
from hashlib import sha256
from time import monotonic


from .ADAPTERS_C30__pub import LimitReached
from .native_carrier_inventory import (
    archive_versions as scan_archive_versions,
    startup_reader,
)
from .native_carrier_placement__pub import (
    TICKET_DIRECTORY,
)
from .native_generation_snapshot import snapshot
from .model_capture import model_inputs
from .native_status_domains import status_domains
from .native_source_rows__pub import (
    _native_carrier_hashes,
    capture_native,
)

from .native_snapshot_delta import (
    UnrepresentableCarrierDelta as UnrepresentableCarrierDelta,
    capture_delta,
)
from .native_snapshot_prepare import (
    initial_capture,
    make_finish,
    generation_result,
)
from .native_snapshot_finish import (
    NativeSnapshotChanged as NativeSnapshotChanged,
    finish_snapshot,
)
from .native_snapshot_paths import (
    _SnapshotSelection as _SnapshotSelection,
    _archive_directories as _archive_directories,
    _carrier_paths as _carrier_paths,
    _partition_archived as _partition_archived,
    _relative as _relative,
    _selection as _selection,
    _ticket_paths as _ticket_paths,
    _ticket_versions as _ticket_versions,
)
from .native_snapshot_serialization import (
    _encode as _encode,
    _graph_config as _graph_config,
    _snapshot as _snapshot,
)

_FIELDS = {
    "root",
    "control_root",
    "manifest_path",
    "manifest_sha256",
    "project_prefix",
}
_TICKET_TREES = {TICKET_DIRECTORY, "001_TICKETS", "__TKT"}
_MAX_TICKET_DELTA_PATHS = 1024


def _capture(binding):
    selection = _selection(binding)
    capture = capture_native(selection)
    return selection, capture, _graph_config(selection)


def native_carrier_hashes(
    binding, *, foreground=False, archive_roots=None, watcher_guarded=False
):
    """Hash selected native carriers without parsing them."""
    if foreground and archive_roots is not None:
        raise ValueError("Conflicting native inventory scopes")
    selection = _selection(binding)
    roots = (
        _archive_directories(selection, archive_roots)
        if archive_roots is not None
        else None
    )
    try:
        return _native_carrier_hashes(
            selection,
            foreground=foreground,
            archive_roots=roots,
            watcher_guarded=watcher_guarded,
        )
    except LimitReached as error:
        if error.limit != "max_file_bytes":
            raise
        raise UnrepresentableCarrierDelta(
            "Carrier exceeds the per-file read limit"
        ) from error


def _snapshot_functions():
    return (
        _selection,
        startup_reader,
        _archive_directories,
        capture_native,
        _partition_archived,
        scan_archive_versions,
    )


def _snapshot_finish_functions():
    return (
        startup_reader,
        capture_native,
        status_domains,
        _partition_archived,
        snapshot,
        monotonic,
    )


def _generation_output(context, archive_stage, finish, flags):
    include_model_inputs, include_spec_rows = flags
    return generation_result(
        context[0],
        context[2],
        archive_stage,
        finish,
        include_model_inputs,
        include_spec_rows,
        _graph_config,
        model_inputs,
    )


def prepare_generation_snapshot(
    binding,
    *,
    include_hashes=False,
    watcher_guarded=False,
    archive_stage=None,
    archive_roots=(),
    include_model_inputs=False,
    archive_versions=None,
    include_spec_rows=False,
    domains=None,
):
    """Capture once and recheck versions and membership before use.

    A continuously guarded caller can own reconciliation. Startup can defer
    archive directories and retain parsed off-path Archives.
    """
    if archive_stage not in (None, "foreground", "archive") or (
        archive_roots and archive_stage != "archive"
    ):
        raise ValueError("Invalid generation archive stage")
    flags = (include_model_inputs, include_spec_rows)
    context = initial_capture(
        binding,
        archive_stage,
        archive_roots,
        archive_versions,
        domains,
        _snapshot_functions(),
    )
    finish_context = (
        binding,
        *context[:7],
        domains,
        archive_stage,
        watcher_guarded,
        include_hashes,
        context[7],
    )
    finish = make_finish(
        finish_context, finish_snapshot, _snapshot_finish_functions
    )

    return _generation_output(context, archive_stage, finish, flags)


def _capture_delta(
    binding,
    selection,
    relatives,
    endpoints,
    *,
    include_hashes,
    ticket_only,
    manifest_admitted=False,
    domains=None,
):
    return capture_delta(
        binding,
        selection,
        relatives,
        endpoints,
        include_hashes=include_hashes,
        ticket_only=ticket_only,
        manifest_admitted=manifest_admitted,
        domains=domains,
        capture_native=capture_native,
        snapshot=snapshot,
    )


def capture_ticket_delta(
    binding,
    paths,
    endpoints,
    *,
    include_hashes=False,
    manifest_admitted=False,
    domains=None,
):
    """Capture requested Ticket files and retain absent paths for deletion."""
    selection = _selection(binding, manifest_admitted=manifest_admitted)
    return _capture_delta(
        binding,
        selection,
        _ticket_paths(selection, paths),
        endpoints,
        include_hashes=include_hashes,
        ticket_only=True,
        manifest_admitted=manifest_admitted,
        domains=domains,
    )


def capture_carrier_delta(
    binding,
    paths,
    endpoints,
    *,
    include_hashes=False,
    manifest_admitted=False,
    domains=None,
):
    """Capture canonical carriers and retain absent paths for deletion."""
    selection = _selection(binding, manifest_admitted=manifest_admitted)
    return _capture_delta(
        binding,
        selection,
        _carrier_paths(selection, paths),
        endpoints,
        include_hashes=include_hashes,
        ticket_only=False,
        manifest_admitted=manifest_admitted,
        domains=domains,
    )


def _print_snapshot(capture, result, graph_config):
    raw = json.dumps(
        [capture.versions, capture.atoms, capture.containment],
        sort_keys=True,
        separators=(",", ":"),
        default=_encode,
    ).encode()
    print(
        json.dumps(
            {
                "snapshot": result,
                "stability_sha256": sha256(raw).hexdigest(),
                "graph_config": graph_config,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )


def main():
    try:
        request = json.load(sys.stdin)
        expanded = isinstance(request, dict) and set(request) == {
            "binding",
            "endpoints",
        }
        binding = request["binding"] if expanded else request
        selection, capture, graph_config = _capture(binding)
        if expanded:
            manifest_path = selection.manifest_path.relative_to(
                selection.root
            ).as_posix()
            result = snapshot(
                binding,
                capture,
                request["endpoints"],
                manifest_path=manifest_path,
            )
        else:
            if capture.errors:
                raise ValueError(
                    "Native capture failed: "
                    + json.dumps(capture.errors, sort_keys=True)
                )
            result = _snapshot(binding, capture)
        _print_snapshot(capture, result, graph_config)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
