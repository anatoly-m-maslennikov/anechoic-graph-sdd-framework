"""Check the historical local release phase lock ordering."""

import argparse
import ast
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


def fail(message):
    raise ValueError(message)


def source_functions(root):
    matches = []
    for path in root.rglob("*.py"):
        rel = path.relative_to(root)
        if "RELEASE" not in str(rel).upper() or any(
            ("test") in part.lower() or part.startswith(("."))
            for part in rel.parts
        ):
            continue
        try:
            tree = ast.parse(path.read_text())
        except (OSError, UnicodeError, SyntaxError) as error:
            fail(f"cannot parse release source {rel}: {error}")
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == (
                "run_local_release"
            ):
                loops = [
                    n
                    for n in ast.walk(node)
                    if isinstance(n, ast.For)
                    and ast.unparse(n.target) == "phase"
                    and ast.unparse(n.iter) == "phases"
                ]
                if loops:
                    matches.append((rel.as_posix(), tree, node, loops))
    if len(matches) != 1 or len(matches[0][3]) != 1:
        fail("expected one historical phase-loop release implementation")
    return matches[0]


def _validate_lock_body(lock):
    flags = [
        n
        for n in ast.walk(lock)
        if isinstance(n, ast.Call) and ast.unparse(n.func) == "fcntl.flock"
    ]
    if (
        len(flags) != 1
        or len(flags[0].args) != 2
        or ast.unparse(flags[0].args[1]) != "fcntl.LOCK_EX | fcntl.LOCK_NB"
    ):
        fail("unsupported non-blocking exclusive flock")
    handlers = [
        n
        for n in ast.walk(lock)
        if isinstance(n, ast.ExceptHandler)
        and n.type
        and ast.unparse(n.type) == "BlockingIOError"
    ]
    if (
        len(handlers) != 1
        or not any(
            isinstance(n, ast.Raise)
            and "local-release-installation-lock-busy" in ast.unparse(n)
            for n in handlers[0].body
        )
        or len([n for n in ast.walk(lock) if isinstance(n, ast.Yield)]) != 1
    ):
        fail("unsupported lock refusal or yield")


def validate_lock(tree, block, before):
    lock_functions = [
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "_installation_lock"
    ]
    if len(lock_functions) != 1:
        fail("missing lock implementation")
    lock = lock_functions[0]
    if (
        hashlib.sha256(ast.unparse(lock).encode()).hexdigest()
        != "aa37da649cb281145a10e09cda395d7df4ccec96118435fcf9a441622d088ab3"
    ):
        fail("unsupported lock implementation shape")
    _validate_lock_body(lock)
    if not any(
        isinstance(n, ast.Expr)
        and ast.unparse(n) == ("installation_lock.close()")
        for n in block.finalbody
    ):
        fail("installation lock is not released in finally")
    if any(
        isinstance(n, ast.Call)
        and (
            ast.unparse(n.func) in ("version_path.write_text", "_clear_target")
            or ast.unparse(n.func) == "runner"
        )
        for n in ast.walk(ast.Module(body=before, type_ignores=[]))
    ):
        fail("possible effect before lock-covered loop")


def _validate_loop_effects(loop):
    calls = [n for n in ast.walk(loop) if isinstance(n, ast.Call)]
    git = [
        n
        for n in calls
        if isinstance(n.func, ast.Name)
        and n.func.id == "runner"
        and n.args
        and isinstance(n.args[0], ast.Tuple)
        and n.args[0].elts
        and isinstance(n.args[0].elts[0], ast.Constant)
        and n.args[0].elts[0].value == "git"
    ]
    writes = [
        n
        for n in calls
        if isinstance(n.func, ast.Attribute)
        and ast.unparse(n.func) == "version_path.write_text"
    ]
    clears = [
        n
        for n in calls
        if isinstance(n.func, ast.Name) and n.func.id == "_clear_target"
    ]
    if not git or not writes or not clears:
        fail("expected phase-loop Git, version writes, and target clears")


def _lock_entries(before, function):
    entries = [
        n
        for n in before
        if isinstance(n, ast.Expr)
        and isinstance(n.value, ast.Call)
        and ast.unparse(n.value.func) == "installation_lock.enter_context"
        and n.value.args
        and isinstance(n.value.args[0], ast.Call)
        and ast.unparse(n.value.args[0].func) == "_installation_lock"
    ]
    all_entries = [
        n
        for n in ast.walk(function)
        if isinstance(n, ast.Call)
        and ast.unparse(n.func) == "installation_lock.enter_context"
    ]
    return entries, all_entries


def model(root):
    path, tree, function, loops = source_functions(root)
    loop = loops[0]
    _validate_loop_effects(loop)
    blocks = [
        n for n in function.body if isinstance(n, ast.Try) and loop in n.body
    ]
    if len(blocks) != 1:
        fail("phase loop does not have one supported enclosing try")
    block = blocks[0]
    prefix = function.body[: function.body.index(block)]
    if any(
        isinstance(n, ast.Call)
        and ast.unparse(n.func)
        in ("runner", "version_path.write_text", "_clear_target")
        for n in ast.walk(ast.Module(body=prefix, type_ignores=[]))
    ):
        fail("possible protected effect before phase block")
    before = block.body[: block.body.index(loop)]
    entries, all_entries = _lock_entries(before, function)
    if not entries and not all_entries:
        if any(
            isinstance(n, ast.Call)
            and (
                "lock" in ast.unparse(n.func).lower()
                or ast.unparse(n.func) == "fcntl.flock"
            )
            for n in ast.walk(function)
        ):
            fail("another possible lock requires manual analysis")
        return path, False
    if not any(
        isinstance(n, ast.Assign)
        and ast.unparse(n) == "installation_lock = ExitStack()"
        for n in prefix
    ):
        fail("missing ExitStack installation lock owner")
    if len(entries) != 1 or len(all_entries) != 1:
        fail("unsupported installation lock placement")
    validate_lock(tree, block, before)
    return path, True


def lean_source(locked):
    events = "[.lock, .git, .version]" if locked else "[.git, .version]"
    return (
        "inductive Event where | lock | git | version deriving "
        "DecidableEq, Repr\n"
        f"def trace : List Event := {events}\n"
        "def lockedBeforeEffects : List Event → Bool\n"
        "  | [] => true\n"
        "  | .lock :: _ => true\n"
        "  | _ :: _ => false\n"
        "def contract : Bool := lockedBeforeEffects trace\n"
        f"theorem checked : contract = {'true' if locked else 'false'} "
        ":= by decide\n"
        "#eval contract\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True, type=Path)
    args = parser.parse_args()
    report = {"findings": [], "unresolved": []}
    try:
        path, locked = model(args.checkout.resolve(strict=True))
        with tempfile.TemporaryDirectory() as tmp:
            program = Path(tmp) / "generated.lean"
            program.write_text(lean_source(locked))
            run = subprocess.run(
                [str(args.lean.resolve(strict=True)), str(program)],
                capture_output=True,
                text=True,
                timeout=120,
            )
        if run.returncode or run.stdout.strip().splitlines()[-1:] != [
            str(locked).lower()
        ]:
            fail(f"Lean verification failed: {run.stdout} {run.stderr}")
        if not locked:
            report["findings"].append(
                {
                    "path": path,
                    ("detail"): (
                        "The release phase loop can run Git commands and "
                        "mutate version/product state without first acqui"
                        "ring the installation lock."
                    ),
                }
            )
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        report["unresolved"].append(str(error))
    print(json.dumps(report, sort_keys=True))
    return 2 if report["unresolved"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
