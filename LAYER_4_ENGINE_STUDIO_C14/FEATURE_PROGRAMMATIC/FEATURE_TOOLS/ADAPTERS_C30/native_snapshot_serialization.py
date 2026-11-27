"""Support native snapshot projection."""

import base64
from .ADAPTERS_C30__pub import CEILINGS, ReadContext
from .carrier_read__pub import parse_carrier
from .native_generation_snapshot import row_summary
from .native_source_rows__pub import check_native_manifest
from .project_manifest__pub import manifest_inputs


def _graph_config(selection):
    reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    raw = check_native_manifest(reader, selection, None)
    path = selection.manifest_path
    fields, _ = manifest_inputs(path, parse_carrier(raw, path))
    config = fields.get("parameters", {})
    if not isinstance(config, dict):
        raise ValueError("Invalid runtime Project settings")
    config = config.get("runtime", {})
    if not isinstance(config, dict):
        raise ValueError("Invalid import graph Project settings")
    config = config.get("iwe_console", config.get("workbench", {}))
    if not isinstance(config, dict):
        raise ValueError("Invalid import graph Project settings")
    graph = config.get("import_graph", {})
    if graph is not False and not isinstance(graph, dict):
        raise ValueError("Invalid import graph Project settings")
    if reader.currentness()["state"] != "unchanged":
        raise ValueError("Project Manifest changed during capture")
    return None if graph is False else graph


def _snapshot(binding, capture):
    atoms = []
    for row in capture.atoms:
        if row["status_group"] != "Current":
            continue
        atoms.append({"reference": row["ref"], "summary": row_summary(row)})
    return {
        "manifest_sha256": binding["manifest_sha256"],
        "atoms": sorted(atoms, key=lambda item: item["reference"]),
    }


def _encode(value):
    if isinstance(value, bytes):
        return {"__bytes_base64__": base64.b64encode(value).decode("ascii")}
    raise TypeError(
        "Unsupported native capture value: " + type(value).__name__
    )
