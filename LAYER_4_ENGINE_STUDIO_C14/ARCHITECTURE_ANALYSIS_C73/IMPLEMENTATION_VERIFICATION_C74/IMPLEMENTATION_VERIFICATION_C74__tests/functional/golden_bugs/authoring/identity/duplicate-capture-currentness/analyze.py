"""Check currentness calls on the bounded successful full generation path."""

import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile

DETAIL = "Full generation checks currentness in capture and again at finish."


def function(tree, name):
    matches = [
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == name
    ]
    if len(matches) != 1:
        raise ValueError("expected one " + name)
    return matches[0]


def _capture_deferred(nodes):
    calls = [
        n
        for n in ast.walk(nodes[1])
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "capture_native"
    ]
    if len(calls) != 1:
        raise ValueError("expected one generation capture call")
    deferred = any(
        k.arg == "defer_currentness"
        and isinstance(k.value, ast.Constant)
        and k.value.value is True
        for k in calls[0].keywords
    )
    guards = [
        n
        for n in nodes[0].body
        if isinstance(n, ast.If)
        and any(
            isinstance(call, ast.Call)
            and ast.unparse(call.func) == "reader.currentness"
            for call in ast.walk(n.test)
        )
    ]
    if len(guards) != 1:
        raise ValueError("unsupported capture currentness guard")
    test = ast.unparse(guards[0].test)
    old = (
        "reader.currentness()['state'] != 'unchanged'"
        " or any((path.exists() or path.is_symlink() "
        "for path in missing))"
    )
    fixed = (
        "not defer_currentness and reader.currentness"
        "()['state'] != 'unchanged' or any((path.exis"
        "ts() or path.is_symlink() for path in missin"
        "g))"
    )
    if test not in (old, fixed) or (deferred and test != fixed):
        raise ValueError("unsupported capture currentness condition")
    return deferred


def extract(root):
    metadata = json.loads((HERE / "case.json").read_text())
    paths = metadata["before"]["source"]
    nodes = [
        function(ast.parse((root / path).read_text()), name)
        for path, name in zip(
            paths, ("capture_native", "prepare_generation_snapshot")
        )
    ]
    deferred = _capture_deferred(nodes)
    finish = function(nodes[1], "finish")
    finish_guards = [
        n
        for n in finish.body
        if isinstance(n, ast.If)
        and ast.unparse(n.test)
        == "reader.currentness()['state'] != 'unchanged'"
    ]
    all_calls = [
        n
        for n in ast.walk(nodes[1])
        if isinstance(n, ast.Call)
        and ast.unparse(n.func) == "reader.currentness"
    ]
    if len(finish_guards) != 1 or len(all_calls) != 1:
        raise ValueError("unsupported finish currentness guard")
    capture_count = int(not deferred)
    finish_count = len(finish_guards)
    bad = capture_count + finish_count != 1 or finish_count != 1
    program = f"""def captureChecks : Nat := {capture_count}
def finishChecks : Nat := {finish_count}
def violates : Bool := captureChecks + finishChecks != 1 || finishChecks != 1
theorem checked : violates = {str(bad).lower()} := by decide
#eval violates
"""
    return paths[0], bad, program


HERE = Path(__file__).resolve().parent


def verify(program, expected, lean):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "check.lean"
        path.write_text(program)
        run = subprocess.run(
            [lean, str(path)], capture_output=True, text=True, timeout=30
        )
    if run.returncode or run.stdout.strip() != expected:
        raise ValueError(
            "Lean verification failed: " + (run.stdout + run.stderr)[:1000]
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True)
    args = parser.parse_args()
    report = {"findings": [], "unresolved": []}
    try:
        path, bad, program = extract(args.checkout.resolve(strict=True))
        verify(program, str(bad).lower(), args.lean)
        if bad:
            report["findings"].append({"path": path, "detail": DETAIL})
    except (
        OSError,
        SyntaxError,
        UnicodeError,
        ValueError,
        subprocess.TimeoutExpired,
    ) as error:
        report["unresolved"].append(str(error))
    print(json.dumps(report))


if __name__ == "__main__":
    main()
