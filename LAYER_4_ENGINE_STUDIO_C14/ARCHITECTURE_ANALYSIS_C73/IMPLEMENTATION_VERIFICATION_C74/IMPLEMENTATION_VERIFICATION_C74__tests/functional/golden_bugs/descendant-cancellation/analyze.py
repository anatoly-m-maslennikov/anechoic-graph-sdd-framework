#!/usr/bin/env -S python3 -B
"""Project one unfinished-child cancellation path;
unsupported shapes remain unresolved."""

import argparse
import ast
import json
import pathlib
import subprocess
import tempfile

p = argparse.ArgumentParser()
p.add_argument("checkout", type=pathlib.Path)
p.add_argument("--lean", required=True)
a = p.parse_args()
source = a.checkout / (
    "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM"
    "_LIFECYCLE/native_update.py"
)
result = {"findings": [], "unresolved": []}


def fn(tree, name):
    return next(
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name
    )


def match(node, text):
    return any(ast.unparse(x) == text for x in ast.walk(node))


def assignment(node, name):
    xs = [
        x
        for x in ast.walk(node)
        if isinstance(x, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == name for t in x.targets)
    ]
    assert len(xs) == 1
    return ast.unparse(xs[0].value)


try:
    tree = ast.parse(source.read_text())
    read = fn(tree, "_read_ticket")
    change = fn(tree, "change_ticket_status")
    if any(
        isinstance(k, ast.arg) and k.arg == "close_epic" for k in read.args.kwonlyargs
    ):
        assert assignment(change, "close_epic") == (
            "status == 'done' and native_header_view(selected['header_json'])."
            "get('context', {}).get('template') == 'epic'"
        )
        assert any(
            isinstance(x, ast.If)
            and ast.unparse(x.test) == "pending and (not close_epic)"
            and len(x.body) == 1
            and isinstance(x.body[0], ast.Raise)
            and isinstance(x.body[0].exc, ast.Call)
            and isinstance(x.body[0].exc.func, ast.Name)
            and x.body[0].exc.func.id == "InputError"
            for x in ast.walk(read)
        )
        assert match(
            change,
            (
                "_read_ticket(selection, target, selected, digest, path, close_epi"
                "c=close_epic, placement=True)"
            ),
        )
        assert match(
            change,
            (
                "_move_ticket(selection, target, selected, digest, path, destinati"
                "on, status, check_definition, close_epic=close_epic)"
            ),
        )
        code = (
            "def closesTree (done epic : Bool) : Bool := done && epic\ndef reje"
            "cts (pending closeTree companion : Bool) : Bool := pending && !cl"
            "oseTree\ndef selectChild (terminal childTerminal : Bool) : Bool :="
            " false\ndef actionCanceled (parentCanceled isParent : Bool) : Bool"
            " := false"
        )
    else:
        assert assignment(change, "move_tree") == "template in ('task', 'epic')"
        assert (
            assignment(change, "terminal")
            == "move_tree and status in ('done', 'canceled')"
        )
        assert (
            assignment(change, "planned")
            == "_descendants(current_rows, selected['id']) if move_tree else []"
        )
        assert assignment(change, "actions") == (
            "[row for row in planned if terminal and row['status'] not in ('do"
            "ne', 'canceled')]"
        )
        assert (
            assignment(change, "action_status") == "status if is_parent else 'canceled'"
        )
        assert any(
            isinstance(x, ast.If)
            and ast.unparse(x.test)
            == "pending and (not close_tree or not companion.is_dir())"
            and len(x.body) == 1
            and isinstance(x.body[0], ast.Raise)
            and isinstance(x.body[0].exc, ast.Call)
            and isinstance(x.body[0].exc.func, ast.Name)
            and x.body[0].exc.func.id == "InputError"
            for x in ast.walk(read)
        )
        assert match(
            change,
            (
                "_read_ticket(selection, target, selected, digest, path, close_tre"
                "e=move_tree, placement=True)"
            ),
        )
        assert match(change, "actions.append(selected)")
        descendants = fn(tree, "_descendants")
        assert (
            match(descendants, "ordered.append(row)")
            and match(descendants, "stack.append((row, True))")
            and match(
                descendants,
                (
                    "stack.extend(((child, False) for child in reversed(sorted(childre"
                    "n.get(row['id'], ()), key=lambda r: r['id']))))"
                ),
            )
        )
        assert any(
            isinstance(x, ast.For) and ast.unparse(x.iter) == "actions"
            for x in ast.walk(change)
        )
        assert any(
            isinstance(x, ast.Call)
            and isinstance(x.func, ast.Name)
            and x.func.id == "_move_ticket"
            and len(x.args) > 6
            and ast.unparse(x.args[6]) == "action_status"
            for x in ast.walk(change)
        )
        assert any(
            k.arg == "require_terminal"
            and isinstance(v, ast.Constant)
            and v.value is False
            for k, v in zip(read.args.kwonlyargs, read.args.kw_defaults)
        )
        code = (
            "def closesTree (done epic : Bool) : Bool := epic\ndef rejects (pen"
            "ding closeTree companion : Bool) : Bool := pending && (!closeTree"
            " || !companion)\ndef selectChild (terminal childTerminal : Bool) :"
            " Bool := terminal && !childTerminal\ndef actionCanceled (parentCan"
            "celed isParent : Bool) : Bool := if isParent then parentCanceled "
            "else true"
        )
    lean = (
        """set_option linter.unusedVariables false\n"""
        + code
        + """\n-- One valid Epic, one unfinished Current child, a valid companion; status is canceled.\ndef accepted : Bool := !(rejects true (closesTree false true) true)\n-- Independent invariant: an unfinished child is canceled before its parent.\n#eval accepted && selectChild true false && actionCanceled true false\n"""
    )
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / "Check.lean"
        f.write_text(lean)
        run = subprocess.run(
            [a.lean, str(f)], text=True, capture_output=True, timeout=30
        )
    if run.returncode or run.stdout.strip() not in ("true", "false"):
        raise ValueError("Lean failed: " + run.stdout + run.stderr)
    if run.stdout.strip() == "false":
        result["findings"].append(
            {
                "path": str(source.relative_to(a.checkout)),
                "detail": (
                    "Canceling an Epic with an unfinished child is rejected before the"
                    " child can be canceled (Lean counterexample)."
                ),
            }
        )
except (
    OSError,
    ValueError,
    StopIteration,
    AssertionError,
    subprocess.SubprocessError,
    SyntaxError,
) as e:
    result["unresolved"].append(str(e) or "unrecognized source shape")
print(json.dumps(result))
