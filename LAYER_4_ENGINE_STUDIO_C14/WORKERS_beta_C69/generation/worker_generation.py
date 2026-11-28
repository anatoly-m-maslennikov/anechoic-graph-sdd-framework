"""Compile and publish a Worker generation through an isolated stage."""

import os
from pathlib import Path
import tempfile

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from WORKERS_beta_C69.generation.generation_batches import _write_generation_batches
from WORKERS_beta_C69.refresh.native_refresh import artifact_inputs, digest, reusable_graph
from WORKERS_beta_C69.generation.worker_graph import _build_graph


@dataclass(
    frozen=True,
    config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True),
)
class _GenerationOptions:
    managed: bool
    watcher_guarded: bool
    foreground: bool
    replay_graph: bool
    model_source: dict | None
    batch_full: bool
    defer_graph: bool
    domains: dict | None


def _generation_graph(
    binding, config, structure, compiled, model_source, replay_graph
):
    try:
        return _build_graph(
            binding, config, structure, replay_graph=replay_graph
        )
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        if model_source is not None and compiled[3]:
            error.model_diagnostics = compiled[3]
        raise


def _publish_generation(output, identity, stage, result, batch_full):
    if batch_full:
        result["batch_artifact"] = _write_generation_batches(
            stage,
            result.pop("snapshot"),
            result.pop("graph"),
            result.pop("carrier_hashes"),
        )
    if (
        output.is_symlink()
        or not output.is_dir()
        or output.stat() != identity
        or any(output.iterdir())
    ):
        raise ValueError("Generation directory changed during build")
    os.replace(stage, output)


def _deferred_archive(deferred, endpoints, archive_versions):
    roots, archived, archive_hashes = deferred
    return {
        "roots": roots,
        "snapshot": archived,
        "carrier_hashes": archive_hashes,
        "endpoints": endpoints,
        "archive_versions": archive_versions,
    }


def _validate_output(output):
    if (
        not output.is_absolute()
        or output.is_symlink()
        or not output.is_dir()
        or output.resolve(strict=True) != output
        or any(output.iterdir())
    ):
        raise ValueError(
            "Generation directory must be an existing "
            "empty canonical directory"
        )


def _prepare_generation(binding, output, options):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
        ADAPTERS_C30__shared import (
        prepare_generation_snapshot,
    )  # fmt: skip

    output = Path(output)
    _validate_output(output)
    foreground = options.foreground
    model_source = options.model_source
    archive_versions = {}
    captured = prepare_generation_snapshot(
        binding,
        include_hashes=True,
        watcher_guarded=options.watcher_guarded,
        domains=options.domains,
        archive_stage="foreground" if foreground else None,
        **({"archive_versions": archive_versions} if foreground else {}),
        **(
            {
                "include_model_inputs": True,
                "include_spec_rows": "spec_database" in model_source,
            }
            if model_source is not None
            else {}
        ),
    )
    config, finish_snapshot = captured[:2]
    model_inputs = captured[2] if model_source is not None else None
    control = Path(binding["root"]) / binding["control_root"]
    if output == control or control in output.parents:
        raise ValueError(
            "Generation directory must be outside the Project control root"
        )
    return (
        output,
        output.stat(),
        config,
        finish_snapshot,
        model_inputs,
        archive_versions,
    )


def _compile_managed_refresh(
    output, source, domains, compile_capture, binding, stage
):
    options = _GenerationOptions(
        managed=True,
        watcher_guarded=True,
        foreground=True,
        replay_graph=False,
        model_source=source,
        batch_full=False,
        defer_graph=True,
        domains=domains,
    )
    prepared = _prepare_generation(binding, output, options)
    compiled, _ = compile_capture(
        binding, stage, prepared[4], source, prepared[3]
    )
    return compiled


def _generation_result(
    binding, config, compiled, captured, options, archive_versions
):
    receipt, structure, endpoints = compiled[:3]
    snapshot, hashes, *deferred = captured
    graph = (
        None
        if options.defer_graph and config is not None
        else _generation_graph(
            binding,
            config,
            structure,
            compiled,
            options.model_source,
            options.replay_graph,
        )
    )
    receipt["graph_sha256"] = digest(graph)
    receipt["snapshot_sha256"] = digest(snapshot)
    result = {
        "snapshot": snapshot,
        "receipt": receipt,
        "graph": graph,
        "carrier_hashes": hashes,
    }
    if options.model_source is not None:
        result["model_diagnostics"] = compiled[3]
    if options.foreground:
        result["deferred_archive"] = _deferred_archive(
            deferred, endpoints, archive_versions
        )
    return result


def _artifact_witness(binding, config, guarded, graph_option):
    return artifact_inputs(
        binding, config, watcher_guarded=guarded, **graph_option
    )


def _reuse_after_build(
    binding,
    config,
    inputs,
    result,
    compiled,
    watcher_guarded,
    graph_option,
):
    reusable = (
        inputs is not None
        and reusable_graph(result["graph"])
        and artifact_inputs(
            binding,
            config,
            watcher_guarded=watcher_guarded,
            **graph_option,
        )
        == inputs
    )
    return (
        {
            "inputs": inputs,
            "graph_config": config,
            "endpoints": compiled[2],
        }
        if reusable
        else None
    )


def _build_generation(binding, output, compile_capture, options):
    prepared = _prepare_generation(binding, output, options)
    output, identity, config, finish_snapshot, model_inputs, versions = (
        prepared
    )
    graph_option = {"defer_graph": True} if options.defer_graph else {}
    guarded = options.watcher_guarded
    inputs = None
    if options.managed:
        inputs = _artifact_witness(binding, config, guarded, graph_option)
    with tempfile.TemporaryDirectory(
        prefix=".beta-job-", dir=output.parent
    ) as temporary:
        stage = Path(temporary) / "generation"
        stage.mkdir()
        compiled, captured = compile_capture(
            binding,
            stage,
            model_inputs,
            options.model_source,
            finish_snapshot,
        )
        result = _generation_result(
            binding,
            config,
            compiled,
            captured,
            options,
            versions,
        )
        if options.managed:
            result["reuse"] = _reuse_after_build(
                binding,
                config,
                inputs,
                result,
                compiled,
                guarded,
                graph_option,
            )
        _publish_generation(
            output, identity, stage, result, options.batch_full
        )
    return result
