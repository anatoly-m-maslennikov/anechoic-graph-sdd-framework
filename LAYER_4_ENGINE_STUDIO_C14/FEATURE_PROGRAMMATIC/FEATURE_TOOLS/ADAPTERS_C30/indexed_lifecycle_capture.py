"""Build bounded lifecycle capture from indexed carrier evidence."""

from dataclasses import field
from pathlib import PurePosixPath
import os
import re
import stat
from typing import Any

from pydantic import field_validator
from pydantic.dataclasses import dataclass

from .ADAPTERS_C30__pub import ReadContext, open_regular
from .atom_reference__pub import derive_atom_ref
from .native_carrier_header__pub import native_header_view
from .native_carrier_placement__pub import project_goal_filename
from .native_status_domains import status_domains as default_status_domains
from .native_source_rows__pub import (
    NativeCapture,
    _container,
    _preserve_capture_data,
    capture_native,
)


@dataclass(frozen=True)
class IndexedLifecycleCapture(NativeCapture):
    carriers: tuple[dict[str, Any], ...] = ()
    max_numbers: dict[str, int] = field(default_factory=dict)
    lenses: tuple[str, ...] = ()
    max_archived_version: int = 0

    _validate_index_facts = field_validator(
        "carriers", "max_numbers", "lenses", mode="wrap"
    )(_preserve_capture_data)


def capture_indexed_lifecycle(
    selection: Any,
    carriers,
    max_numbers,
    *,
    lenses=(),
    max_archived_version=0,
    domains=None,
) -> IndexedLifecycleCapture:
    "Capture addressed carriers and retain index facts for lifecycle guards."
    if (
        type(max_archived_version) is not int
        or not 0 <= max_archived_version <= 2**63 - 1
        or not isinstance(carriers, (list, tuple))
        or not isinstance(max_numbers, dict)
        or not set(max_numbers) <= {"T", "S"}
        or any(
            not isinstance(value, str)
            or not re.fullmatch(r"0|[1-9][0-9]*", value)
            for value in max_numbers.values()
        )
        or not isinstance(lenses, (list, tuple))
        or any(not isinstance(lens, str) or not lens for lens in lenses)
    ):
        raise ValueError("Invalid indexed lifecycle facts")
    descriptors = _validate_descriptors(selection, carriers, domains)
    return _capture(
        selection,
        descriptors,
        max_numbers,
        lenses,
        max_archived_version,
        domains,
    )


def _validate_descriptors(selection, carriers, domains):
    fields = {
        "ref",
        "_exact_ref",
        "source_path",
        "version",
        "status",
        "status_group",
        "id",
        "owner_kind",
        "owner_ref",
        "read",
    }
    domains = domains or default_status_domains({})
    descriptors, paths, exacts = [], set(), set()
    for item in carriers:
        if (
            not isinstance(item, dict)
            or set(item) != fields
            or type(item["read"]) is not bool
        ):
            raise ValueError("Invalid indexed carrier descriptor")
        row = dict(item)
        path = row["source_path"]
        _validate_descriptor_path(selection, path, paths)
        _validate_descriptor_identity(selection, row, domains, exacts)
        paths.add(path)
        exacts.add(row["_exact_ref"])
        descriptors.append(row)
    return descriptors


def _validate_descriptor_identity(selection, row, domains, exacts):
    atom_id = row["id"]
    match = (
        re.fullmatch(
            re.escape(selection.project_prefix) + r"-([STPC])-[0-9]+",
            atom_id,
        )
        if isinstance(atom_id, str)
        else None
    )
    version, status, group = (
        row["version"],
        row["status"],
        row["status_group"],
    )
    if (
        match is None
        or type(version) is not int
        or version < 1
        or not isinstance(status, str)
        or group not in {"Current", "Draft", "Archived"}
        or status not in domains[match[1]]
        or group
        != (status.title() if status in ("draft", "archived") else "Current")
        or row["_exact_ref"] != derive_atom_ref(atom_id, version, status)
        or row["ref"] != (atom_id if group == "Current" else row["_exact_ref"])
        or row["_exact_ref"] in exacts
    ):
        raise ValueError("Invalid indexed carrier identity")
    _container(
        {str(row["owner_kind"]).lower(): row["owner_ref"]},
        atom_id,
        re.escape(selection.project_prefix) + r"-([STPC])-[0-9]+",
    )


def _validate_descriptor_path(selection, path, paths):
    if (
        not isinstance(path, str)
        or not path
        or str(PurePosixPath(path)) != path
        or path.startswith("/")
        or "\\" in path
        or ".." in PurePosixPath(path).parts
        or not path.endswith(".md")
        or not (
            (selection.root / path).is_relative_to(selection.control_root)
            or (
                PurePosixPath(path).parent == PurePosixPath(".")
                and project_goal_filename(PurePosixPath(path).name)
            )
        )
        or (selection.root / path).is_relative_to(
            selection.control_root / "000_ANECHOIC_framework"
        )
        or selection.root / path == selection.manifest_path
        or path in paths
    ):
        raise ValueError("Invalid indexed carrier path")


def _capture(
    selection, descriptors, max_numbers, lenses, max_archived_version, domains
):
    wanted = {
        PurePosixPath(row["source_path"]) for row in descriptors if row["read"]
    }
    captured = capture_native(
        selection,
        previous=NativeCapture([], [], {}),
        paths=wanted,
        manifest_admitted=True,
        include_content_properties=False,
        domains=domains,
    )
    if captured.errors or len(captured.atoms) != len(wanted):
        raise ValueError("Indexed carrier is missing or unreadable")
    by_path = {row["source_path"]: row for row in captured.atoms}
    rows, edges = [], []
    for item in descriptors:
        row, kind = _captured_row(item, by_path)
        rows.append(row)
        edges.append(
            {
                "source_kind": "Atom",
                "source_ref": row["ref"],
                "relation_type": "CONTAINED_BY",
                "target_kind": kind.title(),
                "target_ref": item["owner_ref"],
                "derived": False,
            }
        )
    return IndexedLifecycleCapture(
        rows,
        edges,
        {},
        captured.versions,
        tuple(descriptors),
        {key: int(value) for key, value in max_numbers.items()},
        tuple(lenses),
        max_archived_version,
        status_domains=domains,
    )


def _captured_row(item, by_path):
    kind = item["owner_kind"].lower()
    if item["read"]:
        row = by_path[item["source_path"]]
        if any(
            row.get(key) != item[key]
            for key in (
                "ref",
                "_exact_ref",
                "source_path",
                "version",
                "status",
                "status_group",
                "id",
            )
        ) or native_header_view(row["header_json"]).get("context", {}).get(
            "container"
        ) != {kind: item["owner_ref"]}:
            raise ValueError("Indexed carrier changed")
    else:
        row = {
            key: item[key]
            for key in (
                "ref",
                "_exact_ref",
                "source_path",
                "version",
                "status",
                "status_group",
                "id",
            )
        }
        row["_source_sha256"] = None
        row["header_json"] = {
            "context": {"container": {kind: item["owner_ref"]}}
        }
    return row, kind


def revalidate_indexed_lifecycle(selection, capture):
    """Check the exact admitted files without reading carrier content again."""
    for item in capture.carriers:
        if not item["read"]:
            continue
        path = selection.root / item["source_path"]
        expected = capture.versions.get(str(path))
        if expected is None:
            raise ValueError("Indexed carrier has no version witness")
        try:
            descriptor = open_regular(path)
            try:
                info = os.fstat(descriptor)
                if (
                    not stat.S_ISREG(info.st_mode)
                    or ReadContext.version(info) != expected
                ):
                    raise ValueError("Indexed carrier changed")
            finally:
                os.close(descriptor)
        except OSError as error:
            raise ValueError("Indexed carrier missing or changed") from error
    return capture
