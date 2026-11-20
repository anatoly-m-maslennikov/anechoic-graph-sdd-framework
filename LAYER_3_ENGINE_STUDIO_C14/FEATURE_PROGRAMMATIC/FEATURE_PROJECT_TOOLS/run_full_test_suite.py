"""Run every source test module in a fresh interpreter; report skips honestly."""

# CA-M-409@14

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager, nullcontext
import json
from itertools import chain
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from full_suite_docker import APP, current_code_test_image

PROGRAMMATIC = Path("LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC")
WORKBENCH = Path("LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH")
WORKBENCH_TESTS = WORKBENCH / (WORKBENCH.name + "__tests")
MCP_TESTS = APP / (APP.name + "__tests")
CODE_ROOTS = ("LAYER_3_ENGINE_STUDIO_C14", "LAYER_5_FRAMEWORK_DELIVERY")
MODULE_TIMEOUT_SECONDS = 3600
RESULT_MARKER = "ANECHOIC_TEST_COUNTS "
CHILD = """
import json, sys, unittest
sys.path.insert(0, sys.argv[1])
suite = unittest.defaultTestLoader.loadTestsFromName(sys.argv[2])
count = suite.countTestCases()
result = unittest.TextTestRunner(verbosity=2).run(suite)
required_skips = [(test.id(), reason) for test, reason in result.skipped
                  if "_e2e" in sys.argv[2] or "_e2e." in test.id()]
if required_skips:
    print("Required integration tests skipped: " + repr(required_skips), file=sys.stderr)
print("ANECHOIC_TEST_COUNTS " + json.dumps({"tests": result.testsRun, "skipped": len(result.skipped)}))
if not count:
    print("No test cases loaded", file=sys.stderr)
sys.exit(0 if count and result.wasSuccessful() and not required_skips else 1)
"""


@contextmanager
def legacy_test_fixture(root: Path):
    """Run legacy data assumptions in an owned clone of the current source."""
    with tempfile.TemporaryDirectory(prefix="anechoic-legacy-tests-") as temporary:
        temporary_root = Path(temporary).resolve(strict=True)
        fixture = temporary_root / "project"
        status = subprocess.run(("git", "status", "--porcelain", "--untracked-files=no"),
                                cwd=root, capture_output=True, check=True, timeout=300).stdout
        if status:
            raise OSError("legacy fixture requires clean tracked source")
        head = subprocess.run(("git", "rev-parse", "HEAD"), cwd=root,
                              capture_output=True, check=True, timeout=300).stdout
        subprocess.run(("git", "clone", "--quiet", "--shared", "--no-hardlinks", "--no-tags",
                        str(root), str(fixture)),
                       check=True, timeout=300)
        cloned_head = subprocess.run(("git", "rev-parse", "HEAD"), cwd=fixture,
                                     capture_output=True, check=True, timeout=300).stdout
        if head != cloned_head:
            raise OSError("source HEAD changed while creating legacy fixture")
        native, legacy = fixture / ".anechoic_anechoic", fixture / ".anechoic_legacy"
        if any(path.is_symlink() or not path.is_dir() for path in (native, legacy)):
            raise OSError("native control or retained legacy fixture is missing")
        native.rename(temporary_root / "native-control")
        legacy.rename(native)
        for relative in (
            Path(".anechoic_tmp/workbench/extensions"),
            Path(".anechoic_tmp/workbench/playwright-browsers"),
            WORKBENCH / "FEATURE_WORKBENCH_FRONTEND/node_modules",
        ):
            source, destination = root / relative, fixture / relative
            if source.is_symlink():
                raise OSError(f"test cache is a symbolic link: {source}")
            if source.is_dir():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, destination, symlinks=True)
        print(f"Legacy test fixture: {fixture} (source HEAD {head.decode().strip()})", flush=True)
        yield fixture


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
                ):
                    if path.is_symlink():
                        raise OSError(f"test module is a symbolic link: {path}")
                    modules.append(path)
    return sorted(modules)


def _select_test_modules(
    root: Path, discovered: list[Path], selected: tuple[str, ...]
) -> list[Path]:
    if not isinstance(selected, tuple):
        raise ValueError("test-module selection must be a tuple")
    if not selected:
        raise ValueError("test-module selection is empty")
    if any(not isinstance(module, str) or not module for module in selected):
        raise ValueError("test-module selection contains an invalid path")
    if len(set(selected)) != len(selected):
        raise ValueError("test-module selection contains duplicates")
    available = {module.relative_to(root).as_posix(): module for module in discovered}
    missing = [module for module in selected if module not in available]
    if missing:
        raise ValueError("test-module selection is not discovered: " + ", ".join(missing))
    return [available[module] for module in selected]


def run_module(
    root: Path, module: Path, environment=None
) -> tuple[bool, int, int, str, str, float, str | None]:
    """Return one isolated module's result and output for coherent reporting."""
    started = time.monotonic()
    environment = {
        **(os.environ if environment is None else environment),
        "ANECHOIC_DOCKER_E2E": "1",
        "ANECHOIC_DOCKER_QUERY_E2E": "1",
    }
    programmatic = root / PROGRAMMATIC
    apps = root / WORKBENCH.parent
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = os.pathsep.join(
        path for path in (str(programmatic / "FEATURE_TOOLS"), str(programmatic), str(apps),
                          str(apps / "APP_WORKBENCH"), str(root / APP.parent), existing_pythonpath) if path
    )
    print(f"Test module START: {module.relative_to(root)}", flush=True)
    try:
        result = subprocess.run(
            (sys.executable, "-B", "-c", CHILD, str(module.parent), module.stem),
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


def run_full_suite(root: Path, test_modules: tuple[str, ...] | None = None, *,
                   image_mode: str = "refresh") -> int:
    """Attempt the complete discovered suite and fail on test or import errors."""
    modules = discover_test_modules(root)
    scope = "full" if test_modules is None else "focused"
    if test_modules is None:
        selection = "all discovered modules"
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
    integration = any(_docker_module(root, module) for module in modules)
    context = (current_code_test_image(root, use_packaged_assets=image_mode == "existing")
               if integration else nullcontext({}))
    try:
        with context as additions:
            environment = {**os.environ, **additions}
            if integration:
                environment.pop("ANECHOIC_RELEASE_E2E_CONTEXT", None)
                environment.pop("ANECHOIC_CANDIDATE_IMAGE_DIGEST", None)
            return _run_modules(root, modules, environment, integration)
    except Exception as error:
        print(f"Required test environment failed: {error}", file=sys.stderr)
        return 1


def _output_text(output: str | bytes | None) -> str:
    return output.decode("utf-8", errors="replace") if isinstance(output, bytes) else output or ""


def _record_modules(root: Path, pending: dict) -> tuple[list[str], int, int]:
    failed = []
    tests = skipped = 0
    if not pending:
        return failed, tests, skipped
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


def _run_modules(root: Path, modules: list[Path], environment: dict, integration: bool) -> int:
    failed = []
    tests = skipped = 0
    workbench_tests = root / WORKBENCH_TESTS
    isolated = [module for module in modules if module.parent == workbench_tests and module.stem in {
        "test_workbench_docker_e2e", "test_workbench_resource_docker_e2e",
    }]
    with ThreadPoolExecutor(max_workers=2) as ordinary, ThreadPoolExecutor(max_workers=2) as docker:
        try:
            pending = {
                (docker if _docker_module(root, module) else ordinary).submit(
                    run_module, root, module, environment
                ): module
                for module in modules if module not in isolated
            }
            # Performance gates need an uncontended Docker daemon.
            for batch in chain([pending], (
                {docker.submit(run_module, root, module, environment): module} for module in isolated
            )):
                completed_failed, completed_tests, completed_skipped = _record_modules(root, batch)
                failed.extend(completed_failed)
                tests += completed_tests
                skipped += completed_skipped
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
    parser.add_argument("--image-mode", choices=("refresh", "existing"), default="refresh")
    parser.add_argument("--legacy-fixture", action="store_true", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    root = arguments.project_root.resolve(strict=True)
    try:
        with legacy_test_fixture(root) if arguments.legacy_fixture else nullcontext(root) as test_root:
            return run_full_suite(
                test_root, test_modules=tuple(arguments.test_modules) if arguments.test_modules is not None else None,
                image_mode=arguments.image_mode,
            )
    except (OSError, subprocess.SubprocessError) as error:
        print(f"Required legacy test fixture failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
