"""Run one suite module with the original runner's patch points."""

from pathlib import Path


def run_module(runner, root: Path, module: Path, environment=None):
    started = runner.time.monotonic()
    child = next(
        root / name
        for name in runner.CODE_ROOTS
        if module.is_relative_to(root / name)
    )
    environment = runner._module_environment(
        child, environment, image_module=runner._docker_module(root, module)
    )
    environment["ANECHOIC_TEST_IMPORT_DIRS"] = runner.os.pathsep.join(
        (
            str(module.parent),
            str(module.parent.parent),
            str(root / runner.WORKBENCH / "FEATURE_IWE_CONSOLE_BACKEND"),
        )
    )
    required = environment.pop("ANECHOIC_FUNCTIONAL_REQUIRED", None) == "1"
    print(f"Test module START: {module.relative_to(root)}", flush=True)
    try:
        result = runner.subprocess.run(
            runner._module_command(child, module, environment, required),
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=None
            if environment.get(runner.IMAGE_DEADLINES) == "0"
            else runner.MODULE_TIMEOUT_SECONDS,
            env=environment,
        )
        return _result(runner, result, started)
    except (OSError, runner.subprocess.TimeoutExpired, ValueError) as error:
        return _error(runner, error, started)


def _result(runner, result, started):
    counts = [
        line[len(runner.RESULT_MARKER) :]
        for line in result.stdout.splitlines()
        if line.startswith(runner.RESULT_MARKER)
    ]
    observed = (
        runner.json.loads(counts[-1]) if counts else {"tests": 0, "skipped": 0}
    )
    return (
        result.returncode == 0 and bool(counts),
        observed["tests"],
        observed["skipped"],
        result.stdout,
        result.stderr,
        runner.time.monotonic() - started,
        None,
    )


def _error(runner, error, started):
    stdout = (
        runner._output_text(error.stdout)
        if isinstance(error, runner.subprocess.TimeoutExpired)
        else ""
    )
    stderr = (
        runner._output_text(error.stderr)
        if isinstance(error, runner.subprocess.TimeoutExpired)
        else ""
    )
    return (
        False,
        0,
        0,
        stdout,
        stderr,
        runner.time.monotonic() - started,
        str(error),
    )


def discover_selected(runner, root, selection, report):
    phase, test_modules, host_gate, functional_suite, image_suite = selection
    report["step"] = "discovery"
    try:
        modules = runner._discover_for_phase(
            root,
            phase,
            test_modules,
            host_gate,
            functional_suite,
            image_suite,
            report,
        )
    except (OSError, ValueError) as error:
        report["error"] = str(error)
        label = (
            "Test discovery failed"
            if isinstance(error, OSError)
            else "Invalid test selection"
        )
        print(f"{label}: {error}", file=runner.sys.stderr)
        return None
    return modules


def schedule_modules(
    runner,
    root,
    modules,
    browser,
    environment,
    modules_report,
    ordinary,
    docker,
):
    failed, tests, skipped = [], 0, 0
    if browser in modules:
        first = {
            docker.submit(
                runner.run_module, root, browser, environment
            ): browser
        }
        failed, tests, skipped = runner._record_modules(
            root, first, modules_report
        )
    pending = {
        (docker if runner._docker_module(root, module) else ordinary).submit(
            runner.run_module, root, module, environment
        ): module
        for module in modules
        if module != browser
    }
    other_failed, other_tests, other_skipped = runner._record_modules(
        root, pending, modules_report
    )
    failed.extend(other_failed)
    tests += other_tests
    skipped += other_skipped
    return failed, tests, skipped


def finish_suite(
    runner,
    root,
    modules,
    phase,
    host_gate,
    candidate_image,
    image_mode,
    report,
):
    report["selected_modules"] = len(modules)
    if not modules:
        if phase == "static":
            return 0
        print("No source test modules found", file=runner.sys.stderr)
        return 1
    return runner._run_selected_modules(
        root,
        modules,
        candidate_image,
        image_mode,
        required=host_gate or phase in ("image", "e2e"),
        report=report,
    )
