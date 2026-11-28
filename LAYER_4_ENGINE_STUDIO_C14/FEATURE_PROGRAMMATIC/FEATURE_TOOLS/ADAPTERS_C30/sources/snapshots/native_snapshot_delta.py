"""Capture addressed native carrier deltas."""

import re
from ...sources.capture.native_capture_types import NativeCapture
from ...sources.snapshots.native_snapshot_paths import _ticket_versions


class UnrepresentableCarrierDelta(ValueError):
    pass


def _validate_delta_rows(selection, capture, failed, versions, ticket_only):
    ticket = re.compile(rf"{re.escape(selection.project_prefix)}-T-[0-9]+")
    captured_paths = set()
    for row in capture.atoms:
        if ticket_only and not ticket.fullmatch(row["id"]):
            raise ValueError("Ticket delta contains a non-Ticket Atom")
        header = row["header_json"]
        if not ticket_only and (
            header.get("atom_family") not in {"SPEC", "TKT", "PROJECT_CONFIG"}
            or header.get("context", {}).get("template") == "project_manifest"
        ):
            raise UnrepresentableCarrierDelta(
                "Carrier delta contains a non-canonical carrier "
                "or Project Manifest"
            )
        captured_paths.add(str(selection.root / row["source_path"]))
    if captured_paths | (failed & versions.keys()) != versions.keys():
        raise ValueError("Ticket delta rows do not match the changed paths")


def _check_delta_versions(selection, relatives, capture, paths_before):
    versions = _ticket_versions(selection.root, relatives)
    observed = {
        path: version
        for path, version in capture.versions.items()
        if path != str(selection.manifest_path)
    }
    failed = {str(selection.root / path) for path in capture.errors}
    expected = {
        path: version
        for path, version in versions.items()
        if path in observed or path not in failed
    }
    if observed != expected or versions.keys() != paths_before:
        raise ValueError("Ticket delta paths changed during capture")
    return failed, versions


def capture_delta(
    binding,
    selection,
    relatives,
    endpoints,
    *,
    include_hashes,
    ticket_only,
    manifest_admitted=False,
    domains=None,
    capture_native,
    snapshot,
):
    paths_before = _ticket_versions(selection.root, relatives).keys()
    capture = capture_native(
        selection,
        previous=NativeCapture([], [], {}),
        paths=relatives,
        manifest_admitted=manifest_admitted,
        include_content_properties="summary",
        domains=domains,
    )
    failed, versions = _check_delta_versions(
        selection, relatives, capture, paths_before
    )
    _validate_delta_rows(selection, capture, failed, versions, ticket_only)
    manifest_path = selection.manifest_path.relative_to(
        selection.root
    ).as_posix()
    result = {
        "paths": [
            [path.parent.as_posix(), path.name] for path in sorted(relatives)
        ],
        "snapshot": snapshot(
            binding, capture, endpoints, manifest_path=manifest_path
        ),
    }
    if include_hashes:
        result["carrier_hashes"] = capture.carrier_hashes
    return result
