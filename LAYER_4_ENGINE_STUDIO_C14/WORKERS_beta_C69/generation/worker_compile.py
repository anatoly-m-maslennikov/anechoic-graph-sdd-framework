"""Compile Model inputs and verify their build receipt."""

from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from WORKERS_beta_C69.generation.graph_consistency import _graph_consistency


class _BuildFailure(ValueError):
    def __init__(self, module, message, graph_consistency=None):
        super().__init__(message)
        self.graph_consistency = graph_consistency
        self.issue_code = {
            "manifest_build_CS4__shared": "manifest_build_failed",
            "realization_graph": "realization_scan_failed",
        }.get(module, "build_failed")


def _run_job(module, payload, *arguments):
    engine = Path(__file__).resolve().parents[2]
    env = {
        key: value for key, value in os.environ.items() if key != "PYTHONHOME"
    }
    env["PYTHONPATH"] = str(engine)
    result = subprocess.run(
        [sys.executable, "-B", "-P", "-m", module, *arguments],
        input=json.dumps(payload, default=str),
        text=True,
        capture_output=True,
        cwd=engine,
        env=env,
    )
    if result.returncode:
        job = module.rsplit(".", 1)[-1]
        if (
            job == "realization_graph"
            and (details := _graph_consistency(result.stderr)) is not None
        ):
            raise _BuildFailure(
                job,
                "realization_graph failed: Project source or dependency "
                "inputs changed during capture",
                graph_consistency=details,
            )
        error = _BuildFailure(job, f"{job} failed: " + result.stderr[-2048:])
        try:
            diagnostics = json.loads(result.stdout).get("model_diagnostics")
            if isinstance(diagnostics, list) and diagnostics:
                error.model_diagnostics = diagnostics
        except ValueError, TypeError, AttributeError:
            pass
        raise error
    if result.stderr:
        sys.stderr.write(result.stderr[-8192:])
    return json.loads(result.stdout)


def _read_compile_receipt(binding, stage, receipt):
    fields = {
        "manifest_sha256",
        "model_sha256",
        "model_descriptor_sha256",
        "structure_sha256",
    }
    if (
        not isinstance(receipt, dict)
        or set(receipt) != fields
        or receipt["manifest_sha256"] != binding["manifest_sha256"]
    ):
        raise ValueError("Invalid Manifest build receipt")
    structure = (stage / "structure.json").read_bytes()
    if sha256(structure).hexdigest() != receipt["structure_sha256"]:
        raise ValueError("Structure does not match Manifest build receipt")
    model = (stage / "model.json").read_bytes()
    if sha256(model).hexdigest() != receipt["model_descriptor_sha256"]:
        raise ValueError("Model does not match Manifest build receipt")
    return (
        receipt,
        json.loads(structure),
        json.loads(model)["bindings"]["endpoints"],
    )


def _compile_ingested(
    binding, stage, inputs, source, *, fallback=None, diagnostics=None
):
    model_inputs, previous = _prepare_model_inputs(
        inputs, source, stage, fallback, diagnostics
    )
    module = "WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared"
    try:
        response = _run_job(
            module,
            {"binding": binding, "model_inputs": model_inputs},
            "--output-dir",
            str(stage),
            "--ingested-model",
        )
    except _BuildFailure as error:
        if previous:
            error.model_diagnostics = previous + getattr(
                error, "model_diagnostics", []
            )
        raise
    diagnostics = response.pop("model_diagnostics")
    if not isinstance(diagnostics, list):
        raise ValueError("Invalid Manifest build Model diagnostics")
    for issue in diagnostics:
        print(
            "Model candidate rejected: "
            + str(issue.get("message", "invalid Model")),
            file=sys.stderr,
        )
    receipt, structure, endpoints = _read_compile_receipt(
        binding, stage, response
    )
    return receipt, structure, endpoints, previous + diagnostics


def _prepare_model_inputs(inputs, source, stage, fallback, diagnostics):
    if (
        not isinstance(source, dict)
        or "accepted_model" not in source
        or set(source) - {"accepted_model", "force_rebuild", "spec_database"}
        or type(source.get("force_rebuild", False)) is not bool
    ):
        raise ValueError("Invalid accepted Model source")
    model_inputs = {
        "rows": inputs["rows"],
        "has_c9": inputs["has_c9"],
        "issues": list(inputs["issues"]),
        "accepted_model": source["accepted_model"],
    }
    if "spec_rows" in inputs:
        model_inputs.update(
            spec_rows=inputs["spec_rows"],
            manifest_path=inputs["manifest_path"],
            snapshot_id=inputs["snapshot_id"],
            structure_alias_issues=inputs.get("structure_alias_issues", ()),
        )
    if source.get("force_rebuild"):
        model_inputs["force_rebuild"] = True
    previous = [] if diagnostics is None else diagnostics
    if fallback is not None:
        for child in stage.iterdir():
            shutil.rmtree(child) if child.is_dir() else child.unlink()
        model_inputs["issues"].append(
            {"code": "model_snapshot_invalid", "message": str(fallback)}
        )
    return model_inputs, previous
