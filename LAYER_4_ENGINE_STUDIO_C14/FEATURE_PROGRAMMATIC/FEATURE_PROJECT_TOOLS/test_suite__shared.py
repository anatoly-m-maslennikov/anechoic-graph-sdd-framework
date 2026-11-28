"""Run source test modules in fresh interpreters and report skips."""

from __future__ import annotations

import argparse as argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import nullcontext
import json as json
import os
from pathlib import Path
import subprocess as subprocess
import sys
import time as time

from . import (
    static_checks as static_checks,
)

from .source_inventory import (
    source_inventory__shared as source_comments,  # noqa: F401
    source_line_length as source_line_length,
)
from . import prune_private_tmp as prune_private_tmp
from .suite_runner import suite_preflight as suite_preflight
from .release_image import (
    release_image__shared as full_suite_docker,  # noqa: F401
)
from .language_checks.python_bytecode import (
    python_findings as python_findings,
    shell_findings as shell_findings,
    unsafe as unsafe,
    yaml_findings as yaml_findings,
)
from .source_inventory.source_sizes import (
    check_functions as check_functions,
    check_module as check_module,
    python_functions as python_functions,
    web_functions as web_functions,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.functional_suite import (
    MCP_TESTS as MCP_TESTS,
    WORKBENCH as WORKBENCH,
    _test_phase,
    select_phase_modules,
    valid_test_request,
)
from .release_image.release_image__shared import (
    APP as APP,
    IMAGE_DEADLINES as IMAGE_DEADLINES,
    candidate_test_image,
    current_code_test_image,
    image_deadline_mode as image_deadline_mode,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.static_checks import (
    CODE_ROOTS as CODE_ROOTS,
    check as _run_static_checks,
)
from .suite_runner.suite_runner__shared import run_phase
from .suite_runner.suite_preflight import run_preflight
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    suite_runner.suite_report import (
    record_module,
    suite_report,
)

from .suite_runner._suite_runner_module import (
    discover_selected as _discover_selected,
    finish_suite as _finish_suite,
    run_module as _run_module,
    schedule_modules as _schedule_modules,
)
from .suite_runner._suite_runner_inputs import (
    CHILD as CHILD,
    _suite_parser as _suite_parser,
    _module_command as _module_command,
    _module_environment as _module_environment,
    _report_scope as _report_scope,
    discover_test_modules as discover_test_modules,
)

MODULE_TIMEOUT_SECONDS = 3600
RESULT_MARKER = "ANECHOIC_TEST_COUNTS "


def __getattr__(name: str):
    if name == "_release_canary":
        from .release_image import _release_canary

        return _release_canary
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def run_module(root: Path, module: Path, environment=None):
    """Run one isolated module and return its result and output."""
    return _run_module(sys.modules[__name__], root, module, environment)


def _docker_module(root: Path, module: Path) -> bool:
    return _test_phase(root, module) == "image"


def _discover_for_phase(
    root, phase, focused, host_gate, functional_suite, image_suite, report
):
    modules = select_phase_modules(
        root,
        discover_test_modules(root),
        phase,
        focused,
        host_gate,
        image_suite=image_suite,
    )
    if functional_suite == "fast":
        from .suite_runner.functional_history import select_fast

        return select_fast(root, modules, report)
    return modules


def _valid_phase_request(
    phase,
    candidate_image,
    test_modules,
    required,
    functional_suite,
    image_suite,
):
    if (
        functional_suite not in ("full", "fast")
        or functional_suite == "fast"
        and phase != "functional"
        or image_suite not in ("full", "fast")
        or image_suite == "fast"
        and phase != "image"
        or not valid_test_request(
            phase, candidate_image, test_modules, required
        )
    ):
        print(
            "Invalid test phase or candidate image selection", file=sys.stderr
        )
        return False
    return True


def run_full_suite(
    root: Path,
    test_modules: tuple[str, ...] | None = None,
    *,
    image_mode: str = "existing",
    phase: str = "full",
    candidate_image: str | None = None,
    required: bool = False,
    report: dict | None = None,
    functional_suite: str = "full",
    image_suite: str = "full",
) -> int:
    """Run a source phase and retain legacy Python phase names."""
    report = {} if report is None else report
    request = (phase, candidate_image, test_modules, required)
    if not _valid_phase_request(*request, functional_suite, image_suite):
        return 1
    if phase == "preflight":
        return run_preflight(root, report)
    if phase in ("full", "static") and test_modules is None:
        report["step"] = "static_checks"
        status = _run_static_checks(root)
        if status:
            return status
    host_gate = required or phase in ("functional", "canary")
    selection = (phase, test_modules, host_gate, functional_suite, image_suite)
    modules = _discover_selected(
        sys.modules[__name__], root, selection, report
    )
    if modules is None:
        return 1
    _report_scope(root, phase, test_modules, host_gate, image_suite, modules)
    return _finish_suite(
        sys.modules[__name__],
        root,
        modules,
        phase,
        host_gate,
        candidate_image,
        image_mode,
        report,
    )


def _run_selected_modules(
    root, modules, candidate_image, image_mode, *, required, report
):
    report["step"] = "environment"
    integration = any(_docker_module(root, module) for module in modules)
    context = (
        candidate_test_image(root, candidate_image)
        if candidate_image is not None
        else current_code_test_image(
            root, use_packaged_assets=image_mode == "existing"
        )
        if integration
        else nullcontext({})
    )
    try:
        with context as additions:
            environment = {**os.environ, **additions}
            environment.setdefault(
                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                str(root / ".anechoic_tmp/workbench/extensions"),
            )
            if required:
                environment["ANECHOIC_FUNCTIONAL_REQUIRED"] = "1"
            else:
                environment.pop("ANECHOIC_FUNCTIONAL_REQUIRED", None)
            if integration:
                environment.pop("ANECHOIC_RELEASE_E2E_CONTEXT", None)
                environment.pop("ANECHOIC_CANDIDATE_IMAGE_DIGEST", None)
            report["step"] = "modules"
            return _run_modules(
                root, modules, environment, report.setdefault("modules", [])
            )
    except Exception as error:
        report["error"] = str(error)
        print(f"Required test environment failed: {error}", file=sys.stderr)
        return 1


def _output_text(output: str | bytes | None) -> str:
    return (
        output.decode("utf-8", errors="replace")
        if isinstance(output, bytes)
        else output or ""
    )


def _record_modules(
    root: Path, pending: dict, modules_report: list
) -> tuple[list[str], int, int]:
    failed = []
    tests = skipped = 0
    for future in as_completed(pending):
        module = pending.pop(future)
        result = future.result()
        successful, count, skips, *_ = result
        record_module(
            modules_report, module.relative_to(root).as_posix(), result
        )
        tests += count
        skipped += skips
        if not successful:
            failed.append(module.relative_to(root).as_posix())
    return failed, tests, skipped


def _run_modules(
    root: Path, modules: list[Path], environment: dict, modules_report: list
) -> int:
    browser = next(
        (
            module
            for module in modules
            if module.name == "test_native_import_graph_docker_e2e.py"
            and _docker_module(root, module)
        ),
        None,
    )
    failed, tests, skipped = [], 0, 0
    host_workers = int(environment.get("ANECHOIC_TEST_FANOUT", "2"))
    image_workers = int(environment.get("ANECHOIC_TEST_IMAGE_FANOUT", "2"))
    if image_workers not in (2, 3):
        raise ValueError("ANECHOIC_TEST_IMAGE_FANOUT must be 2 or 3")
    with (
        ThreadPoolExecutor(max_workers=host_workers) as ordinary,
        ThreadPoolExecutor(max_workers=image_workers) as docker,
    ):
        try:
            failed, tests, skipped = _schedule_modules(
                sys.modules[__name__],
                root,
                modules,
                browser,
                environment,
                modules_report,
                ordinary,
                docker,
            )
        except KeyboardInterrupt:
            for executor in (ordinary, docker):
                executor.shutdown(wait=False, cancel_futures=True)
            raise
    if failed:
        print("Failed test modules: " + ", ".join(failed), file=sys.stderr)
    print(
        f"Modules: {len(modules)}; tests run: {tests}; "
        f"skipped: {skipped}; failed modules: {len(failed)}"
    )
    return int(bool(failed))


def main() -> int:
    parser = _suite_parser(__doc__)
    arguments = parser.parse_args()
    root = arguments.project_root.resolve(strict=True)
    with suite_report(root, arguments) as report:
        report["exit_code"] = run_phase(
            root, arguments, report, run_full_suite
        )
        return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
