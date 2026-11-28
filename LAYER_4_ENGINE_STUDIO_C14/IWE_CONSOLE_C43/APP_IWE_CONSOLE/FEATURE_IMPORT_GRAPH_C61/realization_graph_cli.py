"""Build a Realization Graph snapshot from a JSON request on standard input."""

from datetime import datetime, timezone
import json
from functools import cache
from pathlib import Path
import sys

# fmt: off
from ARCHITECTURE_ANALYSIS_C73.CODE_AND_SPEC_METRICS_C76 \
    .metrics__shared import (
    is_measurement_input,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 \
    .structure.structure__shared import (
    build_code_access_ownership,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75 \
    .LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION \
    .access._package__shared import (
    check_code_access,
)
# fmt: on

from .RESOLUTION.analysis_inputs import analysis_inputs
from .RESOLUTION.code_access_occurrences import code_access_occurrences
from .RESOLUTION.graph_inputs import _git_selection_witness
from .realization_graph_options import _difference, _first_difference
from .realization_graph_options import _options as _options
from .realization_graph_options import _structure
from .RESOLUTION.RESOLUTION__shared import resolve_realization
from .SOURCE_CAPTURE.SOURCE_CAPTURE__shared import (
    _iter_files,
    _RESOLUTION_INPUTS,
    _stat_signature,
    capture,
)
from .STATE_ANALYSIS.STATE_ANALYSIS__shared import (
    _SourceVersionChanged,
    _read,
    analyze_state,
)


_CONSISTENCY_CODE = "realization_graph_inputs_changed"


class _ChangedInputs(RuntimeError):
    def __init__(self, details):
        super().__init__(
            "Project source or dependency inputs changed during capture"
        )
        self.details = details


def _require_stable(before, root, sources, include, *, watcher_replay):
    if watcher_replay:
        if _git_selection_witness(root) != before:
            raise _ChangedInputs(
                {
                    "resolution_inputs": {
                        "change": "changed",
                        "fields": ["stat_signature"],
                    }
                }
            )
        return
    after = capture(root, sources, include)
    details = {}
    for name, left, right in (
        ("resolution_inputs", before, _manifests(root)),
        ("sources", sources, after),
    ):
        if left != right:
            details[name] = _first_difference(left, right)
    if details:
        raise _ChangedInputs(details)


def _manifests(root):
    return {
        path.relative_to(root).as_posix(): _stat_signature(path)
        for path in _iter_files(root)
        if path.name in _RESOLUTION_INPUTS
        or is_measurement_input(path.relative_to(root))
    }


def _request_root(request):
    if (
        not isinstance(request, dict)
        or set(request)
        not in (
            {"root", "config"},
            {"root", "config", "structure", "control_root"},
        )
        or not isinstance(request["root"], str)
    ):
        raise ValueError("request must contain root and config")
    root = Path(request["root"])
    if (
        not root.is_absolute()
        or str(root.resolve()) != request["root"]
        or not root.is_dir()
    ):
        raise ValueError("root must be a canonical absolute Project directory")
    return root


def _state_projection(root, sources, occurrences, ownership, derive_rows):
    @cache
    def read_source(path):
        try:
            return _read(root, path, sources[path])
        except _SourceVersionChanged as error:
            raise _ChangedInputs(
                {"sources": _difference(path, "changed", ["signature"])}
            ) from error

    if derive_rows is None:
        return {}, analyze_state(
            root, sources, ownership, read_source=read_source
        )
    extra = derive_rows(root, sources, occurrences, read_source, ownership)
    findings = analyze_state(
        root,
        sources,
        ownership,
        read_source=read_source,
        code_units=extra.get("code_units"),
        calls=extra.get("code_unit_calls", ()),
    )
    return extra, findings


def _measure(root, graph, sources, snapshot, ownership, components, measure):
    nodes, test_edges = graph
    sizes, assets, bindings = analysis_inputs(
        root, nodes, sources, snapshot, ownership
    )
    return {
        "analysis_code": measure(
            nodes, test_edges, components or {".": "C00"}, sizes, assets
        ),
        "analysis_bindings": bindings,
    }


def _ownership(
    root, sources, roots, images, components, snapshot, control, nodes
):
    ownership, sites = None, ()
    if components is not None:
        packages, sites = code_access_occurrences(
            root, sources, roots, python_image_imports=images
        )
        paths = {
            parent.as_posix()
            for path in sources
            for parent in (Path(path).parent, *Path(path).parent.parents)
        }
        paths.update(
            node[3] for node in nodes if node[1] == "package" and node[3]
        )
        paths.update(set(components) | packages)
        ownership = build_code_access_ownership(
            root, root / control, snapshot, paths, allow_unrealized=True
        )
    findings = [
        (
            f"module:{problem.path}",
            problem.path,
            problem.line,
            problem.column,
            problem.written,
            problem.status,
            problem.reason,
        )
        for problem in check_code_access(
            ownership, sources, sites, include_entry_bypasses=True
        )
    ]
    return ownership, findings


def _rows(
    extra,
    nodes,
    occurrences,
    edges,
    test_edges,
    state_findings,
    findings,
    sources,
):
    rows = {
        **extra,
        "nodes": nodes,
        "occurrences": occurrences,
        "edges": edges,
        "test_edges": test_edges,
        "state_effect_findings": state_findings,
        "code_access_findings": findings,
        "read_issues": [
            (path, source.error_message)
            for path, source in sources.items()
            if source.status == "read_error"
            and source.error_message is not None
        ],
    }
    return {
        name: sorted(items, key=lambda row: json.dumps(row, ensure_ascii=True))
        for name, items in rows.items()
    }


def _measure_nodes(
    root,
    nodes,
    test_keys,
    test_edges,
    sources,
    snapshot,
    ownership,
    components,
    measure,
    extra,
):
    nodes = [
        (*node, "Test Package" if node[0] in test_keys else None)
        for node in nodes
    ]
    if measure is not None:
        extra.update(
            _measure(
                root,
                (nodes, test_edges),
                sources,
                snapshot,
                ownership,
                components,
                measure,
            )
        )
    return nodes


def _build(request, derive_rows=None, measure=None, *, watcher_replay=False):
    root = _request_root(request)
    roots, include, images = _options(root, request["config"])
    before = (_git_selection_witness if watcher_replay else _manifests)(root)
    sources = capture(root, None, include)
    components, snapshot, control = _structure(request, root, sources)
    nodes, occurrences, edges, test_edges, test_keys = resolve_realization(
        root,
        sources,
        roots,
        components=components,
        python_image_imports=images,
    )
    ownership, findings = _ownership(
        root, sources, roots, images, components, snapshot, control, nodes
    )
    extra, state_findings = _state_projection(
        root, sources, occurrences, ownership, derive_rows
    )
    nodes = _measure_nodes(
        root,
        nodes,
        test_keys,
        test_edges,
        sources,
        snapshot,
        ownership,
        components,
        measure,
        extra,
    )
    _require_stable(
        before, root, sources, include, watcher_replay=watcher_replay
    )
    return _rows(
        extra,
        nodes,
        occurrences,
        edges,
        test_edges,
        state_findings,
        findings,
        sources,
    )


def main(derive_rows=None, measure=None, *, watcher_replay=False):
    try:
        result = _build(
            json.load(sys.stdin),
            derive_rows,
            measure,
            watcher_replay=watcher_replay,
        )
    except _ChangedInputs as error:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(
                timespec="milliseconds"
            ),
            "severity": "ERROR",
            "code": _CONSISTENCY_CODE,
            "event": _CONSISTENCY_CODE,
            "component": "C61",
            "operation": "verify_realization_graph",
            "outcome": "failed",
            "details": error.details,
        }
        print(
            json.dumps(record, ensure_ascii=True, separators=(",", ":")),
            file=sys.stderr,
            flush=True,
        )
        return 1
    except (ValueError, OSError, RuntimeError) as error:
        print(f"realization graph: {error}", file=sys.stderr)
        return 1
    json.dump(result, sys.stdout, ensure_ascii=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
