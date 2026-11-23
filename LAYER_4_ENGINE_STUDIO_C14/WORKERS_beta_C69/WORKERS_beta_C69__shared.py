"""Build a transient, pinned Current Atom snapshot from an admitted binding."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import traceback

from .managed_parent import watch_managed_parent
from .python_code_units import python_code_units as python_code_units
from .python_context_restoration import python_context_restoration as python_context_restoration
from .python_import_order import python_import_order as python_import_order
from .native_refresh import artifact_inputs, digest, refresh

sys.dont_write_bytecode = True


class _BuildFailure(ValueError):
    def __init__(self, module, message):
        super().__init__(message)
        self.issue_code = {
            "manifest_build_CS4__shared": "manifest_build_failed",
            "realization_graph": "realization_scan_failed",
        }.get(module, "build_failed")


def _run_job(module, payload, *arguments):
    engine = Path(__file__).resolve().parents[1]
    env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
    env["PYTHONPATH"] = str(engine)
    result = subprocess.run([sys.executable, "-B", "-P", "-m", module, *arguments], input=json.dumps(payload),
                            text=True, capture_output=True, cwd=engine, env=env)
    if result.returncode:
        job = module.rsplit(".", 1)[-1]
        raise _BuildFailure(job, f"{job} failed: " + result.stderr[-2048:])
    if result.stderr:
        sys.stderr.write(result.stderr[-8192:])
    return json.loads(result.stdout)


def _capture(binding, endpoints=None):
    if endpoints is not None:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import prepare_generation_snapshot

        config, finish = prepare_generation_snapshot(binding, include_hashes=True)
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
    return _run_job("WORKERS_beta_C69.realization_graph",
                    {"root": binding["root"], "config": config, "control_root": binding["control_root"],
                     "structure": structure})


def _rebuild_graph(binding, config, structure, endpoints):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        prepare_generation_snapshot,
    )

    current_config, finish_snapshot = prepare_generation_snapshot(binding, include_hashes=True)
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


def build_generation(binding, output, *, managed=False):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        prepare_generation_snapshot,
    )

    output = Path(output)
    if (not output.is_absolute() or output.is_symlink() or not output.is_dir()
            or output.resolve(strict=True) != output or any(output.iterdir())):
        raise ValueError("Generation directory must be an existing empty canonical directory")
    config, finish_snapshot = prepare_generation_snapshot(binding, include_hashes=True)
    control = Path(binding["root"]) / binding["control_root"]
    if output == control or control in output.parents:
        raise ValueError("Generation directory must be outside the Project control root")
    identity = output.stat()
    inputs = artifact_inputs(binding, config) if managed else None
    with tempfile.TemporaryDirectory(prefix=".beta-job-", dir=output.parent) as temporary:
        stage = Path(temporary) / "generation"
        stage.mkdir()
        receipt, structure, endpoints = _compile(binding, stage)
        graph = _build_graph(binding, config, structure)
        receipt["graph_sha256"] = digest(graph)
        snapshot, hashes = finish_snapshot(endpoints)
        receipt["snapshot_sha256"] = digest(snapshot)
        result = {"snapshot": snapshot, "receipt": receipt, "graph": graph, "carrier_hashes": hashes}
        if managed:
            reusable = inputs is not None and artifact_inputs(binding, config) == inputs
            result["reuse"] = {"inputs": inputs, "graph_config": config, "endpoints": endpoints} if reusable else None
        if (output.is_symlink() or not output.is_dir() or output.stat() != identity or any(output.iterdir())):
            raise ValueError("Generation directory changed during build")
        os.replace(stage, output)
    return result


def _run(request, output):
    if output is None:
        return build(request)
    if not isinstance(request, dict) or set(request) not in ({"binding", "reuse"}, {"binding", "reuse", "paths"}, {"binding", "reuse", "structure"}):
        return build_generation(request, output)
    binding = request["binding"]
    native = refresh(binding, request["reuse"], _capture, request.get("paths"), request.get("structure"), _rebuild_graph)
    return native if native is not None else build_generation(binding, output, managed=True)


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
                print(json.dumps({"ingestion_failure": _ingestion_failure(error)}, ensure_ascii=False))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
