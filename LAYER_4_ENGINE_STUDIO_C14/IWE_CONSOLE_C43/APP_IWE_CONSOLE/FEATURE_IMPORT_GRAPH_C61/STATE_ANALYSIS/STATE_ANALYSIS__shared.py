"""Check ordered source effects with Lean and project the evidence as rows."""

from collections import defaultdict
from collections.abc import Mapping
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tokenize

from .python_state_cases import python_state_cases
from ..SOURCE_CAPTURE.SOURCE_CAPTURE__shared import _stat_signature
from .state_results import _finding, _lean_case, _unresolved
from ..STATE_ANALYSIS.WEB_STATE.WEB_STATE__shared import web_state_cases


_CHECKER = Path(__file__).with_name("ActionEffects.lean")
_LANGUAGES = frozenset(("python", "javascript", "typescript"))


class _SourceVersionChanged(ValueError):
    pass


def _diagnostic(message):
    print(f"state analysis: {message}", file=sys.stderr)


def _declared_state(owner, ownership):
    while owner is not None:
        boundaries = owner["fields"].get("boundaries") or {}
        if "state" in boundaries or owner["kind"] == "component":
            return boundaries.get("state")
        owner = ownership.entries.get(owner["parent"])
    return None


def _policy(path, ownership):
    owner = ownership.owner(path) if ownership is not None else None
    owner_name = (
        owner["id"]
        if owner is not None
        else PurePosixPath(path).parent.as_posix()
    )
    value = _declared_state(owner, ownership)
    mode, channels = "local", {}
    if isinstance(value, str):
        mode = value
    elif isinstance(value, Mapping) and not set(value) - {
        "mode",
        "channels",
        "reads",
        "writes",
    }:
        mode, channels = value.get("mode", "local"), value.get("channels", {})
    elif value is not None:
        raise ValueError("invalid boundaries.state declaration")
    if (
        mode not in ("local", "pure")
        or not isinstance(channels, Mapping)
        or any(
            not isinstance(name, str)
            or not name
            or access not in ("r", "w", "rw")
            for name, access in channels.items()
        )
        or (mode == "pure" and channels)
    ):
        raise ValueError("invalid boundaries.state mode or channel grant")
    return {
        "kind": mode,
        "owner": owner_name,
        "grants": [
            {"channel": name, "mode": access}
            for name, access in channels.items()
        ],
    }


def _read(root, path, source):
    file = root / path
    try:
        if not file.is_relative_to(root) or file.resolve(strict=True) != file:
            raise ValueError("source path changed or left the Project")
        if _stat_signature(file) != source.signature:
            raise _SourceVersionChanged("source changed after graph capture")
        if source.language == "python":
            with tokenize.open(file) as handle:
                content = handle.read()
        else:
            content = file.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise _SourceVersionChanged(
            "source removed after graph capture"
        ) from error
    if _stat_signature(file) != source.signature:
        raise _SourceVersionChanged("source changed during state analysis")
    return content


def _no_ops(cases, text, marker):
    lines = text.splitlines()
    for case in cases:
        line = case["line"] - 2
        if (
            case["action"] != "<module>"
            and 0 <= line < len(lines)
            and lines[line].strip() == marker
        ):
            case["declaredNoOp"] = True
    return cases


def _call_sites(code_units, calls):
    if code_units is None:
        return None
    paths = {
        key: module.removeprefix("module:") for key, module, *_ in code_units
    }
    matches = defaultdict(lambda: defaultdict(set))
    for caller, callee, line, column in calls:
        matches[paths[caller]][line, column].add(callee)
    return {
        path: {
            site: next(iter(targets))
            for site, targets in sites.items()
            if len(targets) == 1
        }
        for path, sites in matches.items()
    }


def _web_cases(web, sites):
    if sites is None:
        return web_state_cases(web)
    links = {
        path: [
            [line, column, unit]
            for (line, column), unit in sites.get(path, {}).items()
        ]
        for path in web
    }
    return web_state_cases(web, links)


def _inputs(sources, ownership, read_source, sites):
    problems, policies, python, web = {}, {}, {}, {}
    for path, source in sources.items():
        try:
            if source.status in ("read_error", "parse_error"):
                raise ValueError(
                    source.error_message or source.status.replace("_", " ")
                )
            text = read_source(path)
            policies[path] = _policy(path, ownership)
            if source.language == "python":
                calls = None if sites is None else sites.get(path, {})
                python[path] = _no_ops(
                    python_state_cases(text, calls), text, "# anechoic: no-op"
                )
            else:
                web[path] = text
        except (
            OSError,
            LookupError,
            UnicodeError,
            SyntaxError,
            ValueError,
        ) as error:
            problems[path] = str(error)
            _diagnostic(f"{path}: {error}")
    if web:
        try:
            python.update(
                {
                    path: _no_ops(cases, web[path], "// anechoic: no-op")
                    for path, cases in _web_cases(web, sites).items()
                }
            )
        except (OSError, RuntimeError, ValueError) as error:
            _diagnostic(str(error))
            problems.update(dict.fromkeys(web, str(error)))
    return python, policies, problems


def _check(lean, cases):
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in {"LEAN_PATH", "LEAN_SRC_PATH"}
    }
    timeout = None if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0" else 60
    result = subprocess.run(
        [lean, "--run", str(_CHECKER)],
        input=json.dumps(cases, allow_nan=False),
        text=True,
        capture_output=True,
        check=True,
        timeout=timeout,
        cwd=_CHECKER.parent,
        env=environment,
    )
    output = json.loads(result.stdout)
    if not isinstance(output, list) or len(output) != len(cases):
        raise ValueError("Lean returned the wrong number of state results")
    for case, row in zip(cases, output, strict=True):
        if not isinstance(row, dict) or any(
            row.get(key) != case[key]
            for key in ("sourcePath", "line", "input")
        ):
            raise ValueError("Lean result does not match its source case")
    return output


def _actions(paths, policies, code_units):
    units = {
        (module.removeprefix("module:"), line, column): key
        for key, module, kind, _, line, column in code_units or ()
        if kind != "class"
    }
    actions = [
        (case["action"], _lean_case(path, case, policies[path], units))
        for path, items in paths.items()
        for case in items
    ]
    return actions


def _findings(problems, selected, actions, verified, code_units):
    return [
        *(
            _unresolved(path, selected[path], detail)
            for path, detail in problems.items()
        ),
        *(
            finding
            for (action, case), result in zip(actions, verified, strict=True)
            if (
                finding := _finding(
                    selected[case["sourcePath"]],
                    action,
                    case,
                    result,
                    graph_mode=code_units is not None,
                )
            )
            is not None
        ),
    ]


def _find_lean(selected, require_lean):
    if not selected:
        return None
    lean = shutil.which(os.getenv("LEAN_BIN") or "lean")
    if lean is None:
        detail = "Lean executable unavailable on PATH"
        if require_lean:
            raise RuntimeError(detail)
        _diagnostic(detail)
        return None
    return lean


def _check_actions(lean, actions):
    return _check(lean, [case for _, case in actions]) if actions else []


def analyze_state(
    root,
    sources,
    ownership=None,
    *,
    read_source=None,
    code_units=None,
    calls=(),
    require_lean=False,
):
    """Return state evidence for captured Module nodes."""
    selected = {
        path: source
        for path, source in sources.items()
        if source.language in _LANGUAGES
    }
    lean = _find_lean(selected, require_lean)
    if lean is None:
        detail = "Lean executable unavailable on PATH"
        return [
            _unresolved(path, source, detail)
            for path, source in selected.items()
        ]
    if read_source is None:
        root = Path(root).resolve()

        def read_source(path):
            return _read(root, path, selected[path])

    paths, policies, problems = _inputs(
        selected, ownership, read_source, _call_sites(code_units, calls)
    )
    if require_lean and problems:
        raise RuntimeError("State inputs could not be analyzed; see stderr")
    actions = _actions(paths, policies, code_units)
    try:
        verified = _check_actions(lean, actions)
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        detail = getattr(error, "stderr", None) or str(error)
        if require_lean:
            raise RuntimeError(f"Lean check failed: {detail}") from error
        _diagnostic(f"Lean check failed: {detail}")
        return [
            _unresolved(path, source, "Lean check failed")
            for path, source in selected.items()
        ]
    return _findings(problems, selected, actions, verified, code_units)
