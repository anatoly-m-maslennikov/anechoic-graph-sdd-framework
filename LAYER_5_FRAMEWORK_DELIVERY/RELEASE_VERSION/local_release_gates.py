"""Test-gate commands for the direct local Release."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys

from .release_assets import LocalReleaseError

_ROOT = Path(__file__).resolve().parents[2]
_ENGINE_PROJECT = _ROOT / "LAYER_4_ENGINE_STUDIO_C14"
_ENGINE_ENVIRONMENT = _ROOT / "LAYER_3_ENVIRONMENTS_C72/engine"


def _gate_command(root, phase, candidate_image, package, package_identity, selection, run_id, verify):
    suite_phase = "image" if phase == "verify candidate image" else phase.split()[0]
    argv = (
        "uv", "run", "--project", str(_ENGINE_ENVIRONMENT), "--locked", "--python", "3.14",
        "--managed-python", "--no-env-file", "--all-groups", "python", "-P", "-B", "-u",
        str(_ENGINE_PROJECT / "FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py"),
        "--project-root", str(root), "--phase", suite_phase,
    )
    if suite_phase == "unit":
        argv += ("--required",)
    if suite_phase == "image":
        if candidate_image is None:
            raise LocalReleaseError("local-release-candidate-image-invalid")
        argv += ("--candidate-image", candidate_image)
    if suite_phase == "image":
        verify(package, package_identity)
        project_mcp = selection.parameters.get("project_mcp", {})
        handoff = {
            "control_root": selection.control_relative.as_posix(),
            "manifest_path": selection.manifest_path.relative_to(root).as_posix(),
            "manifest_ref": selection.manifest_ref,
            "manifest_sha256": selection.manifest_sha256,
            "project_name": selection.project_name,
            "project_prefix": selection.project_prefix,
            "query_enabled": "query_run" not in project_mcp.get("tool_blacklist", ()),
        }
        argv += ("--canary-package", str(package), "--run-id", run_id,
                 "--canary-selection", json.dumps(handoff, sort_keys=True))
    return suite_phase, argv


def _run_gate_command(root, run_id, suite_phase, argv, runner, log_paths, *, target, named_file, logged_process):
    if runner is not None:
        try:
            return runner(argv, root)
        except OSError as error:
            raise LocalReleaseError("local-release-command-unavailable") from error
    temporary = target(root, Path(".anechoic_tmp/simple_local_release"), label="test-log")
    temporary.mkdir(parents=True, exist_ok=True)
    with named_file(mode="w+b", prefix=f"{run_id}-{suite_phase}-tests-", suffix=".log",
                    dir=temporary, delete=False) as log:
        log_paths[suite_phase] = Path(log.name).relative_to(root).as_posix()
        print(f"Local release tests; output log: {log_paths[suite_phase]}", file=sys.stderr, flush=True)
        env = {key: value for key, value in os.environ.items()
               if key not in {"PYTHONHOME", "VIRTUAL_ENV", "PYTHONPATH"}}
        env.update(PYTHONPATH=str(_ENGINE_PROJECT),
                   UV_PROJECT_ENVIRONMENT=str(_ENGINE_PROJECT / ".venv-dev"))
        return logged_process(argv, root, log, env=env)


def run_gate(root, phase, candidate_image, package, package_identity, selection, run_id, runner, log_paths,
             *, verify, target, named_file, logged_process, failed_output):
    suite_phase, argv = _gate_command(root, phase, candidate_image, package, package_identity, selection, run_id, verify)
    result = _run_gate_command(root, run_id, suite_phase, argv, runner, log_paths, target=target,
                               named_file=named_file, logged_process=logged_process)
    if getattr(result, "returncode", 1) != 0:
        detail = failed_output(root, run_id, result, log_path=log_paths.get(suite_phase))
        raise LocalReleaseError(f"local-release-command-failed: {detail}")
    if suite_phase == "image":
        observed = re.findall(
            r"(?m)^ANECHOIC_CANARY_ENDPOINT (http://127\.0\.0\.1:([1-9][0-9]{0,4})/anechoic/mcp)$",
            result.stdout,
        )
        if len(observed) != 1 or int(observed[0][1]) > 65535:
            raise LocalReleaseError("local-release-canary-endpoint-invalid")
        return observed[0][0]
    return None
