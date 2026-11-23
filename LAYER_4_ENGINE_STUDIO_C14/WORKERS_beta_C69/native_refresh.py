"""Revalidate the inputs to the artifacts from the last admitted generation."""

import json
from hashlib import sha256
from pathlib import Path

_GRAPH_ANALYZERS = ("realization_graph.py", "python_code_units.py", "web_code_units.mjs")


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def artifact_inputs(binding, config):
    from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import (
        graph_input_signature,
    )

    from .manifest_build_CS4.manifest_build_CS4__shared import manifest_input_signature

    manifest = manifest_input_signature(binding)
    if manifest is None:
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
    return {"manifest": manifest, "graph": graph}


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
                                  {"base_generation", "inputs", "endpoints", "graph_config", "carrier_hashes"})
            or not isinstance(reuse["base_generation"], str) or not reuse["base_generation"]
            or not isinstance(reuse["inputs"], dict) or not isinstance(reuse["endpoints"], dict))


def _startup_refresh(binding, reuse, before):
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
        if native_carrier_hashes(binding) != current or artifact_inputs(binding, reuse["graph_config"]) != before:
            return None
        return delta if paths else {"base_generation": reuse["base_generation"], "unchanged": True}
    except (OSError, RuntimeError, TypeError, ValueError):
        return None


def refresh(binding, reuse, capture, paths=None, structure=None, rebuild_graph=None):
    if not valid_reuse(reuse):
        return None
    if paths is not None:
        delta = _ticket_delta(binding, reuse, paths)
        if delta is not None:
            return delta
    config = reuse["graph_config"]
    before = artifact_inputs(binding, config)
    if before is None:
        return None
    if before != reuse["inputs"]:
        if (not isinstance(structure, dict) or rebuild_graph is None or config is None
                or set(before) != {"manifest", "graph"} or set(reuse["inputs"]) != {"manifest", "graph"}
                or before["manifest"] != reuse["inputs"]["manifest"]
                or before["graph"] == reuse["inputs"]["graph"]):
            return None
        result = rebuild_graph(binding, config, structure, reuse["endpoints"])
        if result is None or artifact_inputs(binding, config) != before:
            return None
        snapshot, graph, carrier_hashes = result
        return {"base_generation": reuse["base_generation"], "snapshot": snapshot,
                "snapshot_sha256": digest(snapshot), "graph": graph, "graph_sha256": digest(graph),
                "reuse": {"inputs": before, "graph_config": config, "endpoints": reuse["endpoints"]},
                "carrier_hashes": carrier_hashes}
    if paths is None and "carrier_hashes" in reuse:
        startup = _startup_refresh(binding, reuse, before)
        if startup is not None:
            return startup
    result = capture(binding, reuse["endpoints"])
    if result["graph_config"] != config or artifact_inputs(binding, config) != before:
        return None
    snapshot = result["snapshot"]
    return {"base_generation": reuse["base_generation"], "snapshot": snapshot, "snapshot_sha256": digest(snapshot),
            "carrier_hashes": result["carrier_hashes"]}
