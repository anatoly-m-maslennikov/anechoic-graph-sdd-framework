"""Check a selected Python workflow region against a proposed call."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tokenize

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import parse_structure  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    realization_ownership__pub import build_code_access_ownership  # fmt: skip

from .source import _event_path, _root_path, _stat_signature
from .state_effects import _policy
from .workflow_reuse_source import (
    UnsupportedReuse,
    find_reuse_region,
    lower_reuse,
)
from .workflow_spec import _tool


def _unit(graph, key):
    rows = [row for row in graph.get("code_units", ()) if row[0] == key]
    if len(rows) != 1:
        raise UnsupportedReuse(f"Code Unit is absent or ambiguous: {key}")
    _, module, kind, name, line, column = rows[0]
    relative = module.removeprefix("module:")
    if (
        kind != "function"
        or module == relative
        or not relative.endswith(".py")
    ):
        raise UnsupportedReuse("Select Python function Code Units")
    if key != f"code_unit:{relative}:{line}:{column}":
        raise UnsupportedReuse("Code Unit source location is inconsistent")
    return relative, (name, line, column)


def _ownership(root, relative, structure, control_root):
    if (
        not isinstance(control_root, str)
        or not control_root
        or "/" in control_root
        or control_root in {".", ".."}
    ):
        raise ValueError("control_root must name a Project control directory")
    control = _event_path(root, control_root)
    if control is None or not control.is_dir():
        raise ValueError("control_root must name a Project control directory")
    snapshot = parse_structure(json.dumps(structure).encode())
    paths = {parent.as_posix() for parent in Path(relative).parents}
    return build_code_access_ownership(
        root, control, snapshot, paths, allow_unrealized=True
    )


def _read_source(root, relative):
    path = _event_path(root, relative)
    if path is None or not path.is_file():
        raise UnsupportedReuse(
            "The Code Unit source is outside the Project or unavailable"
        )
    before = _stat_signature(path)
    raw = path.read_bytes()
    if _stat_signature(path) != before or _event_path(root, relative) != path:
        raise UnsupportedReuse("The Code Unit source changed during the check")
    encoding, _ = tokenize.detect_encoding(BytesIO(raw).readline)
    return raw.decode(encoding), sha256(raw).hexdigest()


def _observations(
    root, graph, structure, caller, callee, first, last, control_root
):
    relative, caller_unit = _unit(graph, caller)
    callee_path, callee_unit = _unit(graph, callee)
    if relative != callee_path:
        raise UnsupportedReuse(
            "The pilot compares functions in the same Python module"
        )
    source, digest = _read_source(root, relative)
    if first is None and last is None:
        first, last = find_reuse_region(source, caller_unit)
    if (
        type(first) is not int
        or type(last) is not int
        or not 1 <= first <= last
    ):
        raise ValueError("Select a positive, ordered source line range")
    if "code_unit_calls" not in graph:
        raise UnsupportedReuse("The graph export lacks call edges")
    if any(
        source == caller and first <= line <= last
        for source, _, line, _ in graph["code_unit_calls"]
    ):
        raise UnsupportedReuse("The selected region contains a resolved call")
    ownership = _ownership(root, relative, structure, control_root)
    policy = _policy(relative, ownership)
    lowered = lower_reuse(source, caller_unit, callee_unit, first, last)
    if policy["kind"] == "pure" and any(
        event["kind"] == "effect"
        for event in (*lowered["left"], *lowered["right"])
    ):
        raise UnsupportedReuse(
            "The owning state policy forbids the modeled writes"
        )
    return _reuse_evidence(
        relative, digest, first, last, policy, callee_unit, lowered
    )


def _reuse_evidence(
    relative, digest, first, last, policy, callee_unit, lowered
):
    evidence = {
        "source": {
            "path": relative,
            "sha256": digest,
            "first": first,
            "last": last,
        },
        "owner": policy["owner"],
        "callee_name": callee_unit[0],
        "arguments": lowered["arguments"],
        "domain": lowered["domain"],
        "assumptions": (
            "At region entry, dictionaries are caller-owned built-in "
            "dicts with exact str keys "
            "and immutable scalar values. Scalars are exact str, int, "
            "finite float, bool, or None. "
            "Module bindings and dictionaries are stable outside the "
            "modeled writes."
        ),
        "result_binding": lowered["result_binding"],
    }
    traces = {
        "inputsAligned": True,
        "left": {"complete": True, "events": lowered["left"]},
        "right": {"complete": True, "events": lowered["right"]},
    }
    return evidence, traces


def check_reuse(
    root,
    graph,
    structure,
    caller,
    callee,
    first=None,
    last=None,
    *,
    control_root,
):
    # fmt: off
    (
        "Return a review finding for two selected Code Units and one "
        "source region."
    )
    # fmt: on
    result = {"caller": caller, "callee": callee}
    root = _root_path(Path(root))
    try:
        evidence, traces = _observations(
            root, graph, structure, caller, callee, first, last, control_root
        )
    except UnsupportedReuse as error:
        return {
            **result,
            "status": "unresolved",
            "reason": str(error),
            "firstDifference": None,
        }
    lean = _tool(
        [
            "lean",
            "--run",
            str(Path(__file__).with_name("FlowComparison.lean")),
        ],
        traces,
    )
    return {**result, **evidence, **lean}


def main():
    try:
        result = check_reuse(**json.load(sys.stdin))
    except (
        OSError,
        TypeError,
        ValueError,
        KeyError,
        SyntaxError,
        subprocess.TimeoutExpired,
    ) as error:
        print(f"workflow reuse: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
