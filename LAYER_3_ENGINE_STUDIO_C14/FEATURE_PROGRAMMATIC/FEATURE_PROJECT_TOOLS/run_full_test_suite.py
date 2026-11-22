"""Run every source test module in a fresh interpreter; report skips honestly."""


from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import nullcontext
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import time

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import python_boundaries, source_sizes
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.functional_suite import _select_test_modules, functional_modules
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.full_suite_docker import APP, candidate_test_image, current_code_test_image

WORKBENCH = Path("LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH")
WORKBENCH_TESTS = WORKBENCH / (WORKBENCH.name + "__tests")
MCP_TESTS = APP / (APP.name + "__tests")
CODE_ROOTS = ("LAYER_3_ENGINE_STUDIO_C14", "LAYER_5_FRAMEWORK_DELIVERY", "RUNTIME_SETUP")
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


def _module_environment(child, environment):
    environment = {
        **(os.environ if environment is None else environment),
        "ANECHOIC_DOCKER_E2E": "1",
        "ANECHOIC_DOCKER_QUERY_E2E": "1",
        "PYTHONPATH": str(child),
    }
    environment.pop("PYTHONHOME", None)
    return environment


def _module_command(child, module, environment, required):
    name = ".".join(module.relative_to(child).with_suffix("").parts)
    command = (sys.executable,)
    if child.name != CODE_ROOTS[0]:
        environment.pop("VIRTUAL_ENV", None)
        environment["UV_PROJECT_ENVIRONMENT"] = (
            ".venv-release" if child.name == CODE_ROOTS[1] else ".venv-setup"
        )
        command = ("uv", "run", "--project", str(child), "--locked", "--no-env-file", "python")
    return (*command, "-B", "-P", "-c", CHILD, name, *(("required",) if required else ()))


def run_module(
    root: Path, module: Path, environment=None
) -> tuple[bool, int, int, str, str, float, str | None]:
    """Return one isolated module's result and output for coherent reporting."""
    started = time.monotonic()
    child = root / module.relative_to(root).parts[0]
    environment = _module_environment(child, environment)
    environment["ANECHOIC_TEST_IMPORT_DIRS"] = os.pathsep.join((
        str(module.parent), str(root / WORKBENCH / "FEATURE_WORKBENCH_BACKEND"),
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
            timeout=MODULE_TIMEOUT_SECONDS,
            env=environment,
        )
        counts = [
            line[len(RESULT_MARKER) :]
            for line in result.stdout.splitlines()
            if line.startswith(RESULT_MARKER)
        ]
        observed = json.loads(counts[-1]) if counts else {"tests": 0, "skipped": 0}
        return (
            result.returncode == 0 and bool(counts),
            observed["tests"],
            observed["skipped"],
            result.stdout,
            result.stderr,
            time.monotonic() - started,
            None,
        )
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        stdout = _output_text(error.stdout) if isinstance(error, subprocess.TimeoutExpired) else ""
        stderr = _output_text(error.stderr) if isinstance(error, subprocess.TimeoutExpired) else ""
        return False, 0, 0, stdout, stderr, time.monotonic() - started, str(error)


def _docker_module(root: Path, module: Path) -> bool:
    return module.parent in (root / MCP_TESTS, root / WORKBENCH_TESTS) and (
        module.stem.endswith("_docker_e2e") or module.stem == "test_selected_query_mcp_e2e"
    )


def _run_static_checks(root: Path) -> int:
    print("Static check: unused Python imports", flush=True)
    try:
        status = subprocess.run(
            (sys.executable, "-m", "ruff", "check", "--select", "F401", "--no-fix", *CODE_ROOTS),
            cwd=root, check=False, timeout=60,
        ).returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"Static check failed: {error}", file=sys.stderr)
        return 1

    return status or source_sizes.check(root) or int(bool(python_boundaries.check(root)))

def run_full_suite(root: Path, test_modules: tuple[str, ...] | None = None, *,
                   image_mode: str = "existing", phase: str = "full",
                   candidate_image: str | None = None) -> int:
    """Attempt the complete discovered suite and fail on test or import errors."""
    if (phase not in ("full", "static", "unit", "functional", "e2e") or
            (phase == "e2e") != (candidate_image is not None) or
            (candidate_image is not None and (not isinstance(candidate_image, str)
             or not re.fullmatch(r"sha256:[0-9a-f]{64}", candidate_image))) or
            (phase != "full" and test_modules is not None)):
        print("Invalid test phase or candidate image selection", file=sys.stderr)
        return 1
    if phase == "static" or (phase in ("full", "unit", "functional") and test_modules is None):
        status = _run_static_checks(root)
        if status or phase == "static":
            return status
    modules = discover_test_modules(root)
    if phase == "functional":
        try:
            modules = functional_modules(root, modules, _docker_module)
        except ValueError as error:
            print(f"Invalid functional test selection: {error}", file=sys.stderr)
            return 1
    elif phase != "full":
        modules = [module for module in modules if _docker_module(root, module) == (phase == "e2e")]
    scope = phase if test_modules is None else "focused"
    if test_modules is None:
        selection = "all discovered modules" if phase == "full" else f"{phase} modules"
    else:
        try:
            modules = _select_test_modules(root, modules, test_modules)
        except ValueError as error:
            print(f"Invalid focused test selection: {error}", file=sys.stderr)
            return 1
        selection = ", ".join(test_modules)
    print(f"Test scope: {scope}; selected modules: {selection}")
    if not modules:
        print("No source test modules found", file=sys.stderr)
        return 1
    return _run_selected_modules(root, modules, candidate_image, image_mode, required=phase == "functional")


def _run_selected_modules(root, modules, candidate_image, image_mode, *, required=False):
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
            return _run_modules(root, modules, environment)
    except Exception as error:
        print(f"Required test environment failed: {error}", file=sys.stderr)
        return 1


def _output_text(output: str | bytes | None) -> str:
    return output.decode("utf-8", errors="replace") if isinstance(output, bytes) else output or ""


def _record_modules(root: Path, pending: dict) -> tuple[list[str], int, int]:
    failed = []
    tests = skipped = 0
    for future in as_completed(pending):
        module = pending.pop(future)
        successful, count, skips, stdout, stderr, elapsed, diagnostic = future.result()
        print(f"Test module FINISH: {module.relative_to(root)}", flush=True)
        print(stdout, end="", flush=True)
        print(stderr, end="", file=sys.stderr, flush=True)
        if diagnostic is not None:
            print(
                f"Test module failed: {module.relative_to(root)}: {diagnostic}", file=sys.stderr,
                flush=True,
            )
        print(f"Module time: {module.relative_to(root)}: {elapsed:.3f}s", flush=True)
        tests += count
        skipped += skips
        if not successful:
            failed.append(module.relative_to(root).as_posix())
    return failed, tests, skipped


def _run_modules(root: Path, modules: list[Path], environment: dict) -> int:
    browser = root / MCP_TESTS / "test_native_import_graph_docker_e2e.py"
    failed, tests, skipped = [], 0, 0
    with ThreadPoolExecutor(max_workers=2) as ordinary, ThreadPoolExecutor(max_workers=2) as docker:
        try:
            if browser in modules:
                failed, tests, skipped = _record_modules(root, {docker.submit(run_module, root, browser, environment): browser})
            pending = {
                (docker if _docker_module(root, module) else ordinary).submit(
                    run_module, root, module, environment
                ): module
                for module in modules if module != browser
            }
            other_failed, other_tests, other_skipped = _record_modules(root, pending)
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
    parser.add_argument("--image-mode", choices=("refresh", "existing"), default="existing")
    parser.add_argument("--phase", choices=("full", "static", "unit", "functional", "e2e", "canary"), default="full")
    parser.add_argument("--candidate-image")
    parser.add_argument("--canary-package", type=Path)
    parser.add_argument("--canary-selection")
    parser.add_argument("--run-id")
    arguments = parser.parse_args()
    root = arguments.project_root.resolve(strict=True)
    if arguments.phase == "canary":
        if (arguments.test_modules is not None or arguments.image_mode != "existing" or
                arguments.candidate_image is None or arguments.canary_package is None or not arguments.run_id
                or arguments.canary_selection is None):
            print("Invalid canary selection", file=sys.stderr)
            return 1
        try:
            from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS._release_canary import verify_candidate_image
            endpoint = verify_candidate_image(root, arguments.canary_package, arguments.candidate_image,
                                              run_id=arguments.run_id,
                                              selection=json.loads(arguments.canary_selection))
        except Exception as error:
            print(f"Canary failed: {error}", file=sys.stderr)
            return 1
        print(f"ANECHOIC_CANARY_ENDPOINT {endpoint}")
        return 0
    if arguments.canary_package is not None or arguments.canary_selection is not None or arguments.run_id is not None:
        print("Canary arguments require the canary phase", file=sys.stderr)
        return 1
    return run_full_suite(
        root, test_modules=tuple(arguments.test_modules) if arguments.test_modules is not None else None,
        image_mode=arguments.image_mode, phase=arguments.phase, candidate_image=arguments.candidate_image,
    )


if __name__ == "__main__":
    raise SystemExit(main())
