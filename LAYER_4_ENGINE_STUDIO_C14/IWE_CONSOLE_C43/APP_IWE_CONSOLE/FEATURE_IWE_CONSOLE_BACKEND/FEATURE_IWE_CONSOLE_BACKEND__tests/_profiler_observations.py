"""Collect profiler allocation and DuckDB memory observations."""

import tracemalloc
from typing import Any


def _native_memory(connection: Any) -> dict[str, Any]:
    try:
        rows = connection.execute(
            "SELECT tag, memory_usage_bytes FROM duckdb_memory()"
        ).fetchall()
    except Exception as error:
        return {"available": False, "reason": str(error)}
    return {
        "available": True,
        "managed_bytes": sum(int(row[1]) for row in rows),
        "tags": {str(row[0]): int(row[1]) for row in rows if int(row[1])},
    }


def _allocation_traces(snapshot: tracemalloc.Snapshot) -> list[dict[str, Any]]:
    return [
        {
            "size_bytes": statistic.size,
            "count": statistic.count,
            "traceback": [str(frame) for frame in statistic.traceback],
        }
        for statistic in snapshot.statistics("lineno")[:20]
    ]


def _digest_sources(project_root, atom_rows, scope_rows, hashlib):
    paths = {
        str(row[path_key])
        for row in [*atom_rows, *scope_rows]
        for path_key in ("source_path", "declaration_source_path")
        if isinstance(row.get(path_key), str)
    }
    digest = hashlib.sha256()
    for relative in sorted(paths):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(
            hashlib.sha256((project_root / relative).read_bytes()).digest()
        )
    return {"count": len(paths), "digest": digest.hexdigest()}


def _make_report(
    project_root, REBUILD_CYCLES, TRACE_FRAMES, sys, metadata, _code_hashes
):
    return {
        "instrumented": True,
        "not_performance_acceptance_timing": True,
        "rebuild_cycles": REBUILD_CYCLES,
        "trace_frames": TRACE_FRAMES,
        "source_root": str(project_root),
        "runtime": {
            "python_version": sys.version,
            "platform": sys.platform,
            "duckdb_package_version": metadata.version("duckdb"),
        },
        "code_hashes_before": _code_hashes(),
        "measurements": [],
    }
