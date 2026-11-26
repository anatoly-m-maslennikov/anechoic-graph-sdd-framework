"""Build a transient, pinned Current Atom snapshot from an admitted binding."""
from __future__ import annotations
from functools import partial
from hashlib import sha256
import json
import os
import shutil
from pathlib import Path
import sys
import subprocess
import tempfile


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import NativeSnapshotChanged, mark_startup_timing

from .graph_consistency import _graph_consistency
from .managed_request import _managed_request
from .generation_batches import _write_generation_batches
from .python_code_units import python_code_units as python_code_units
from .python_context_restoration import python_context_restoration as python_context_restoration
from .python_import_order import python_import_order as python_import_order
from .native_refresh import _mark_reused, _reuse_hint, _ticket_delta, artifact_inputs, digest, refresh, reusable_graph, startup_incremental

sys.dont_write_bytecode = True


class _BuildFailure(ValueError):
    def __init__(self, module, message, graph_consistency=None):
        super().__init__(message)
        self.graph_consistency = graph_consistency
        self.issue_code = {
            "manifest_build_CS4__shared": "manifest_build_failed",
            "realization_graph": "realization_scan_failed",
        }.get(module, "build_failed")



def _run_job(module, payload, *arguments):
    engine = Path(__file__).resolve().parents[1]
    env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
    env["PYTHONPATH"] = str(engine)
    result = subprocess.run([sys.executable, "-B", "-P", "-m", module, *arguments], input=json.dumps(payload, default=str),
                            text=True, capture_output=True, cwd=engine, env=env)
    if result.returncode:
        job = module.rsplit(".", 1)[-1]
        if job == "realization_graph" and (details := _graph_consistency(result.stderr)) is not None:
            raise _BuildFailure(job, "realization_graph failed: Project source or dependency inputs changed during capture",
                                graph_consistency=details)
        error = _BuildFailure(job, f"{job} failed: " + result.stderr[-2048:])
        try:
            diagnostics = json.loads(result.stdout).get("model_diagnostics")
            if isinstance(diagnostics, list) and diagnostics:
                error.model_diagnostics = diagnostics
        except (ValueError, TypeError, AttributeError):
            pass
        raise error
    if result.stderr:
        sys.stderr.write(result.stderr[-8192:])
    return json.loads(result.stdout)


def _capture(binding, endpoints=None, *, watcher_guarded=False):
    if endpoints is not None:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import prepare_generation_snapshot

        config, finish = prepare_generation_snapshot(binding, include_hashes=True, watcher_guarded=watcher_guarded)
        snapshot, hashes = finish(endpoints)
        return {"snapshot": snapshot, "graph_config": config, "carrier_hashes": hashes}
    request = binding
    capture = _run_job("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli", request)
    if not isinstance(capture, dict) or set(capture) != {"snapshot", "stability_sha256", "graph_config"}:
        raise ValueError("Invalid native capture response")
    return capture


def build(binding):
    return _capture(binding)["snapshot"]


def _build_graph(binding, config, structure, *, replay_graph=False):
    if config is None:
        mark_startup_timing("realization_graph_ready", mode="disabled")
        return None
    module = "WORKERS_beta_C69.realization_graph"
    payload = {"root": binding["root"], "config": config, "control_root": binding["control_root"],
               "structure": structure}
    arguments = ("--watcher-replay",) if replay_graph else ()
    try:
        graph = _run_job(module, payload, *arguments)
        mark_startup_timing("realization_graph_ready", mode="built")
        return graph
    except _BuildFailure as error:
        if error.graph_consistency is None:
            raise
        evidence = json.dumps(error.graph_consistency, ensure_ascii=True, separators=(",", ":"))
        if len(evidence) < 4096:
            print("\nanechoic-realization-graph-restart " + evidence, file=sys.stderr)
    try:
        graph = _run_job(module, payload, *arguments)
        mark_startup_timing("realization_graph_ready", mode="built")
        return graph
    except _BuildFailure as error:
        if error.graph_consistency is None:
            raise
        raise _BuildFailure("realization_graph", f"{error} after one Realization Graph restart",
                            graph_consistency=error.graph_consistency) from None


def _rebuild_graph(binding, config, structure, endpoints, *, watcher_guarded=False, replay_graph=False):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        prepare_generation_snapshot,
    )

    current_config, finish_snapshot = prepare_generation_snapshot(
        binding, include_hashes=True, watcher_guarded=watcher_guarded)
    if current_config != config:
        return None
    graph = _build_graph(binding, config, structure, replay_graph=replay_graph)
    if graph is None:
        return None
    snapshot, hashes = finish_snapshot(endpoints)
    return snapshot, graph, hashes


def _compile(binding, stage):
    module = "WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared"
    receipt = _run_job(module, binding, "--output-dir", str(stage))
    return _read_compile_receipt(binding, stage, receipt)


def _read_compile_receipt(binding, stage, receipt):
    fields = {"manifest_sha256", "model_sha256", "model_descriptor_sha256", "structure_sha256"}
    if not isinstance(receipt, dict) or set(receipt) != fields or receipt["manifest_sha256"] != binding["manifest_sha256"]:
        raise ValueError("Invalid Manifest build receipt")
    structure = (stage / "structure.json").read_bytes()
    if sha256(structure).hexdigest() != receipt["structure_sha256"]:
        raise ValueError("Structure does not match Manifest build receipt")
    model = (stage / "model.json").read_bytes()
    if sha256(model).hexdigest() != receipt["model_descriptor_sha256"]:
        raise ValueError("Model does not match Manifest build receipt")
    return receipt, json.loads(structure), json.loads(model)["bindings"]["endpoints"]


class _ModelAttemptFailure(ValueError):
    def __init__(self, error, diagnostics):
        super().__init__(str(error))
        self.model_diagnostics = diagnostics


def _compile_ingested(binding, stage, inputs, source, *, fallback=None, diagnostics=None):
    if not isinstance(source, dict) or set(source) != {"accepted_model"}:
        raise ValueError("Invalid accepted Model source")
    model_inputs = {"rows": inputs["rows"], "has_c9": inputs["has_c9"],
                    "issues": list(inputs["issues"]), "accepted_model": source["accepted_model"]}
    previous = [] if diagnostics is None else diagnostics
    if fallback is not None:
        for child in stage.iterdir():
            shutil.rmtree(child) if child.is_dir() else child.unlink()
        model_inputs["issues"].append({"code": "model_snapshot_invalid", "message": str(fallback)})
    module = "WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared"
    try:
        response = _run_job(module, {"binding": binding, "model_inputs": model_inputs},
                            "--output-dir", str(stage), "--ingested-model")
    except _BuildFailure as error:
        if previous:
            error.model_diagnostics = previous + getattr(error, "model_diagnostics", [])
        raise
    diagnostics = response.pop("model_diagnostics")
    if not isinstance(diagnostics, list):
        raise ValueError("Invalid Manifest build Model diagnostics")
    for issue in diagnostics:
        print("Model candidate rejected: " + str(issue.get("message", "invalid Model")), file=sys.stderr)
    receipt, structure, endpoints = _read_compile_receipt(binding, stage, response)
    return receipt, structure, endpoints, previous + diagnostics


def _compile_and_capture(binding, stage, model_inputs, model_source, finish_snapshot):
    compiled = (_compile(binding, stage) if model_source is None else
                _compile_ingested(binding, stage, model_inputs, model_source))
    try:
        captured = finish_snapshot(compiled[2])
    except NativeSnapshotChanged:
        raise
    except ValueError as error:
        if model_source is None:
            raise
        if compiled[3]:
            raise _ModelAttemptFailure(error, compiled[3]) from error
        compiled = _compile_ingested(binding, stage, model_inputs, model_source, fallback=error,
                                     diagnostics=compiled[3])
        try:
            captured = finish_snapshot(compiled[2])
        except (OSError, RuntimeError, TypeError, ValueError) as failure:
            raise _ModelAttemptFailure(failure, compiled[3]) from failure
    return compiled, captured


def _generation_graph(binding, config, structure, compiled, model_source, replay_graph):
    try:
        return _build_graph(binding, config, structure, replay_graph=replay_graph)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        if model_source is not None and compiled[3]:
            error.model_diagnostics = compiled[3]
        raise


def _publish_generation(output, identity, stage, result, batch_full):
    if batch_full:
        result["batch_artifact"] = _write_generation_batches(
            stage, result.pop("snapshot"), result.pop("graph"), result.pop("carrier_hashes"))
    if (output.is_symlink() or not output.is_dir() or output.stat() != identity or any(output.iterdir())):
        raise ValueError("Generation directory changed during build")
    os.replace(stage, output)


def _deferred_archive(deferred, endpoints, archive_versions):
    roots, archived, archive_hashes = deferred
    return {"roots": roots, "snapshot": archived, "carrier_hashes": archive_hashes,
            "endpoints": endpoints, "archive_versions": archive_versions}


def build_generation(binding, output, *, managed=False, watcher_guarded=False, foreground=False,
                     replay_graph=False, model_source=None, batch_full=False, defer_graph=False):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        prepare_generation_snapshot,
    )

    output = Path(output)
    if (not output.is_absolute() or output.is_symlink() or not output.is_dir()
            or output.resolve(strict=True) != output or any(output.iterdir())):
        raise ValueError("Generation directory must be an existing empty canonical directory")
    archive_versions = {}
    captured = prepare_generation_snapshot(
        binding, include_hashes=True, watcher_guarded=watcher_guarded,
        archive_stage="foreground" if foreground else None,
        **({"archive_versions": archive_versions} if foreground else {}),
        **({"include_model_inputs": True} if model_source is not None else {}))
    config, finish_snapshot = captured[:2]
    model_inputs = captured[2] if model_source is not None else None
    control = Path(binding["root"]) / binding["control_root"]
    if output == control or control in output.parents:
        raise ValueError("Generation directory must be outside the Project control root")
    identity = output.stat()
    graph_option = {"defer_graph": True} if defer_graph else {}
    inputs = artifact_inputs(binding, config, watcher_guarded=watcher_guarded, **graph_option) if managed else None
    with tempfile.TemporaryDirectory(prefix=".beta-job-", dir=output.parent) as temporary:
        stage = Path(temporary) / "generation"
        stage.mkdir()
        compiled, captured = _compile_and_capture(binding, stage, model_inputs, model_source, finish_snapshot)
        receipt, structure, endpoints = compiled[:3]
        snapshot, hashes, *deferred = captured
        graph = (None if defer_graph and config is not None else
                 _generation_graph(binding, config, structure, compiled, model_source, replay_graph))
        receipt["graph_sha256"] = digest(graph)
        receipt["snapshot_sha256"] = digest(snapshot)
        result = {"snapshot": snapshot, "receipt": receipt, "graph": graph, "carrier_hashes": hashes}
        if model_source is not None:
            result["model_diagnostics"] = compiled[3]
        if foreground:
            result["deferred_archive"] = _deferred_archive(deferred, endpoints, archive_versions)
        if managed:
            reusable = (inputs is not None and reusable_graph(graph)
                        and artifact_inputs(binding, config, watcher_guarded=watcher_guarded, **graph_option) == inputs)
            result["reuse"] = {"inputs": inputs, "graph_config": config, "endpoints": endpoints} if reusable else None
        _publish_generation(output, identity, stage, result, batch_full)
    return result



def _graph_only(binding, reuse, structure, guarded):
    if reuse is None or reuse.graph_config is None or not isinstance(structure, dict):
        raise ValueError("Graph-only capture requires reuse, graph config, and structure")
    config = reuse.graph_config
    before = artifact_inputs(binding, config, watcher_guarded=guarded)
    if (before is None or before.get("manifest") != reuse.inputs.get("manifest")
            or before.get("carrier_schema") != reuse.inputs.get("carrier_schema")):
        raise ValueError("Core artifact inputs changed before graph capture")
    if before == reuse.inputs:
        mark_startup_timing("realization_graph_ready", mode="reused")
        return {"base_generation": reuse.base_generation, "unchanged": True}
    graph = _build_graph(binding, config, structure)
    if not reusable_graph(graph) or artifact_inputs(binding, config, watcher_guarded=guarded) != before:
        raise ValueError("Graph inputs changed during capture")
    return {"base_generation": reuse.base_generation, "graph": graph, "graph_sha256": digest(graph),
            "reuse": {"inputs": before, "graph_config": config, "endpoints": reuse.endpoints}}


def _deferred_incremental(binding, reuse, foreground, guarded):
    if reuse is None:
        return None
    before = artifact_inputs(binding, reuse.graph_config, watcher_guarded=guarded, defer_graph=True)
    if (before is None or before.get("manifest") != reuse.inputs.get("manifest")
            or before.get("carrier_schema") != reuse.inputs.get("carrier_schema")):
        return None
    result = startup_incremental(binding, reuse, before=before, foreground=foreground,
                                 watcher_guarded=guarded, defer_graph=True)
    if result is not None:
        _mark_reused(foreground, reuse.graph_config, graph=False)
    return result


def _run(request, output):
    if output is None:
        return build(request)
    if not isinstance(request, dict) or "binding" not in request or "reuse" not in request:
        return build_generation(request, output)
    admitted = _managed_request(request)
    binding, reuse = admitted.binding, _reuse_hint(admitted.reuse)
    guarded, foreground, incremental = admitted.watcher_guarded, admitted.foreground, admitted.incremental
    if admitted.graph_only:
        return _graph_only(binding, reuse, admitted.structure, guarded)
    if "archive" in admitted.model_fields_set:
        if incremental:
            return startup_incremental(binding, reuse, archive_roots=admitted.archive["roots"], watcher_guarded=guarded)
        return _capture_archive(binding, admitted.archive, guarded)
    if admitted.defer_graph and incremental and admitted.paths is None:
        native = _deferred_incremental(binding, reuse, foreground, guarded)
        if native is not None:
            return native
    if foreground and admitted.paths is not None:
        native = _ticket_delta(binding, reuse, admitted.paths)
        if native is not None:
            return native
    elif not admitted.defer_graph and (not foreground or incremental):
        native = refresh(binding, reuse, partial(_capture, watcher_guarded=guarded), admitted.paths, admitted.structure,
                         partial(_rebuild_graph, watcher_guarded=guarded and not incremental,
                                 replay_graph=admitted.replay_graph),
                         watcher_guarded=guarded, incremental=incremental, foreground=foreground)
        if native is not None:
            return native
    return build_generation(binding, output, managed=True, watcher_guarded=guarded, foreground=foreground,
                            replay_graph=admitted.replay_graph, model_source=admitted.model_source, batch_full=admitted.batch_full,
                            defer_graph=admitted.defer_graph)


def _capture_archive(binding, archive, watcher_guarded):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import prepare_generation_snapshot

    _, finish = prepare_generation_snapshot(
        binding, include_hashes=True, archive_stage="archive", archive_roots=archive["roots"],
        watcher_guarded=watcher_guarded)
    snapshot, hashes = finish(archive["endpoints"])
    return {"snapshot": snapshot, "carrier_hashes": hashes}


def main():
    from .worker_entry import main as run
    return run(_run)


if __name__ == "__main__":
    raise SystemExit(main())
