"""Test-gate commands for the direct local Release."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
)

_ROOT = Path(__file__).resolve().parents[3]
_LOGS = Path(".anechoic_tmp/simple_local_release")
_SUITE = "FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/test_suite__pub.py"
_PREFLIGHT_SETUP = (
    "Prepare the pinned Engine test environment with release.py local --prepare-environment "
    "--project-root <source-checkout> --run-id <id>."
)


def _gate_command(root, suite_phase, engine, source_bound):
    if source_bound or suite_phase == "preflight":
        argv = (str(engine / ".venv-dev/bin/python"), "-P", "-B", "-u")
    else:
        environment = _ROOT / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine"
        argv = ("uv", "run", "--project", str(environment), "--locked", "--python", "3.14",
                "--managed-python", "--no-env-file", "--all-groups", "python", "-P", "-B", "-u")
    script = (*argv, str(engine / _SUITE))
    if suite_phase is None:
        return (*script, "--help")
    return (*script, "--project-root", str(root), "--phase", suite_phase)


def _test_environment(engine):
    env = {key: value for key, value in os.environ.items()
           if key not in {"PYTHONHOME", "VIRTUAL_ENV", "PYTHONPATH"}}
    env.update(PYTHONPATH=str(engine), UV_PROJECT_ENVIRONMENT=str(engine / ".venv-dev"))
    return env


def _source_image_phase(root, suite_phase, engine):
    argv = _gate_command(root, None, engine, True)
    try:
        result = subprocess.run(argv, cwd=root, env=_test_environment(engine),
                                text=True, capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LocalReleaseError(f"local-release-source-test-suite-help-failed: {_PREFLIGHT_SETUP}") from error
    if result.returncode != 0:
        raise LocalReleaseError(f"local-release-source-test-suite-help-failed: {_PREFLIGHT_SETUP}")
    phase_option = re.search(r"(?m)^[ \t]*--phase[ \t]+\{([^}]+)\}", result.stdout)
    choices = {choice.strip() for choice in phase_option[1].split(",")} if phase_option else set()
    split = {"image-tests", "canary"}
    if split <= choices:
        return suite_phase
    if "image" in choices and split.isdisjoint(choices):
        return "image"
    raise LocalReleaseError("local-release-source-test-suite-phase-unsupported")


def _canary_arguments(root, package, selection, run_id, canary_root, settings_sha256):
    project = canary_root or root
    project_mcp = selection.parameters.get("project_mcp", {})
    blacklist = project_mcp.get("tool_blacklist", ()) if isinstance(project_mcp, dict) else None
    if not isinstance(blacklist, (tuple, list)) or any(not isinstance(name, str) for name in blacklist):
        raise LocalReleaseError("local-release-canary-selection-invalid")
    handoff = {
        "control_root": selection.control_relative.as_posix(),
        "manifest_path": selection.manifest_path.relative_to(project).as_posix(),
        "manifest_ref": selection.manifest_ref,
        "manifest_sha256": selection.manifest_sha256,
        "project_name": selection.project_name,
        "project_prefix": selection.project_prefix,
        "query_enabled": "query_run" not in blacklist,
    }
    if project != root:
        if settings_sha256 is not None and (
                not isinstance(settings_sha256, str) or re.fullmatch(r"[0-9a-f]{64}", settings_sha256) is None):
            raise LocalReleaseError("local-release-canary-selection-invalid")
        handoff["runtime_settings_sha256"] = settings_sha256
    arguments = ("--canary-package", str(package), "--run-id", run_id,
                 "--canary-selection", json.dumps(handoff, sort_keys=True))
    if project != root:
        arguments += ("--canary-project-root", str(project))
    return arguments


def _open_log(root, log_directory, run_id, suite_phase, target, named_file):
    relative = log_directory or _LOGS
    if not relative.is_relative_to(_LOGS) or ".." in relative.parts:
        raise LocalReleaseError("local-release-test-log-directory-invalid")
    directory = target(root, relative, label="test-log")
    directory.mkdir(parents=True, exist_ok=True)
    return named_file(mode="w+b", prefix=f"{run_id}-{suite_phase}-tests-", suffix=".log",
                      dir=directory, delete=False)


def _injected_gate(runner, argv, cwd):
    try:
        return runner(argv, cwd)
    except OSError as error:
        raise LocalReleaseError("local-release-command-unavailable") from error


def _run_gate_command(root, cwd, run_id, suite_phase, argv, runner, log_paths, *, engine,
                      target, named_file, logged_process, log_directory, record_logs):
    if runner is not None and log_directory is None:
        return _injected_gate(runner, argv, cwd)
    with _open_log(root, log_directory, run_id, suite_phase, target, named_file) as log:
        log_paths[suite_phase] = Path(log.name).relative_to(root).as_posix()
        if record_logs is not None:
            record_logs(log_paths)
        print(f"Local release tests; output log: {log_paths[suite_phase]}", file=sys.stderr, flush=True)
        if runner is not None:
            result = _injected_gate(runner, argv, cwd)
            for output in (result.stdout, result.stderr):
                if output:
                    log.write(output if isinstance(output, bytes) else output.encode("utf-8"))
            return result
        try:
            return logged_process(argv, cwd, log, env=_test_environment(engine))
        except OSError as error:
            guidance = f" {argv[0]}. {_PREFLIGHT_SETUP}" if suite_phase == "preflight" or argv[0] != "uv" else ""
            raise LocalReleaseError(f"local-release-command-unavailable:{guidance}") from error


def run_gate(root, suite_phase, candidate_image, package, package_identity, selection, run_id, runner, log_paths,
             *, verify, target, named_file, logged_process, failed_output, source_root=None,
             source_bound=False, canary_root=None, log_directory=None, canary_settings_sha256=None,
             record_logs=None):
    cwd = source_root or root
    source_bound = source_bound or source_root is not None
    engine = (cwd if source_bound else _ROOT) / "LAYER_4_ENGINE_STUDIO_C14"
    log_phase = "image" if suite_phase == "image-tests" else suite_phase
    if source_root is not None and runner is None and suite_phase in {"image-tests", "canary"}:
        suite_phase = _source_image_phase(cwd, suite_phase, engine)
    argv = _gate_command(cwd, suite_phase, engine, source_bound)
    if suite_phase in {"image", "image-tests", "canary"}:
        if candidate_image is None:
            raise LocalReleaseError("local-release-candidate-image-invalid")
        argv += ("--candidate-image", candidate_image)
        verify(package, package_identity)
    if suite_phase in {"image", "canary"}:
        argv += _canary_arguments(cwd, package, selection, run_id, canary_root, canary_settings_sha256)
    result = _run_gate_command(root, cwd, run_id, log_phase, argv, runner, log_paths, engine=engine,
                               target=target, named_file=named_file, logged_process=logged_process,
                               log_directory=log_directory, record_logs=record_logs)
    if getattr(result, "returncode", 1) != 0:
        detail = failed_output(root, run_id, result, log_path=log_paths.get(log_phase))
        if suite_phase == "preflight":
            detail = f"{detail}\n{_PREFLIGHT_SETUP}"
        raise LocalReleaseError(f"local-release-command-failed: {detail}")
    if suite_phase in {"image", "canary"}:
        return _canary_endpoint(result.stdout)
    return None


def _canary_endpoint(output):
    observed = re.findall(
        r"(?m)^ANECHOIC_CANARY_ENDPOINT (http://127\.0\.0\.1:([1-9][0-9]{0,4})/anechoic/mcp)$",
        output,
    )
    if len(observed) != 1 or int(observed[0][1]) > 65535:
        raise LocalReleaseError("local-release-canary-endpoint-invalid")
    return observed[0][0]
