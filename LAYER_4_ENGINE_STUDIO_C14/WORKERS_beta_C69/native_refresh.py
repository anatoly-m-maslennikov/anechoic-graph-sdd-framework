"""Revalidate the inputs to the artifacts from the last admitted generation."""

import json
from hashlib import sha256
from pathlib import Path, PurePosixPath
import re

from .startup_inventory import changed_paths, folder_hashes

_GRAPH_ANALYZERS = ("realization_graph.py", "python_code_units.py", "web_code_units.mjs")


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def carrier_schema():
    engine = Path(__file__).resolve().parent.parent
    folders = (engine / "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30",
               engine / "ARCHITECTURE_ANALYSIS_C73/CODE_AND_SPEC_METRICS_C76")
    files = sorted(path for folder in folders for path in folder.glob("*.py"))
    if any(not folder.is_dir() for folder in folders) or not files:
        return None
    try:
        return digest([[path.relative_to(engine).as_posix(), sha256(path.read_bytes()).hexdigest()] for path in files])
    except OSError:
        return None


def artifact_inputs(binding, config, *, watcher_guarded=False):
    from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import (
        graph_input_signature,
    )

    from .manifest_build_CS4.manifest_build_CS4__shared import manifest_input_signature

    manifest = manifest_input_signature(binding, watcher_guarded=watcher_guarded)
    schema = carrier_schema()
    if manifest is None or schema is None:
        return None
    graph = "disabled" if config is None else graph_input_signature(Path(binding["root"]), config)
    if graph is None:
        return None
    if config is not None:
        try:
            folder = Path(__file__).resolve().parent
            analyzers = [sha256((folder / name).read_bytes()).hexdigest() for name in _GRAPH_ANALYZERS]
        except OSError:
            return None
        graph = digest([graph, *analyzers])
    return {"manifest": manifest, "graph": graph, "carrier_schema": schema}


def _ticket_delta(binding, reuse, paths, capture_ticket_delta=None):
    if capture_ticket_delta is None:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
            capture_ticket_delta,
        )

    try:
        result = capture_ticket_delta(binding, paths, reuse["endpoints"], include_hashes=True)
    except (OSError, RuntimeError, TypeError, ValueError):
        return None
    if result is None:
        return None
    return {"base_generation": reuse["base_generation"], "snapshot_sha256": digest(result), **result}


def valid_reuse(reuse):
    return not (not isinstance(reuse, dict) or set(reuse) not in ({"base_generation", "inputs", "endpoints", "graph_config"},
                                  {"base_generation", "inputs", "endpoints", "graph_config", "carrier_hashes"},
                                  {"base_generation", "inputs", "endpoints", "graph_config", "carrier_hashes", "folder_hashes"})
            or not isinstance(reuse["base_generation"], str) or not reuse["base_generation"]
            or not isinstance(reuse["inputs"], dict) or not isinstance(reuse["endpoints"], dict))


def _startup_refresh(binding, reuse, before, watcher_guarded):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_carrier_hashes

    previous = reuse["carrier_hashes"]
    if (not isinstance(previous, dict) or any(not isinstance(path, str) or not isinstance(value, str)
            or len(value) != 64 or any(c not in "0123456789abcdef" for c in value)
            for path, value in previous.items())):
        return None
    try:
        current = native_carrier_hashes(binding)
        paths = sorted(path for path in previous.keys() | current.keys() if previous.get(path) != current.get(path))
        if len(paths) > 1024:
            return None
        delta = _ticket_delta(binding, reuse, paths) if paths else None
        if paths and (delta is None or delta.get("carrier_hashes") !=
                      {path: current[path] for path in paths if path in current}):
            return None
        if ((not watcher_guarded and native_carrier_hashes(binding) != current)
                or artifact_inputs(binding, reuse["graph_config"]) != before):
            return None
        return delta if paths else {"base_generation": reuse["base_generation"], "unchanged": True}
    except (OSError, RuntimeError, TypeError, ValueError):
        return None


def _scope_hashes(hashes, control, *, archive):
    def is_archive(name):
        parts = PurePosixPath(name).parts
        return len(parts) > 2 and parts[0] == control and "09_archived" in parts[1:-1]
    return {name: value for name, value in hashes.items() if is_archive(name) == archive}


def _representable(binding, paths):
    pattern = re.compile(r"[A-Z][A-Z0-9]*-[STPC]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?[-.].*\.md\Z")
    for value in paths:
        path = PurePosixPath(value)
        if not pattern.fullmatch(path.name) or "-PROJECT_MANIFEST--" in path.name:
            return False
        if len(path.parts) > 1 and path.parts[0] != binding["control_root"]:
            return False
    return True


def startup_incremental(binding, reuse, *, before=None, foreground=False, archive_roots=None, watcher_guarded=False):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        UnrepresentableCarrierDelta, capture_carrier_delta, native_carrier_hashes,
    )

    archive = archive_roots is not None
    incompatible = {"incompatible": True} if archive else None
    if not watcher_guarded or not valid_reuse(reuse):
        return incompatible
    schema = reuse["inputs"].get("carrier_schema")
    if not isinstance(schema, str) or not re.fullmatch(r"[0-9a-f]{64}", schema) or schema != carrier_schema():
        return incompatible
    previous, folders = reuse.get("carrier_hashes"), reuse.get("folder_hashes")
    try:
        if folder_hashes(previous) != folders:
            return incompatible
    except (TypeError, ValueError):
        return incompatible
    previous = _scope_hashes(previous, binding["control_root"], archive=archive) if foreground or archive else previous
    current = native_carrier_hashes(binding, foreground=foreground, archive_roots=archive_roots, watcher_guarded=True)
    paths = changed_paths(previous, current, folder_hashes(previous))
    if len(paths) > 1024 or not _representable(binding, paths):
        return incompatible
    if not paths:
        result = {"base_generation": reuse["base_generation"], "unchanged": True}
    else:
        try:
            result = capture_carrier_delta(binding, paths, reuse["endpoints"], include_hashes=True)
        except UnrepresentableCarrierDelta:
            return incompatible
        if result["carrier_hashes"] != {path: current[path] for path in paths if path in current}:
            raise ValueError("Carrier changed during incremental capture")
        if archive and any(row["status_group"] != "Archived" for row in result["snapshot"]["atoms"]):
            raise ValueError("Archive inventory contains a non-Archived Atom")
        result = {"base_generation": reuse["base_generation"], "snapshot_sha256": digest(result), **result}
    if before is not None and artifact_inputs(binding, reuse["graph_config"], watcher_guarded=True) != before:
        raise ValueError("Artifact inputs changed during incremental capture")
    return result


def refresh(binding, reuse, capture, paths=None, structure=None, rebuild_graph=None, *, watcher_guarded=False,
            incremental=False, foreground=False):
    if not valid_reuse(reuse):
        return None
    if paths is not None:
        delta = _ticket_delta(binding, reuse, paths)
        if delta is not None:
            return delta
    config = reuse["graph_config"]
    before = artifact_inputs(binding, config, watcher_guarded=watcher_guarded)
    if before is None:
        return None
    if before != reuse["inputs"]:
        if (not isinstance(structure, dict) or rebuild_graph is None or config is None
                or set(before) != {"manifest", "graph", "carrier_schema"}
                or set(reuse["inputs"]) != set(before) or before["carrier_schema"] != reuse["inputs"]["carrier_schema"]
                or before["manifest"] != reuse["inputs"]["manifest"]
                or before["graph"] == reuse["inputs"]["graph"]):
            return None
        result = rebuild_graph(binding, config, structure, reuse["endpoints"])
        if result is None or artifact_inputs(binding, config, watcher_guarded=watcher_guarded) != before:
            return None
        snapshot, graph, carrier_hashes = result
        return {"base_generation": reuse["base_generation"], "snapshot": snapshot,
                "snapshot_sha256": digest(snapshot), "graph": graph, "graph_sha256": digest(graph),
                "reuse": {"inputs": before, "graph_config": config, "endpoints": reuse["endpoints"]},
                "carrier_hashes": carrier_hashes}
    if incremental and paths is None:
        return startup_incremental(binding, reuse, before=before, foreground=foreground,
                                   watcher_guarded=watcher_guarded)
    if paths is None and "carrier_hashes" in reuse:
        startup = _startup_refresh(binding, reuse, before, watcher_guarded)
        if startup is not None:
            return startup
    result = capture(binding, reuse["endpoints"])
    if result["graph_config"] != config or artifact_inputs(binding, config, watcher_guarded=watcher_guarded) != before:
        return None
    snapshot = result["snapshot"]
    return {"base_generation": reuse["base_generation"], "snapshot": snapshot, "snapshot_sha256": digest(snapshot),
            "carrier_hashes": result["carrier_hashes"]}
