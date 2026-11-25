"""Build a Realization Graph snapshot from a JSON request on standard input."""

from dataclasses import fields
from datetime import datetime, timezone
import json
import keyword
from functools import cache
from pathlib import Path
import re
import sys

from ARCHITECTURE_ANALYSIS_C73.CODE_AND_SPEC_METRICS_C76.metrics__shared import is_measurement_input
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_structure, realization_component_paths,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.realization_ownership__pub import build_code_access_ownership
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import check_code_access

from .analysis_inputs import analysis_inputs
from .code_access_occurrences import code_access_occurrences
from .graph_inputs import _git_selection_witness
from .resolution import resolve_realization
from .source import _iter_files, _RESOLUTION_INPUTS, _stat_signature, capture
from .state_effects import _SourceVersionChanged, _read, analyze_state


_CONSISTENCY_CODE = "realization_graph_inputs_changed"
_SAFE_PATH = re.compile(r"[A-Za-z0-9_./-]{1,256}")
_PRIVATE_PATH = re.compile(r"\.env\b|\.ssh\b|password|passwd|secret|token|api[_-]?key|authorization|bearer", re.I)


class _ChangedInputs(RuntimeError):
    def __init__(self, details):
        super().__init__("Project source or dependency inputs changed during capture")
        self.details = details


def _first_difference(before, after):
    for path, old in before.items():
        if path not in after:
            return _difference(path, "removed")
        new = after[path]
        if old != new:
            changed = (["stat_signature"] if isinstance(old, str) else
                       [field.name for field in fields(old) if getattr(old, field.name) != getattr(new, field.name)])
            return _difference(path, "changed", changed)
    return _difference(next(path for path in after if path not in before), "added")


def _difference(path, change, changed=()):
    report = {"change": change}
    if (_SAFE_PATH.fullmatch(path) and not path.startswith("/") and ".." not in path.split("/")
            and not _PRIVATE_PATH.search(path)):
        report["path"] = path
    if changed:
        report["fields"] = changed
    return report


def _require_stable(before, root, sources, include, *, watcher_replay):
    if watcher_replay:
        if _git_selection_witness(root) != before:
            raise _ChangedInputs({"resolution_inputs": {"change": "changed", "fields": ["stat_signature"]}})
        return
    after = capture(root, sources, include)
    details = {}
    for name, left, right in (("resolution_inputs", before, _manifests(root)), ("sources", sources, after)):
        if left != right:
            details[name] = _first_difference(left, right)
    if details:
        raise _ChangedInputs(details)


def _options(root, config):
    if not isinstance(config, dict) or set(config) - {"include", "python_roots", "python_image_imports"}:
        raise ValueError("import_graph must contain only supported options")
    result = []
    for name, default in (("python_roots", None), ("include", [])):
        values = config.get(name, default)
        if name == "python_roots" and name not in config:
            result.append(None)
            continue
        if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
            raise ValueError(f"import_graph.{name} must be a list of Project-relative paths")
        for value in values:
            path = Path(value)
            if path.is_absolute() or ".." in path.parts or not (root / path).resolve().is_relative_to(root):
                raise ValueError(f"import_graph.{name} paths must be inside the Project")
            if name == "include" and (path == Path(".") or (root / path).is_dir()):
                raise ValueError("import_graph.include paths must name source files")
        result.append(tuple(values))
    images = config.get("python_image_imports", {})
    if not isinstance(images, dict):
        raise ValueError("import_graph.python_image_imports must be a mapping")
    for value, modules in images.items():
        if not isinstance(value, str) or not value:
            raise ValueError("import_graph.python_image_imports keys must name Python source files")
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or not (root / path).resolve().is_relative_to(root):
            raise ValueError("import_graph.python_image_imports paths must be inside the Project")
        if path.as_posix() != value or path.suffix != ".py" or (root / path).is_dir():
            raise ValueError("import_graph.python_image_imports keys must name Python source files")
        if not isinstance(modules, list) or any(
            not isinstance(module, str) or not module
            or any(not part.isidentifier() or keyword.iskeyword(part) for part in module.split("."))
            for module in modules
        ):
            raise ValueError("import_graph.python_image_imports values must be lists of dotted Python module names")
    return result[0], result[1], {path: tuple(modules) for path, modules in images.items()}


def _manifests(root):
    return {path.relative_to(root).as_posix(): _stat_signature(path)
            for path in _iter_files(root) if path.name in _RESOLUTION_INPUTS
            or is_measurement_input(path.relative_to(root))}


def _request_root(request):
    if (not isinstance(request, dict) or set(request) not in ({"root", "config"},
            {"root", "config", "structure", "control_root"}) or not isinstance(request["root"], str)):
        raise ValueError("request must contain root and config")
    root = Path(request["root"])
    if not root.is_absolute() or str(root.resolve()) != request["root"] or not root.is_dir():
        raise ValueError("root must be a canonical absolute Project directory")
    return root


def _state_projection(root, sources, occurrences, ownership, derive_rows):
    @cache
    def read_source(path):
        try:
            return _read(root, path, sources[path])
        except _SourceVersionChanged as error:
            raise _ChangedInputs({"sources": _difference(path, "changed", ["signature"])}) from error

    if derive_rows is None:
        return {}, analyze_state(root, sources, ownership, read_source=read_source)
    extra = derive_rows(root, sources, occurrences, read_source, ownership)
    findings = analyze_state(root, sources, ownership, read_source=read_source,
                             code_units=extra.get('code_units'), calls=extra.get('code_unit_calls', ()))
    return extra, findings


def _measure(root, graph, sources, snapshot, ownership, components, measure):
    nodes, test_edges = graph
    sizes, assets, bindings = analysis_inputs(root, nodes, sources, snapshot, ownership)
    return {"analysis_code": measure(nodes, test_edges, components or {".": "C00"}, sizes, assets),
            "analysis_bindings": bindings}


def _build(request, derive_rows=None, measure=None, *, watcher_replay=False):
    root = _request_root(request)
    roots, include, images = _options(root, request["config"])
    before = _git_selection_witness(root) if watcher_replay else _manifests(root)
    sources = capture(root, None, include)
    components, snapshot = None, None
    if "structure" in request:
        control = request["control_root"]
        if (not isinstance(control, str) or not control or Path(control).is_absolute()
                or len(Path(control).parts) != 1 or control in {".", ".."}
                or (root / control).is_symlink() or not (root / control).is_dir()):
            raise ValueError("control_root must name a Project control directory")
        snapshot = parse_structure(json.dumps(request["structure"]).encode())
        folders = {Path(path).parent for path in sources}
        components = realization_component_paths(root, root / control, snapshot, folders)
    nodes, occurrences, edges, test_edges, test_keys = resolve_realization(
        root, sources, roots, components=components, python_image_imports=images,
    )
    ownership, sites = None, ()
    if components is not None:
        packages, sites = code_access_occurrences(root, sources, roots, python_image_imports=images)
        paths = {parent.as_posix() for path in sources for parent in (Path(path).parent, *Path(path).parent.parents)}
        paths.update(node[3] for node in nodes if node[1] == "package" and node[3])
        paths.update(set(components) | packages)
        ownership = build_code_access_ownership(root, root / control, snapshot, paths, allow_unrealized=True)
    findings = [(f"module:{problem.path}", problem.path, problem.line, problem.column,
                 problem.written, problem.status, problem.reason)
                for problem in check_code_access(ownership, sources, sites, include_entry_bypasses=True)]
    extra, state_findings = _state_projection(root, sources, occurrences, ownership, derive_rows)
    nodes = [(*node, "Test Package" if node[0] in test_keys else None) for node in nodes]
    if measure is not None:
        extra.update(_measure(root, (nodes, test_edges), sources, snapshot, ownership, components, measure))
    _require_stable(before, root, sources, include, watcher_replay=watcher_replay)
    rows = {
        **extra,
        "nodes": nodes,
        "occurrences": occurrences, "edges": edges, "test_edges": test_edges,
        "state_effect_findings": state_findings, "code_access_findings": findings,
        "read_issues": [(path, source.error_message) for path, source in sources.items()
                        if source.status == "read_error" and source.error_message is not None],
    }
    return {name: sorted(items, key=lambda row: json.dumps(row, ensure_ascii=True)) for name, items in rows.items()}


def main(derive_rows=None, measure=None, *, watcher_replay=False):
    try:
        result = _build(json.load(sys.stdin), derive_rows, measure, watcher_replay=watcher_replay)
    except _ChangedInputs as error:
        record = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "severity": "ERROR",
                  "code": _CONSISTENCY_CODE, "event": _CONSISTENCY_CODE, "component": "C61",
                  "operation": "verify_realization_graph", "outcome": "failed", "details": error.details}
        print(json.dumps(record, ensure_ascii=True, separators=(",", ":")), file=sys.stderr, flush=True)
        return 1
    except (ValueError, OSError, RuntimeError) as error:
        print(f"realization graph: {error}", file=sys.stderr)
        return 1
    json.dump(result, sys.stdout, ensure_ascii=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
