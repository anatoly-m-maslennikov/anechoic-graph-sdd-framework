"""Build a transient, pinned Current Atom snapshot from an admitted binding."""
from __future__ import annotations

import argparse
from functools import partial
from hashlib import sha256
import json
import os
import shutil
from pathlib import Path
import sys
import subprocess
import tempfile
import traceback

from .managed_parent import watch_managed_parent
from .python_code_units import python_code_units as python_code_units
from .python_context_restoration import python_context_restoration as python_context_restoration
from .python_import_order import python_import_order as python_import_order
from .native_refresh import _ticket_delta, artifact_inputs, digest, refresh, startup_incremental

sys.dont_write_bytecode = True


class _BuildFailure(ValueError):
    def __init__(self, module, message, graph_consistency=None):
        super().__init__(message)
        self.graph_consistency = graph_consistency
        self.issue_code = {
            "manifest_build_CS4__shared": "manifest_build_failed",
            "realization_graph": "realization_scan_failed",
        }.get(module, "build_failed")


def _graph_consistency(stderr):
    try:
        record = json.loads(stderr[-4096:].rstrip().rsplit("\n", 1)[-1])
        if (record["code"] == "realization_graph_inputs_changed" and record["component"] == "C61"
                and record["severity"] == "ERROR" and isinstance(record["details"], dict)):
            return record["details"]
    except (ValueError, TypeError, KeyError):
        pass
    return None


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
                for issue in diagnostics:
                    if isinstance(issue, dict):
                        print("Model candidate rejected: " + str(issue.get("message", "invalid Model")), file=sys.stderr)
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


def _build_graph(binding, config, structure):
    if config is None:
        return None
    module = "WORKERS_beta_C69.realization_graph"
    payload = {"root": binding["root"], "config": config, "control_root": binding["control_root"],
               "structure": structure}
    try:
        return _run_job(module, payload)
    except _BuildFailure as error:
        if error.graph_consistency is None:
            raise
        evidence = json.dumps(error.graph_consistency, ensure_ascii=True, separators=(",", ":"))
        if len(evidence) < 4096:
            print("\nanechoic-realization-graph-restart " + evidence, file=sys.stderr)
    try:
        return _run_job(module, payload)
    except _BuildFailure as error:
        if error.graph_consistency is None:
            raise
        raise _BuildFailure("realization_graph", f"{error} after one Realization Graph restart",
                            graph_consistency=error.graph_consistency) from None


def _rebuild_graph(binding, config, structure, endpoints, *, watcher_guarded=False):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        prepare_generation_snapshot,
    )

    current_config, finish_snapshot = prepare_generation_snapshot(
        binding, include_hashes=True, watcher_guarded=watcher_guarded)
    if current_config != config:
        return None
    graph = _build_graph(binding, config, structure)
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


def build_generation(binding, output, *, managed=False, watcher_guarded=False, foreground=False, model_source=None):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import prepare_generation_snapshot

    output = Path(output)
    if (not output.is_absolute() or output.is_symlink() or not output.is_dir()
            or output.resolve(strict=True) != output or any(output.iterdir())):
        raise ValueError("Generation directory must be an existing empty canonical directory")
    captured = prepare_generation_snapshot(
        binding, include_hashes=True, watcher_guarded=watcher_guarded,
        archive_stage="foreground" if foreground else None,
        **({"include_model_inputs": True} if model_source is not None else {}))
    config, finish_snapshot = captured[:2]
    model_inputs = captured[2] if model_source is not None else None
    control = Path(binding["root"]) / binding["control_root"]
    if output == control or control in output.parents:
        raise ValueError("Generation directory must be outside the Project control root")
    identity = output.stat()
    inputs = artifact_inputs(binding, config, watcher_guarded=watcher_guarded) if managed else None
    with tempfile.TemporaryDirectory(prefix=".beta-job-", dir=output.parent) as temporary:
        stage = Path(temporary) / "generation"
        stage.mkdir()
        compiled, captured = _compile_and_capture(binding, stage, model_inputs, model_source, finish_snapshot)
        receipt, structure, endpoints = compiled[:3]
        snapshot, hashes, *deferred = captured
        try:
            graph = _build_graph(binding, config, structure)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            if model_source is not None and compiled[3]:
                error.model_diagnostics = compiled[3]
            raise
        receipt["graph_sha256"] = digest(graph)
        receipt["snapshot_sha256"] = digest(snapshot)
        result = {"snapshot": snapshot, "receipt": receipt, "graph": graph, "carrier_hashes": hashes}
        if model_source is not None:
            result["model_diagnostics"] = compiled[3]
        if foreground:
            roots, archived, archive_hashes = deferred
            result["deferred_archive"] = {"roots": roots, "snapshot": archived,
                                          "carrier_hashes": archive_hashes, "endpoints": endpoints}
        if managed:
            reusable = inputs is not None and artifact_inputs(binding, config, watcher_guarded=watcher_guarded) == inputs
            result["reuse"] = {"inputs": inputs, "graph_config": config, "endpoints": endpoints} if reusable else None
        if (output.is_symlink() or not output.is_dir() or output.stat() != identity or any(output.iterdir())):
            raise ValueError("Generation directory changed during build")
        os.replace(stage, output)
    return result


def _run(request, output):
    if output is None:
        return build(request)
    if not isinstance(request, dict) or "binding" not in request or "reuse" not in request:
        return build_generation(request, output)
    fields = set(request) - {"watcher_guarded", "foreground", "incremental", "model_source"}
    incremental = request.get("incremental", False)
    if any(type(request.get(key, False)) is not bool for key in ("incremental", "foreground", "watcher_guarded")):
        raise ValueError("Invalid managed Worker option")
    if fields == {"binding", "reuse", "archive"}:
        if incremental:
            return startup_incremental(request["binding"], request["reuse"], archive_roots=request["archive"]["roots"],
                                       watcher_guarded=request.get("watcher_guarded", False))
        return _capture_archive(request["binding"], request["archive"], request.get("watcher_guarded", False))
    if fields not in ({"binding", "reuse"}, {"binding", "reuse", "paths"}, {"binding", "reuse", "structure"}):
        raise ValueError("Invalid managed Worker fields")
    binding = request["binding"]
    guarded = request.get("watcher_guarded", False)
    foreground = request.get("foreground", False)
    if foreground and request.get("paths") is not None:
        native = _ticket_delta(binding, request["reuse"], request["paths"])
        if native is not None:
            return native
    elif not foreground or incremental:
        native = refresh(binding, request["reuse"], partial(_capture, watcher_guarded=guarded),
                         request.get("paths"), request.get("structure"),
                         partial(_rebuild_graph, watcher_guarded=guarded and not incremental),
                         watcher_guarded=guarded, incremental=incremental, foreground=foreground)
        if native is not None:
            return native
    return build_generation(binding, output, managed=True, watcher_guarded=guarded, foreground=foreground,
                            model_source=request.get("model_source"))


def _capture_archive(binding, archive, watcher_guarded):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import prepare_generation_snapshot

    _, finish = prepare_generation_snapshot(
        binding, include_hashes=True, archive_stage="archive", archive_roots=archive["roots"],
        watcher_guarded=watcher_guarded)
    snapshot, hashes = finish(archive["endpoints"])
    return {"snapshot": snapshot, "carrier_hashes": hashes}


def _ingestion_failure(error):
    issues = getattr(error, "ingestion_issues", None)
    if issues is not None:
        return {"source": "atom", "issues": issues}
    return {"source": "build", "issues": [{
        "relative_path": None, "code": getattr(error, "issue_code", "build_failed"),
        "message": str(error)[-8192:] or type(error).__name__, "atom_ref": None, "related_paths": [],
    }]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation-dir")
    args = parser.parse_args()
    request = None
    try:
        watch_managed_parent()
        request = json.load(sys.stdin)
        result = _run(request, args.generation_dir)
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError, subprocess.TimeoutExpired) as error:
        if args.generation_dir is None:
            print(str(error), file=sys.stderr)
        else:
            traceback.print_exc()
            if isinstance(request, dict) and {"binding", "reuse"} <= request.keys():
                failure = {"ingestion_failure": _ingestion_failure(error)}
                if getattr(error, "model_diagnostics", None):
                    failure["model_diagnostics"] = error.model_diagnostics
                if isinstance(error, _BuildFailure) and error.graph_consistency is not None:
                    failure["graph_consistency"] = error.graph_consistency
                print(json.dumps(failure, ensure_ascii=False))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
