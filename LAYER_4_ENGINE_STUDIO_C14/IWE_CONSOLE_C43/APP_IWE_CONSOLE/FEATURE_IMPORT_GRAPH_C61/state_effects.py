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
from .source import _stat_signature
from .web_state_cases import web_state_cases


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
    owner_name = owner["id"] if owner is not None else PurePosixPath(path).parent.as_posix()
    value = _declared_state(owner, ownership)
    mode, channels = "local", {}
    if isinstance(value, str):
        mode = value
    elif isinstance(value, Mapping) and not set(value) - {"mode", "channels", "reads", "writes"}:
        mode, channels = value.get("mode", "local"), value.get("channels", {})
    elif value is not None:
        raise ValueError("invalid boundaries.state declaration")
    if (mode not in ("local", "pure") or not isinstance(channels, Mapping)
            or any(not isinstance(name, str) or not name or access not in ("r", "w", "rw")
                   for name, access in channels.items()) or (mode == "pure" and channels)):
        raise ValueError("invalid boundaries.state mode or channel grant")
    return {"kind": mode, "owner": owner_name,
            "grants": [{"channel": name, "mode": access} for name, access in channels.items()]}


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
        raise _SourceVersionChanged("source removed after graph capture") from error
    if _stat_signature(file) != source.signature:
        raise _SourceVersionChanged("source changed during state analysis")
    return content


def _no_ops(cases, text, marker):
    lines = text.splitlines()
    for case in cases:
        line = case["line"] - 2
        if case["action"] != "<module>" and 0 <= line < len(lines) and lines[line].strip() == marker:
            case["declaredNoOp"] = True
    return cases


def _call_sites(code_units, calls):
    if code_units is None:
        return None
    paths = {key: module.removeprefix('module:') for key, module, *_ in code_units}
    matches = defaultdict(lambda: defaultdict(set))
    for caller, callee, line, column in calls:
        matches[paths[caller]][line, column].add(callee)
    return {path: {site: next(iter(targets)) for site, targets in sites.items() if len(targets) == 1}
            for path, sites in matches.items()}


def _web_cases(web, sites):
    if sites is None:
        return web_state_cases(web)
    links = {path: [[line, column, unit] for (line, column), unit in sites.get(path, {}).items()]
             for path in web}
    return web_state_cases(web, links)


def _inputs(sources, ownership, read_source, sites):
    problems, policies, python, web = {}, {}, {}, {}
    for path, source in sources.items():
        try:
            if source.status in ("read_error", "parse_error"):
                raise ValueError(source.error_message or source.status.replace("_", " "))
            text = read_source(path)
            policies[path] = _policy(path, ownership)
            if source.language == "python":
                calls = None if sites is None else sites.get(path, {})
                python[path] = _no_ops(python_state_cases(text, calls), text, "# anechoic: no-op")
            else:
                web[path] = text
        except (OSError, LookupError, UnicodeError, SyntaxError, ValueError) as error:
            problems[path] = str(error)
            _diagnostic(f"{path}: {error}")
    if web:
        try:
            python.update({path: _no_ops(cases, web[path], "// anechoic: no-op")
                           for path, cases in _web_cases(web, sites).items()})
        except (OSError, RuntimeError, ValueError) as error:
            _diagnostic(str(error))
            problems.update(dict.fromkeys(web, str(error)))
    return python, policies, problems


def _lean_case(path, case, policy, units):
    result = {
        "sourcePath": path, "line": case["line"], "input": case["input"],
        "reachable": case["reachable"], "declaredNoOp": case["declaredNoOp"],
        "complete": case["complete"] and isinstance(case["input"], dict),
        "events": [{**event, "name": policy["owner"] if event["name"] == "$owner" else event["name"]}
                   for event in case["events"]],
        "policy": policy,
    }
    if case.get('inlineable'):
        unit = units.get((path, case['line'], case['column']))
        if unit is not None:
            result['unit'] = unit
    return result


def _check(lean, cases):
    environment = {key: value for key, value in os.environ.items() if key not in {"LEAN_PATH", "LEAN_SRC_PATH"}}
    timeout = None if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0" else 60
    result = subprocess.run(
        [lean, "--run", str(_CHECKER)], input=json.dumps(cases, allow_nan=False), text=True,
        capture_output=True, check=True, timeout=timeout, cwd=_CHECKER.parent, env=environment,
    )
    output = json.loads(result.stdout)
    if not isinstance(output, list) or len(output) != len(cases):
        raise ValueError("Lean returned the wrong number of state results")
    for case, row in zip(cases, output, strict=True):
        if not isinstance(row, dict) or any(row.get(key) != case[key] for key in ("sourcePath", "line", "input")):
            raise ValueError("Lean result does not match its source case")
    return output


def _unresolved(path, source, detail):
    return (f"module:{path}", path, source.language, "<module>", 1, None,
            "unresolved", False, "[]", "[]", detail)


def _finding(source, action, case, result, *, graph_mode):
    path = case["sourcePath"]
    status = result["status"]
    detail = "Control flow, effects, or input are not fully modeled" if status == "unresolved" else None
    witness = None if case["input"] is None else json.dumps(case["input"])
    violations = result["violations"] if case["reachable"] and case["complete"] else []
    events = result["events"] if graph_mode else case["events"]
    for event in (*events, *violations):
        if event.get('sourcePath') is None:
            event.pop('sourcePath', None)
    if action == "<module>" and status == "deadEnd":
        return None
    return (f"module:{path}", path, source.language, action, case["line"], witness, status,
            status == "deadEnd", json.dumps(events), json.dumps(violations), detail)


def analyze_state(root, sources, ownership=None, *, read_source=None, code_units=None, calls=()):
    """Return checkable state evidence for the existing captured Module nodes."""
    selected = {path: source for path, source in sources.items() if source.language in _LANGUAGES}
    if not selected:
        return []
    lean = shutil.which("lean")
    if lean is None:
        detail = "Lean executable unavailable on PATH"
        _diagnostic(detail)
        return [_unresolved(path, source, detail) for path, source in selected.items()]
    if read_source is None:
        root = Path(root).resolve()
        read_source = lambda path: _read(root, path, selected[path])
    paths, policies, problems = _inputs(selected, ownership, read_source, _call_sites(code_units, calls))
    units = {(module.removeprefix('module:'), line, column): key
             for key, module, kind, _, line, column in code_units or () if kind != 'class'}
    actions, cases = [], []
    for path, items in paths.items():
        for case in items:
            actions.append(case["action"])
            cases.append(_lean_case(path, case, policies[path], units))
    try:
        verified = _check(lean, cases) if cases else []
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        detail = getattr(error, "stderr", None) or str(error)
        _diagnostic(f"Lean check failed: {detail}")
        return [_unresolved(path, source, "Lean check failed") for path, source in selected.items()]
    return [
        *(_unresolved(path, selected[path], detail) for path, detail in problems.items()),
        *(finding for action, case, result in zip(actions, cases, verified, strict=True)
          if (finding := _finding(selected[case["sourcePath"]], action, case, result,
                                  graph_mode=code_units is not None)) is not None),
    ]
