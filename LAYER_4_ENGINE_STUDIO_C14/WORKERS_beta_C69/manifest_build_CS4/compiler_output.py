"""Run the Model compiler and validate its result."""

import json
import os
import subprocess
import sys


def compile_pinned_generation(
    binding, stage, model_inputs, *, engine, compiler, compiler_digest
):
    env = {
        key: value for key, value in os.environ.items() if key != "PYTHONHOME"
    }
    env["PYTHONPATH"] = str(engine)
    model_args = (
        ["--ingested-model"] if model_inputs is not None else ["--build-model"]
    )
    if model_inputs is not None:
        model_inputs = {**model_inputs, "compiler_sha256": compiler_digest()}
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-P",
            "-m",
            compiler,
            binding["root"],
            binding["control_root"],
            binding["manifest_sha256"],
            str(stage),
            *model_args,
            "--attest-model",
        ],
        cwd=engine,
        env=env,
        input=(
            json.dumps(model_inputs, default=str).encode()
            if model_inputs is not None
            else None
        ),
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise _compiler_error(result.stderr, model_inputs is not None)
    if os.getenv("ANECHOIC_STARTUP_TIMING") == "1" and result.stderr:
        sys.stderr.write(result.stderr[-8192:].decode(errors="replace"))
    return _checked_artifact(json.loads(result.stdout), binding, model_inputs)


def _compiler_error(stderr, ingested):
    stderr = stderr.decode(errors="replace")
    error = ValueError("Manifest compiler failed: " + stderr[-2048:])
    if ingested:
        try:
            record = stderr.rstrip().rsplit("\n", 1)[-1]
            error.model_diagnostics = json.loads(record)["model_diagnostics"]
        except ValueError, KeyError, TypeError:
            pass
    return error


def _checked_artifact(artifact, binding, model_inputs):
    if (
        model_inputs is not None
        and model_inputs.get("snapshot_id") is not None
        and artifact.get("snapshot_id") != model_inputs["snapshot_id"]
    ):
        raise ValueError(
            "Manifest compiler returned a different Spec snapshot identity"
        )
    compiled = artifact["structure"]
    project = compiled["project"]
    if project["sha256"] != binding["manifest_sha256"] or not project[
        "ref"
    ].startswith(binding["project_prefix"] + "-S-"):
        raise ValueError("Compiled Structure has a different Project binding")
    if model_inputs is not None:
        return (
            compiled,
            artifact["model_descriptor_sha256"],
            artifact["model_diagnostics"],
        )
    return compiled, artifact["model_descriptor_sha256"]
