"""Revalidate the inputs to the artifacts from the last admitted generation."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    mark_startup_timing,
)  # fmt: skip

from .refresh_carriers import (
    _representable,
    _startup_carriers,
    _startup_delta,
    _startup_refresh,
    _ticket_delta as _ticket_delta,
)
from .refresh_inputs import (
    _domain_option as _domain_option,
    _ReuseHint as _ReuseHint,
    _reuse_hint as _reuse_hint,
    artifact_inputs as artifact_inputs,
    carrier_schema as carrier_schema,
    digest as digest,
    reusable_graph as reusable_graph,
)


def _require_same_inputs(binding, reuse, before, defer_graph):
    graph_option = {"defer_graph": True} if defer_graph else {}
    if (
        before is not None
        and artifact_inputs(
            binding, reuse.graph_config, watcher_guarded=True, **graph_option
        )
        != before
    ):
        raise ValueError("Artifact inputs changed during incremental capture")


def startup_incremental(
    binding,
    reuse,
    *,
    before=None,
    foreground=False,
    archive_roots=None,
    watcher_guarded=False,
    defer_graph=False,
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        ADAPTERS_C30__shared import (
        UnrepresentableCarrierDelta,
    )  # fmt: skip

    archive = archive_roots is not None
    incompatible = {"incompatible": True} if archive else None
    if not watcher_guarded or reuse is None:
        return incompatible
    changed = _startup_carriers(
        binding,
        reuse,
        foreground,
        archive_roots,
    )
    if changed is None:
        return incompatible
    current, paths = changed
    if len(paths) > 1024 or not _representable(binding, paths):
        return incompatible
    if not paths:
        result = {"base_generation": reuse.base_generation, "unchanged": True}
    else:
        try:
            result = _startup_delta(
                binding, reuse, current, paths, archive=archive
            )
        except UnrepresentableCarrierDelta:
            return incompatible
    _require_same_inputs(binding, reuse, before, defer_graph)
    return result


def _mark_reused(foreground, config, *, graph=True):
    if foreground:
        mark_startup_timing("model_ready", mode="reused")
        mark_startup_timing("structure_ready", mode="reused")
        if graph:
            mark_startup_timing(
                "realization_graph_ready",
                mode="disabled" if config is None else "reused",
            )


def _compile_receipt(binding, output, compile_artifacts):
    with TemporaryDirectory(
        prefix=".beta-compile-", dir=Path(output).parent
    ) as temporary:
        stage = Path(temporary)
        receipt, _, endpoints = compile_artifacts(binding, stage)
        compiler = {
            "receipt": receipt,
            "model": (stage / "model.json").read_text(encoding="utf-8"),
            "structure": (stage / "structure.json").read_text(
                encoding="utf-8"
            ),
        }
    return compiler, endpoints


def _compile_refresh(binding, reuse, before, output, compile_artifacts):
    compiler, endpoints = _compile_receipt(binding, output, compile_artifacts)
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        ADAPTERS_C30__shared import (
        status_domains,
    )  # fmt: skip

    domains = status_domains(json.loads(compiler["model"])["bindings"])
    if domains != _domain_option(reuse).get("domains", status_domains({})):
        return None
    candidate = reuse.model_copy(update={"endpoints": endpoints})
    delta = startup_incremental(
        binding,
        candidate,
        before=before,
        foreground=True,
        watcher_guarded=True,
        defer_graph=True,
    )
    if delta is None:
        return None
    result = {
        "base_generation": reuse.base_generation,
        "compiler": compiler,
        "reuse": {
            "inputs": before,
            "graph_config": reuse.graph_config,
            "endpoints": endpoints,
        },
    }
    if not delta.get("unchanged"):
        result["delta"] = {
            key: value
            for key, value in delta.items()
            if key != "base_generation"
        }
    return result


def deferred_incremental(
    binding, reuse, foreground, guarded, output, compile_artifacts
):
    if reuse is None:
        return None
    before = artifact_inputs(
        binding, reuse.graph_config, watcher_guarded=guarded, defer_graph=True
    )
    if before is None or before.get("carrier_schema") != reuse.inputs.get(
        "carrier_schema"
    ):
        return None
    if before.get("manifest") != reuse.inputs.get("manifest"):
        if foreground and guarded and compile_artifacts is not None:
            return _compile_refresh(
                binding, reuse, before, output, compile_artifacts
            )
        return None
    result = startup_incremental(
        binding,
        reuse,
        before=before,
        foreground=foreground,
        watcher_guarded=guarded,
        defer_graph=True,
    )
    if result is not None:
        _mark_reused(foreground, reuse.graph_config, graph=False)
    return result


def _incremental_reuse(binding, reuse, before, foreground, watcher_guarded):
    result = startup_incremental(
        binding,
        reuse,
        before=before,
        foreground=foreground,
        watcher_guarded=watcher_guarded,
    )
    if result is not None:
        _mark_reused(foreground, reuse.graph_config)
    return result


def _graph_inputs_changed(before, reuse, config, structure, rebuild_graph):
    return not (
        not isinstance(structure, dict)
        or rebuild_graph is None
        or config is None
        or set(before) != {"manifest", "graph", "carrier_schema"}
        or set(reuse.inputs) != set(before)
        or before["carrier_schema"] != reuse.inputs["carrier_schema"]
        or before["manifest"] != reuse.inputs["manifest"]
        or before["graph"] == reuse.inputs["graph"]
    )


def _refresh_graph(
    binding,
    reuse,
    before,
    structure,
    rebuild_graph,
    watcher_guarded,
    mark_progress,
):
    config = reuse.graph_config
    if not _graph_inputs_changed(
        before, reuse, config, structure, rebuild_graph
    ):
        return None
    result = rebuild_graph(
        binding, config, structure, reuse.endpoints, **_domain_option(reuse)
    )
    if result is None:
        return None
    snapshot, graph, carrier_hashes = result
    if (
        not reusable_graph(graph)
        or artifact_inputs(binding, config, watcher_guarded=watcher_guarded)
        != before
    ):
        return None
    _mark_reused(mark_progress, config, graph=False)
    return {
        "base_generation": reuse.base_generation,
        "snapshot": snapshot,
        "snapshot_sha256": digest(snapshot),
        "graph": graph,
        "graph_sha256": digest(graph),
        "reuse": {
            "inputs": before,
            "graph_config": config,
            "endpoints": reuse.endpoints,
        },
        "carrier_hashes": carrier_hashes,
    }


def _capture_reusable(
    binding, reuse, capture, config, before, watcher_guarded
):
    result = capture(binding, reuse.endpoints, **_domain_option(reuse))
    if (
        result["graph_config"] != config
        or artifact_inputs(binding, config, watcher_guarded=watcher_guarded)
        != before
    ):
        return None
    snapshot = result["snapshot"]
    return {
        "base_generation": reuse.base_generation,
        "snapshot": snapshot,
        "snapshot_sha256": digest(snapshot),
        "carrier_hashes": result["carrier_hashes"],
    }


def refresh(
    binding,
    reuse,
    capture,
    paths=None,
    structure=None,
    rebuild_graph=None,
    *,
    watcher_guarded=False,
    incremental=False,
    foreground=False,
):
    if reuse is None:
        return None
    if paths is not None:
        delta = _ticket_delta(binding, reuse, paths)
        if delta is not None:
            return delta
    config = reuse.graph_config
    before = artifact_inputs(binding, config, watcher_guarded=watcher_guarded)
    if before is None:
        return None
    if before != reuse.inputs:
        return _refresh_graph(
            binding,
            reuse,
            before,
            structure,
            rebuild_graph,
            watcher_guarded,
            foreground and incremental,
        )
    if incremental and paths is None:
        return _incremental_reuse(
            binding, reuse, before, foreground, watcher_guarded
        )
    if paths is None and "carrier_hashes" in reuse.model_fields_set:
        startup = _startup_refresh(
            binding, reuse, before, watcher_guarded, artifact_inputs
        )
        if startup is not None:
            return startup
    return _capture_reusable(
        binding, reuse, capture, config, before, watcher_guarded
    )
