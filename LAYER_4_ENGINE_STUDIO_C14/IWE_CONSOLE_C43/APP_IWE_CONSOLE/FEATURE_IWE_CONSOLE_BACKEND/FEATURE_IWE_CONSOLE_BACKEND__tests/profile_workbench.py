"Opt-in, isolated Workbench profiler; it is never a performance gate."

from __future__ import annotations

import argparse
import cProfile
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import resource
import shutil
import sys
import time
import tracemalloc
import uuid
from typing import Any


if __package__:
    from ._profiler_observations import _allocation_traces, _native_memory
    from ._profiler_observations import _digest_sources, _make_report
else:
    from _profiler_observations import _allocation_traces, _native_memory
    from _profiler_observations import _digest_sources, _make_report


REBUILD_CYCLES = 3
TRACE_FRAMES = 5
OWNER = "workbench-profile"
IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[5]
APPS_ROOT = IMPLEMENTATION_ROOT / "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43"
TOOLS_ROOT = (
    IMPLEMENTATION_ROOT
    / "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS"
)
BACKEND_ROOT = APPS_ROOT / "APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND"
KERNEL_ROOT = APPS_ROOT.parent / "KERNEL_MIXER_C59"


def _imports() -> None:
    for path in (APPS_ROOT.parent,):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def _temporary_root(project_root: Path) -> Path:
    _imports()
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
        PROJECT_SUPPORT.PROJECT_SELECTION.\
        PROJECT_SELECTION__shared import (
        resolve_project,
    )

    selection = resolve_project(project_root)
    temporary = selection.settings.get("paths", {}).get("temporary_root")
    if not isinstance(temporary, str) or not temporary:
        raise ValueError("Project settings must define paths.temporary_root")
    return (selection.root / temporary).resolve()


def output_directory(project_root: Path, requested: Path | None) -> Path:
    temporary = _temporary_root(project_root)
    candidate = (
        requested
        if requested is not None
        else temporary / OWNER / uuid.uuid4().hex
    ).resolve()
    if not candidate.is_relative_to(temporary):
        raise ValueError(
            "--output must stay beneath the selected Project temporary root"
        )
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def _code_hashes() -> dict[str, str]:
    paths = [
        BACKEND_ROOT / "source_capture/reader/source_reader.py",
        BACKEND_ROOT / "source_capture/source_rows.py",
        KERNEL_ROOT / "kernel_query/query_database/query_store.py",
        KERNEL_ROOT / "kernel_model/schema_state/content_schema.py",
        KERNEL_ROOT / "kernel_graph/projection_rows/projection_delta.py",
        KERNEL_ROOT / "kernel_runtime/relations_data/relations.py",
        TOOLS_ROOT / "ADAPTERS_C30/carriers/content/markdown_content__pub.py",
    ]
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
    }


def _source_digest(
    project_root: Path,
    atom_rows: list[dict[str, Any]],
    scope_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return _digest_sources(project_root, atom_rows, scope_rows, hashlib)


def _peak_rss_bytes() -> int:
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return raw if sys.platform == "darwin" else raw * 1024


def _measure_rebuilds(
    store,
    reader,
    atom_rows,
    scope_rows,
    relation_types,
    report,
    initial_started,
):
    store.replace(
        atom_rows,
        scope_rows,
        relation_types=relation_types,
        content_schema=reader.content_schema,
    )
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    report["measurements"].append(
        {
            "label": "initial_index",
            "instrumented_elapsed_seconds": round(
                time.perf_counter() - initial_started, 6
            ),
            "includes_source_capture_and_materialization": True,
            "python_current_bytes": current_bytes,
            "python_peak_bytes": peak_bytes,
            "process_high_water_rss_bytes": _peak_rss_bytes(),
            "process_high_water_rss_is_current_memory": False,
            "duckdb_managed_memory": _native_memory(store._connection),
        }
    )
    for number in range(1, REBUILD_CYCLES + 1):
        _measure_rebuild(
            store,
            reader,
            atom_rows,
            scope_rows,
            relation_types,
            report,
            number,
        )


def _measure_rebuild(
    store, reader, atom_rows, scope_rows, relation_types, report, number
):
    phase_started = time.perf_counter()
    store.replace(
        atom_rows,
        scope_rows,
        relation_types=relation_types,
        content_schema=reader.content_schema,
    )
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    report["measurements"].append(
        {
            "label": f"full_rebuild_{number}",
            "instrumented_elapsed_seconds": round(
                time.perf_counter() - phase_started, 6
            ),
            "includes_source_capture_and_materialization": False,
            "input": "same captured source projection",
            "python_current_bytes": current_bytes,
            "python_peak_bytes": peak_bytes,
            "process_high_water_rss_bytes": _peak_rss_bytes(),
            "process_high_water_rss_is_current_memory": False,
            "duckdb_managed_memory": _native_memory(store._connection),
        }
    )


def _capture_and_measure(
    project_root,
    database_directory,
    report,
    SourceReader,
    QueryStore,
    materialize,
):
    initial_started = time.perf_counter()
    reader = SourceReader(project_root)
    raw_atoms, raw_scopes = reader.capture()
    report["source_hashes_before"] = _source_digest(
        project_root, raw_atoms, raw_scopes
    )
    atom_rows, scope_rows, relation_types, _inverse, _cache = materialize(
        raw_atoms, raw_scopes
    )
    extension = os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY")
    store = QueryStore(
        extension_directory=Path(extension) if extension else None,
        database_path=database_directory / "projection.duckdb",
    )
    try:
        _measure_rebuilds(
            store,
            reader,
            atom_rows,
            scope_rows,
            relation_types,
            report,
            initial_started,
        )
    finally:
        store.close()
    report["dataset"] = {
        "atom_count": len(raw_atoms),
        "scope_unit_count": len(raw_scopes),
    }
    report["source_hashes_after"] = _source_digest(
        project_root, raw_atoms, raw_scopes
    )


def _write_profile_artifacts(
    profiler, started, output, database_directory, report
):
    profiler.disable()
    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    report["python_allocations"] = {
        "current_bytes": current_bytes,
        "peak_bytes": peak_bytes,
        "top": _allocation_traces(tracemalloc.take_snapshot()),
    }
    tracemalloc.stop()
    report["total_instrumented_elapsed_seconds"] = round(
        time.perf_counter() - started, 6
    )
    report["code_hashes_after"] = _code_hashes()
    profiler.dump_stats(str(output / "cpu.pstats"))
    try:
        if database_directory.exists():
            shutil.rmtree(database_directory)
        report["disposable_database_cleanup"] = {"succeeded": True}
    except OSError as cleanup_error:
        report["disposable_database_cleanup"] = {
            "succeeded": False,
            "retained_path": str(database_directory),
            "error": str(cleanup_error),
        }
    (output / "report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def profile(project_root: Path, output: Path) -> dict[str, Any]:
    """Profile one initial index plus exactly three isolated full rebuilds."""
    _imports()
    from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
        QueryStore,
        materialize_with_registry,
    )
    from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
        FEATURE_IWE_CONSOLE_BACKEND__shared import SourceReader  # fmt: skip

    report = _make_report(
        project_root, REBUILD_CYCLES, TRACE_FRAMES, sys, metadata, _code_hashes
    )
    database_directory = output / "disposable-database"
    error: BaseException | None = None
    started = time.perf_counter()
    profiler = cProfile.Profile()
    tracemalloc.start(TRACE_FRAMES)
    profiler.enable()
    try:
        _capture_and_measure(
            project_root,
            database_directory,
            report,
            SourceReader,
            QueryStore,
            materialize_with_registry,
        )
    except BaseException as caught:
        error = caught
        report["error"] = {
            "type": type(caught).__name__,
            "message": str(caught),
        }
    finally:
        _write_profile_artifacts(
            profiler, started, output, database_directory, report
        )
    if error is not None:
        raise error
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        required=True,
        type=Path,
        help="ANECHOIC Project whose sources are read",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output under the selected Project temporary root",
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    output = output_directory(project_root, args.output)
    report = profile(project_root, output)
    print(
        json.dumps(
            {
                "output": str(output),
                "dataset": report["dataset"],
                "rebuild_cycles": REBUILD_CYCLES,
            }
        )
    )


if __name__ == "__main__":
    main()
