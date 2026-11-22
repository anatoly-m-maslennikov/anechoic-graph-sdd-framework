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

sys.dont_write_bytecode = True


def _run_job(module, payload, *arguments):
    engine = Path(__file__).resolve().parents[1]
    env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
    env["PYTHONPATH"] = str(engine)
    result = subprocess.run([sys.executable, "-B", "-P", "-m", module, *arguments], input=json.dumps(payload),
                            text=True, capture_output=True, cwd=engine, env=env, timeout=120)
    if result.returncode:
        raise ValueError(f"{module.rsplit('.', 1)[-1]} failed: " + result.stderr[-2048:])
    if result.stderr:
        sys.stderr.write(result.stderr[-8192:])
    return json.loads(result.stdout)


def _capture(binding, endpoints=None):
    request = binding if endpoints is None else {"binding": binding, "endpoints": endpoints}
    capture = _run_job("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli", request)
    if not isinstance(capture, dict) or set(capture) != {"snapshot", "stability_sha256", "graph_config"}:
        raise ValueError("Invalid native capture response")
    return capture


def build(binding):
    return _capture(binding)["snapshot"]


def _build_graph(binding, config, structure):
    if config is None:
        return None
    return _run_job("IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.realization_graph_cli",
                    {"root": binding["root"], "config": config, "control_root": binding["control_root"],
                     "structure": structure})


def build_generation(binding, output):
    output = Path(output)
    if (not output.is_absolute() or output.is_symlink() or not output.is_dir()
            or output.resolve(strict=True) != output or any(output.iterdir())):
        raise ValueError("Generation directory must be an existing empty canonical directory")
    before = _capture(binding)
    control = Path(binding["root"]) / binding["control_root"]
    if output == control or control in output.parents:
        raise ValueError("Generation directory must be outside the Project control root")
    identity = output.stat()
    module = "WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared"
    with tempfile.TemporaryDirectory(prefix=".beta-job-", dir=output.parent) as temporary:
        stage = Path(temporary) / "generation"
        stage.mkdir()
        receipt = _run_job(module, binding, "--output-dir", str(stage))
        fields = {"manifest_sha256", "model_sha256", "model_descriptor_sha256", "structure_sha256"}
        if not isinstance(receipt, dict) or set(receipt) != fields or receipt["manifest_sha256"] != binding["manifest_sha256"]:
            raise ValueError("Invalid Manifest build receipt")
        structure_raw = (stage / "structure.json").read_bytes()
        if sha256(structure_raw).hexdigest() != receipt["structure_sha256"]:
            raise ValueError("Structure does not match Manifest build receipt")
        structure = json.loads(structure_raw)
        model_raw = (stage / "model.json").read_bytes()
        if sha256(model_raw).hexdigest() != receipt["model_descriptor_sha256"]:
            raise ValueError("Model does not match Manifest build receipt")
        model = json.loads(model_raw)
        expanded = _capture(binding, model["bindings"]["endpoints"])
        if before["stability_sha256"] != expanded["stability_sha256"]:
            raise ValueError("Native Project carriers changed during generation")
        snapshot = expanded["snapshot"]
        snapshot_raw = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        receipt["snapshot_sha256"] = sha256(snapshot_raw).hexdigest()
        graph = _build_graph(binding, before["graph_config"], structure)
        raw = json.dumps(graph, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        receipt["graph_sha256"] = sha256(raw).hexdigest()
        after = _capture(binding)
        if before["stability_sha256"] != after["stability_sha256"]:
            raise ValueError("Native Project carriers changed during generation")
        if (output.is_symlink() or not output.is_dir() or output.stat() != identity or any(output.iterdir())):
            raise ValueError("Generation directory changed during build")
        os.replace(stage, output)
    return {"snapshot": snapshot, "receipt": receipt, "graph": graph}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation-dir")
    args = parser.parse_args()
    try:
        binding = json.load(sys.stdin)
        result = build_generation(binding, args.generation_dir) if args.generation_dir else build(binding)
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
