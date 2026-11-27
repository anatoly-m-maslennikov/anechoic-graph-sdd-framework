"""Persist one structured report for each Test Suite command."""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from time import monotonic


@contextmanager
def suite_report(root, arguments):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
        import owned_temporary_root  # fmt: skip

    if arguments.phase == "functional" and os.environ.get(
        "ANECHOIC_FUNCTIONAL_HISTORY_ROOT"
    ):
        from .functional_history import history_roots

        root = history_roots(root)[-1]
    directory = owned_temporary_root(root, "test_reports")
    started = datetime.now(timezone.utc)
    clock = monotonic()
    report = {
        "started_at": started.isoformat(),
        "phase": arguments.phase,
        "test_modules": arguments.test_modules,
        "required": arguments.required,
        "candidate_image": arguments.candidate_image,
        "run_id": arguments.run_id,
        "step": "validate",
        "exit_code": 1,
        "selected_modules": 0,
        "modules": [],
    }
    try:
        yield report
    except KeyboardInterrupt:
        report["exit_code"] = 130
        raise
    except Exception as error:
        report["error"] = str(error)
        raise
    finally:
        _write_report(directory, started, clock, report)


def record_module(modules, path, result):
    successful, count, skips, stdout, stderr, elapsed, diagnostic = result
    print(f"Test module FINISH: {path}", flush=True)
    print(stdout, end="", flush=True)
    print(stderr, end="", file=sys.stderr, flush=True)
    if diagnostic is not None:
        print(
            f"Test module failed: {path}: {diagnostic}",
            file=sys.stderr,
            flush=True,
        )
    print(f"Module time: {path}: {elapsed:.3f}s", flush=True)
    entry = {
        "path": path,
        "status": "passed" if successful else "failed",
        "tests_run": count,
        "skipped": skips,
        "elapsed_seconds": round(elapsed, 3),
    }
    marker = "ANECHOIC_TEST_METRICS "
    for line in stdout.splitlines():
        if line.startswith(marker):
            try:
                metrics = json.loads(line[len(marker) :])
            except json.JSONDecodeError as error:
                entry["metrics_error"] = str(error)
                print(
                    f"Invalid test metrics: {path}: {error}",
                    file=sys.stderr,
                    flush=True,
                )
            else:
                entry.setdefault("metrics", []).append(metrics)
    if not successful:
        entry.update(stdout=stdout, stderr=stderr, error=diagnostic)
    modules.append(entry)


def _write_report(directory, started, clock, report):
    modules = report["modules"]
    report["tests_run"] = sum(module["tests_run"] for module in modules)
    report["skipped"] = sum(module["skipped"] for module in modules)
    report["failed_modules"] = sum(
        module["status"] == "failed" for module in modules
    )
    report["elapsed_seconds"] = round(monotonic() - clock, 3)
    report["status"] = {0: "passed", 130: "interrupted"}.get(
        report["exit_code"], "failed"
    )
    prefix = f"{started:%Y-%m-%d_%H-%M-%SZ}-{report['phase']}-"
    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=directory,
        prefix=prefix,
        suffix=".tmp",
        delete=False,
    ) as output:
        json.dump(report, output, indent=2)
        output.write("\n")
    path = Path(output.name).with_suffix(".json")
    Path(output.name).rename(path)
    print(f"Test report: {path}", file=sys.stderr, flush=True)
