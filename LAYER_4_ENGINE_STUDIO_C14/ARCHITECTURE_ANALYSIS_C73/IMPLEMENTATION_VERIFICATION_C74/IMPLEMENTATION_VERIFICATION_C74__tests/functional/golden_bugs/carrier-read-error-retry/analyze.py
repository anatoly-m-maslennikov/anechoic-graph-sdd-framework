"""Project retry decisions from the admitted historical capture and scan \
ASTs."""

import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def functions(raw):
    tree = ast.parse(raw)
    result = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in result:
                raise ValueError("duplicate definition: " + node.name)
            result[node.name] = node
    return result


def shape(node):
    return ast.dump(node, include_attributes=False)


def body(node):
    return [
        n
        for n in node.body
        if not isinstance(n, ast.Pass)
        and not (
            isinstance(n, ast.Expr)
            and isinstance(n.value, ast.Constant)
            and isinstance(n.value.value, str)
        )
    ]


def capture_updates(observed, refs):
    capture = body(observed["capture"])
    update = ast.parse(
        "if changed is not None:\n"
        "    changed.update(path for path, source in prior.items() "
        'if source.status == "read_error")'
    ).body[0]
    updates = []
    for i, node in enumerate(capture):
        if shape(node) == shape(update):
            updates.append(i)
    if len(updates) > 1:
        raise ValueError("duplicate retry update")
    without_update = []
    for i, node in enumerate(capture):
        if i not in updates:
            without_update.append(node)
    reference = body(refs[0]["capture"])
    current_flow = [shape(node) for node in without_update]
    reference_flow = [shape(node) for node in reference]
    if current_flow != reference_flow:
        raise ValueError("unsupported capture selection flow")
    if updates and updates[0] != 4:
        raise ValueError("retry update has unsupported order")
    return updates


def extract(observed):
    if not {"_scan", "capture"} <= observed.keys():
        raise ValueError("missing capture or _scan")
    refs = [
        functions((HERE / (tag + ".py.txt")).read_bytes())
        for tag in ("before", "fixed")
    ]
    for name in ("capture", "_scan"):
        if observed[name].decorator_list or not any(
            shape(observed[name].args) == shape(ref[name].args) for ref in refs
        ):
            raise ValueError("unsupported " + name + " signature")
    scan = body(observed["_scan"])
    if len(scan) != 4 or not isinstance(scan[1], ast.If):
        raise ValueError("unsupported scan flow")
    guard = scan[1]
    if (
        guard.orelse
        or len(guard.body) != 1
        or shape(guard.body[0]) != shape(ast.parse("return previous").body[0])
    ):
        raise ValueError("unsupported scan reuse branch")
    guards = {
        "old": "previous is not None and previous.language == language "
        "and previous.signature == signature",
        "fixed": 'previous is not None and previous.status != "read_error" '
        "and previous.language == language and previous.signature == "
        "signature",
    }
    matches = [
        name
        for name, expr in guards.items()
        if shape(guard.test) == shape(ast.parse(expr, mode="eval").body)
    ]
    if len(matches) != 1:
        raise ValueError("unsupported scan reuse predicate")
    remainder = [shape(scan[i]) for i in (0, 2, 3)]
    if remainder not in [
        [shape(body(ref["_scan"])[i]) for i in (0, 2, 3)] for ref in refs
    ]:
        raise ValueError("unsupported scan read flow")
    updates = capture_updates(observed, refs)
    return bool(updates), matches[0] == "fixed"


def analyze(checkout, lean):
    paths = list(
        checkout.glob(
            "LAYER_*_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/"
            "FEATURE_IMPORT_GRAPH_C61/source.py"
        )
    )
    if len(paths) != 1:
        message = f"expected one import graph source, found {len(paths)}"
        raise ValueError(message)
    path = paths[0]
    selected, retry = extract(functions(path.read_bytes()))
    text = f"""import Lean
 def changedIncludesFailure : Bool := {str(selected).lower()}
 def scanRetriesFailure : Bool := {str(retry).lower()}
 def attempt : Bool := changedIncludesFailure && scanRetriesFailure
 def contract : Bool := true
 #eval IO.println (attempt == contract)
"""
    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / "retry.lean"
        file.write_text(text)
        run = subprocess.run(
            [lean, str(file)], capture_output=True, text=True, timeout=40
        )
    if run.returncode or run.stdout.strip() not in ("true", "false"):
        output = (run.stdout + run.stderr)[:1000]
        raise ValueError("Lean comparison failed: " + output)
    return path.relative_to(checkout).as_posix(), run.stdout.strip() == "false"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True)
    args = parser.parse_args()
    report = {"findings": [], "unresolved": []}
    try:
        path, mismatch = analyze(args.checkout.resolve(strict=True), args.lean)
        if mismatch:
            report["findings"].append(
                {
                    "path": path,
                    "detail": "An unchanged source with a prior read error is "
                    "not retried after an unrelated incremental change.",
                }
            )
    except (
        OSError,
        ValueError,
        SyntaxError,
        subprocess.TimeoutExpired,
    ) as error:
        report["unresolved"].append(str(error))
    print(json.dumps(report))


if __name__ == "__main__":
    main()
