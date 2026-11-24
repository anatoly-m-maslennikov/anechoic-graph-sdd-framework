"""Run every source test module in a fresh interpreter; report skips honestly."""


from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import nullcontext
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from . import (_release_canary as _release_canary, full_suite_docker as full_suite_docker,
               prune_private_tmp as prune_private_tmp, source_line_length as source_line_length, static_checks as static_checks)
from .python_bytecode import (python_findings as python_findings, shell_findings as shell_findings,
                              unsafe as unsafe, yaml_findings as yaml_findings)
from .source_sizes import (check_functions as check_functions, check_module as check_module,
                           python_functions as python_functions, web_functions as web_functions)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.functional_suite import (
    MCP_TESTS as MCP_TESTS, WORKBENCH, _test_phase, select_phase_modules, valid_test_request,
)
from .full_suite_docker import (APP as APP, IMAGE_DEADLINES, candidate_test_image,
                                current_code_test_image, image_deadline_mode)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.static_checks import CODE_ROOTS, check as _run_static_checks
from .suite_cli import run_phase
from .suite_preflight import run_preflight
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.suite_report import record_module, suite_report

MODULE_TIMEOUT_SECONDS = 3600
RESULT_MARKER = "ANECHOIC_TEST_COUNTS "
CHILD = """
import json, os, sys, unittest
sys.path.extend(os.environ.pop("ANECHOIC_TEST_IMPORT_DIRS").split(os.pathsep))
suite = unittest.defaultTestLoader.loadTestsFromName(sys.argv[1])
count = suite.countTestCases()
result = unittest.TextTestRunner(verbosity=2).run(suite)
required_skips = [(test.id(), reason) for test, reason in result.skipped
                  if len(sys.argv) > 2 or "_e2e" in sys.argv[1] or "_e2e." in test.id()]
if required_skips:
    label = "functional" if len(sys.argv) > 2 else "integration"
    print("Required " + label + " tests skipped: " + repr(required_skips), file=sys.stderr)
print("ANECHOIC_TEST_COUNTS " + json.dumps({"tests": result.testsRun, "skipped": len(result.skipped)}))
if not count:
    print("No test cases loaded", file=sys.stderr)
sys.exit(0 if count and result.wasSuccessful() and not required_skips else 1)
"""


def discover_test_modules(root: Path) -> list[Path]:
    """Select source modules, not caches or copied tests inside test fixtures."""

    def failed(error: OSError) -> None:
        raise error

    modules = []
    for name in CODE_ROOTS:
        source = root / name
        if source.is_symlink() or not source.is_dir():
            raise OSError(f"source test root is unavailable: {source}")
        for folder, directories, filenames in os.walk(source, followlinks=False, onerror=failed):
            directory = Path(folder)
            parts = directory.relative_to(source).parts
            test_package = directory.name == directory.parent.name + "__tests"
            directories[:] = [
                entry
                for entry in directories
                if not entry.startswith(".")
                and entry != "__pycache__"
                and not (test_package and entry == "assets")
                and not (entry == "tests" and "tests" in parts)
            ]
            for entry in directories:
                if (Path(folder) / entry).is_symlink():
                    raise OSError(
                        f"source test directory is a symbolic link: {Path(folder) / entry}"
                    )
            for filename in filenames:
                path = Path(folder) / filename
                if (
                    filename.startswith("test_")
                    and path.suffix == ".py"
                    and path.stem.isidentifier()
                    and not path.stem.endswith(("__pub", "__shared"))
                ):
                    if path.is_symlink():
                        raise OSError(f"test module is a symbolic link: {path}")
                    modules.append(path)
    return sorted(modules)


def _module_environment(child, environment, *, image_module):
    inherited = os.environ if environment is None else environment
    environment = {key: value for key, value in inherited.items() if key not in ("PYTHONHOME", IMAGE_DEADLINES)}
    environment.update(ANECHOIC_DOCKER_E2E="1", ANECHOIC_DOCKER_QUERY_E2E="1", PYTHONPATH=str(child))
    if image_module:
        environment[IMAGE_DEADLINES] = image_deadline_mode(inherited)
    return environment


def _module_command(child, module, environment, required):
    name = ".".join(module.relative_to(child).with_suffix("").parts)
    command = (sys.executable, "-B")
    if child.name != CODE_ROOTS[0]:
        environment.pop("VIRTUAL_ENV", None)
        environment["UV_PROJECT_ENVIRONMENT"] = (
            str(child / (".venv-release" if child.as_posix().endswith(CODE_ROOTS[1]) else ".venv-setup"))
        )
        command = ("uv", "run", "--project", str((child.parent.parent if child.as_posix().endswith(CODE_ROOTS[1]) else child.parent) / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72" / ("release" if child.as_posix().endswith(CODE_ROOTS[1]) else "setup")), "--locked", "--no-env-file", "python", "-B")
    return (*command, "-P", "-c", CHILD, name, *(("required",) if required else ()))


def run_module(
    root: Path, module: Path, environment=None
) -> tuple[bool, int, int, str, str, float, str | None]:
    """Return one isolated module's result and output for coherent reporting."""
    started = time.monotonic()
    child = next(root / name for name in CODE_ROOTS if module.is_relative_to(root / name))
    environment = _module_environment(child, environment, image_module=_docker_module(root, module))
    environment["ANECHOIC_TEST_IMPORT_DIRS"] = os.pathsep.join((
        str(module.parent), str(module.parent.parent), str(root / WORKBENCH / "FEATURE_WORKBENCH_BACKEND"),
    ))
    required = environment.pop("ANECHOIC_FUNCTIONAL_REQUIRED", None) == "1"
    print(f"Test module START: {module.relative_to(root)}", flush=True)
    try:
        result = subprocess.run(
            _module_command(child, module, environment, required),
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=None if environment.get(IMAGE_DEADLINES) == "0" else MODULE_TIMEOUT_SECONDS,
            env=environment,
        )
        counts = [
            line[len(RESULT_MARKER) :]
            for line in result.stdout.splitlines()
            if line.startswith(RESULT_MARKER)
        ]
        observed = json.loads(counts[-1]) if counts else {"tests": 0, "skipped": 0}
        return (
            result.returncode == 0 and bool(counts), observed["tests"],
            observed["skipped"], result.stdout, result.stderr,
            time.monotonic() - started, None,
        )
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        stdout = _output_text(error.stdout) if isinstance(error, subprocess.TimeoutExpired) else ""
        stderr = _output_text(error.stderr) if isinstance(error, subprocess.TimeoutExpired) else ""
        return False, 0, 0, stdout, stderr, time.monotonic() - started, str(error)


def _docker_module(root: Path, module: Path) -> bool:
    return _test_phase(root, module) == "image"


def run_full_suite(root: Path, test_modules: tuple[str, ...] | None = None, *,
                   image_mode: str = "existing", phase: str = "full",
                   candidate_image: str | None = None, required: bool = False,
                   report: dict | None = None) -> int:
    """Run a source phase; retain legacy Python phase names for existing callers."""
    report = {} if report is None else report
    if not valid_test_request(phase, candidate_image, test_modules, required):
        print("Invalid test phase or candidate image selection", file=sys.stderr)
        return 1
    if phase == "preflight":
        return run_preflight(root, report)
    if phase in ("full", "static") and test_modules is None:
        report["step"] = "static_checks"
        status = _run_static_checks(root)
        if status:
            return status
    host_gate = required or phase == "functional"
    report["step"] = "discovery"
    try:
        modules = select_phase_modules(root, discover_test_modules(root), phase, test_modules, host_gate)
    except OSError as error:
        report["error"] = str(error)
        print(f"Test discovery failed: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        report["error"] = str(error)
        print(f"Invalid test selection: {error}", file=sys.stderr)
        return 1
    scope = phase if test_modules is None else "focused"
    if test_modules is not None:
        selection = ", ".join(test_modules)
    elif host_gate:
        selection = ", ".join(module.relative_to(root).as_posix() for module in modules)
    else:
        selection = "all discovered modules" if phase == "full" else f"{phase} modules"
    print(f"Test scope: {scope}; selected modules: {selection}")
    report["selected_modules"] = len(modules)
    if not modules:
        if phase == "static":
            return 0
        print("No source test modules found", file=sys.stderr)
        return 1
    return _run_selected_modules(root, modules, candidate_image, image_mode,
                                 required=host_gate or phase in ("image", "e2e"), report=report)


def _run_selected_modules(root, modules, candidate_image, image_mode, *, required, report):
    report["step"] = "environment"
    integration = any(_docker_module(root, module) for module in modules)
    context = (candidate_test_image(root, candidate_image) if candidate_image is not None else
               current_code_test_image(root, use_packaged_assets=image_mode == "existing")
               if integration else nullcontext({}))
    try:
        with context as additions:
            environment = {**os.environ, **additions}
            if required:
                environment["ANECHOIC_FUNCTIONAL_REQUIRED"] = "1"
            else:
                environment.pop("ANECHOIC_FUNCTIONAL_REQUIRED", None)
            if integration:
                environment.pop("ANECHOIC_RELEASE_E2E_CONTEXT", None)
                environment.pop("ANECHOIC_CANDIDATE_IMAGE_DIGEST", None)
            report["step"] = "modules"
            return _run_modules(root, modules, environment, report.setdefault("modules", []))
    except Exception as error:
        report["error"] = str(error)
        print(f"Required test environment failed: {error}", file=sys.stderr)
        return 1


def _output_text(output: str | bytes | None) -> str:
    return output.decode("utf-8", errors="replace") if isinstance(output, bytes) else output or ""


def _record_modules(root: Path, pending: dict, modules_report: list) -> tuple[list[str], int, int]:
    failed = []
    tests = skipped = 0
    for future in as_completed(pending):
        module = pending.pop(future)
        result = future.result()
        successful, count, skips, *_ = result
        record_module(modules_report, module.relative_to(root).as_posix(), result)
        tests += count
        skipped += skips
        if not successful:
            failed.append(module.relative_to(root).as_posix())
    return failed, tests, skipped


def _run_modules(root: Path, modules: list[Path], environment: dict, modules_report: list) -> int:
    browser = next((module for module in modules if module.name == "test_native_import_graph_docker_e2e.py"
                    and _docker_module(root, module)), None)
    failed, tests, skipped = [], 0, 0
    with ThreadPoolExecutor(max_workers=2) as ordinary, ThreadPoolExecutor(max_workers=2) as docker:
        try:
            if browser in modules:
                first = {docker.submit(run_module, root, browser, environment): browser}
                failed, tests, skipped = _record_modules(root, first, modules_report)
            pending = {
                (docker if _docker_module(root, module) else ordinary).submit(
                    run_module, root, module, environment
                ): module
                for module in modules if module != browser
            }
            other_failed, other_tests, other_skipped = _record_modules(root, pending, modules_report)
            failed.extend(other_failed)
            tests += other_tests
            skipped += other_skipped
        except KeyboardInterrupt:
            for executor in (ordinary, docker):
                executor.shutdown(wait=False, cancel_futures=True)
            raise
    if failed:
        print("Failed test modules: " + ", ".join(failed), file=sys.stderr)
    print(
        f"Modules: {len(modules)}; tests run: {tests}; skipped: {skipped}; failed modules: {len(failed)}"
    )
    return int(bool(failed))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--test-module", action="append", dest="test_modules", metavar="PATH")
    parser.add_argument("--phase", choices=("preflight", "static", "functional", "unit", "image"), default="unit")
    parser.add_argument("--required", action="store_true", help="run the configured required host selection with the unit phase")
    parser.add_argument("--candidate-image")
    parser.add_argument("--canary-package", type=Path)
    parser.add_argument("--canary-project-root", type=Path)
    parser.add_argument("--canary-selection")
    parser.add_argument("--run-id")
    arguments = parser.parse_args()
    root = arguments.project_root.resolve(strict=True)
    with suite_report(root, arguments) as report:
        report["exit_code"] = run_phase(root, arguments, report, run_full_suite)
        return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
