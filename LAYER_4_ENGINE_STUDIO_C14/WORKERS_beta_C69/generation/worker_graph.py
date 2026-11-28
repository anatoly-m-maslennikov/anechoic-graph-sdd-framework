"""Build, replay, and revalidate the Realization Graph."""

import json
import sys

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.sources__shared import (
    mark_startup_timing,
)

from WORKERS_beta_C69.refresh.native_refresh import artifact_inputs, digest, reusable_graph
from WORKERS_beta_C69.generation.worker_compile import _BuildFailure, _run_job


def _build_graph(binding, config, structure, *, replay_graph=False):
    if config is None:
        mark_startup_timing("realization_graph_ready", mode="disabled")
        return None
    module = "WORKERS_beta_C69.realization_graph"
    payload = {
        "root": binding["root"],
        "config": config,
        "control_root": binding["control_root"],
        "structure": structure,
    }
    arguments = ("--watcher-replay",) if replay_graph else ()
    try:
        graph = _run_job(module, payload, *arguments)
        mark_startup_timing("realization_graph_ready", mode="built")
        return graph
    except _BuildFailure as error:
        if error.graph_consistency is None:
            raise
        evidence = json.dumps(
            error.graph_consistency, ensure_ascii=True, separators=(",", ":")
        )
        if len(evidence) < 4096:
            print(
                "\nanechoic-realization-graph-restart " + evidence,
                file=sys.stderr,
            )
    try:
        graph = _run_job(module, payload, *arguments)
        mark_startup_timing("realization_graph_ready", mode="built")
        return graph
    except _BuildFailure as error:
        if error.graph_consistency is None:
            raise
        raise _BuildFailure(
            "realization_graph",
            f"{error} after one Realization Graph restart",
            graph_consistency=error.graph_consistency,
        ) from None


def _rebuild_graph(
    binding,
    config,
    structure,
    endpoints,
    *,
    watcher_guarded=False,
    replay_graph=False,
    domains=None,
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        ADAPTERS_C30__shared import (
        prepare_generation_snapshot,
    )  # fmt: skip

    current_config, finish_snapshot = prepare_generation_snapshot(
        binding,
        include_hashes=True,
        watcher_guarded=watcher_guarded,
        domains=domains,
    )
    if current_config != config:
        return None
    graph = _build_graph(binding, config, structure, replay_graph=replay_graph)
    if graph is None:
        return None
    snapshot, hashes = finish_snapshot(endpoints)
    return snapshot, graph, hashes


def _graph_only(binding, reuse, structure, guarded, force=False):
    if (
        reuse is None
        or reuse.graph_config is None
        or not isinstance(structure, dict)
    ):
        raise ValueError(
            "Graph-only capture requires reuse, graph config, and structure"
        )
    config = reuse.graph_config
    before = artifact_inputs(binding, config, watcher_guarded=guarded)
    if (
        before is None
        or before.get("manifest") != reuse.inputs.get("manifest")
        or before.get("carrier_schema") != reuse.inputs.get("carrier_schema")
    ):
        raise ValueError("Core artifact inputs changed before graph capture")
    if before == reuse.inputs and not force:
        mark_startup_timing("realization_graph_ready", mode="reused")
        return {"base_generation": reuse.base_generation, "unchanged": True}
    graph = _build_graph(binding, config, structure)
    if (
        not reusable_graph(graph)
        or artifact_inputs(binding, config, watcher_guarded=guarded) != before
    ):
        raise ValueError("Graph inputs changed during capture")
    return {
        "base_generation": reuse.base_generation,
        "graph": graph,
        "graph_sha256": digest(graph),
        "reuse": {
            "inputs": before,
            "graph_config": config,
            "endpoints": reuse.endpoints,
        },
    }
