"""Check stable-table freshness for a bounded full rebuild."""

import argparse
import ast
import json
import re
import subprocess
import tempfile
from pathlib import Path

from _effects import expand_helper
from _extract import extract

parser = argparse.ArgumentParser()
parser.add_argument("checkout", type=Path)
parser.add_argument("--lean", required=True)
parser.add_argument("--emit", type=Path)
parser.add_argument("--case", type=Path)
parser.add_argument("--file", type=Path)
args = parser.parse_args()
result = {"findings": [], "unresolved": []}


def validate_acyclic(order, pairs):
    pending = set(order)
    while pending:
        ready = {
            x
            for x in pending
            if not any(b == x and a in pending for a, b in pairs)
        }
        if not ready:
            raise ValueError("unsupported graph: dependency cycle")
        pending -= ready


def graph():
    data = (
        json.loads(args.case.read_text())
        if args.case
        else {"order": ["A", "B"], "edges": [["A", "B"]]}
    )
    order, edges, released = (
        data["order"],
        data["edges"],
        data.get("released", []),
    )
    if (
        not isinstance(order, list)
        or not 1 <= len(order) <= 32
        or any(not isinstance(x, str) or not x for x in order)
        or len(set(order)) != len(order)
        or not isinstance(edges, list)
        or len(edges) > 256
    ):
        raise ValueError(
            (
                "unsupported graph: expected 1..32 unique query ide"
                "ntities and at most 256 edges"
            )
        )
    if (
        not isinstance(released, list)
        or any(not isinstance(x, str) or x not in order for x in released)
        or len(set(released)) != len(released)
    ):
        raise ValueError("unsupported released observations")
    pairs = []
    for edge in edges:
        if (
            not isinstance(edge, list)
            or len(edge) != 2
            or any(not isinstance(x, str) or x not in order for x in edge)
            or edge[0] == edge[1]
            or edge in pairs
        ):
            raise ValueError("unsupported graph edge: " + repr(edge))
        pairs.append(edge)
    validate_acyclic(order, pairs)
    return order, pairs, released


def check(events, order, edges):
    root = next(
        p
        for p in Path(__file__).resolve().parents
        if (p / "_anechoic_anechoic").is_dir()
    )
    solution = root / (
        "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/IWE_C"
        "ONSOLE_C43/FEATURE_IWE_CONSOLE_BACKEND_C45/_SWD/AN"
        "-S-1363-SWD--keep-duckdb-projection-ownership-in-t"
        "he-existing-server.md"
    )
    match = re.search(
        r"### Formal Claim\s+.*?```lean\n(.*?)```",
        solution.read_text(),
        re.DOTALL,
    )
    if not match or "namespace SavedQueryRebuild" not in match.group(1):
        raise ValueError("saved-query formal claim not found")
    source = match.group(1) + "\nopen SavedQueryRebuild\n"
    source += (
        "def extractedEvents : List Effect := ["
        + ", ".join(f".{e} {i}" for e, i in events)
        + "]\n"
    )
    for a, b in edges:
        source += (
            f"#eval readsFresh extractedEvents {order.index(a)} "
            f"{order.index(b)}\n"
        )
    if args.emit:
        args.emit.write_text(source)
    return check_lean(source, edges)


def check_lean(source, edges):
    with tempfile.TemporaryDirectory() as tmp:
        leanfile = Path(tmp) / "check.lean"
        leanfile.write_text(source)
        run = subprocess.run(
            [args.lean, str(leanfile)],
            capture_output=True,
            text=True,
            timeout=45,
        )
    lines = run.stdout.splitlines()
    if (
        run.returncode
        or len(lines) != len(edges)
        or any(x not in ("true", "false") for x in lines)
    ):
        raise ValueError("Lean failed: " + run.stderr + run.stdout)
    return [edge for edge, value in zip(edges, lines) if value == "false"]


seen = 0
try:
    order, edges, released = graph()
    checkout = args.checkout.resolve()
    if args.file:
        if args.file.is_absolute():
            raise ValueError("source file must be checkout-relative")
        path = (checkout / args.file).resolve()
        if not path.is_relative_to(checkout) or not path.is_file():
            raise ValueError("source file must be inside checkout")
        paths = [path]
    else:
        roots = [
            root
            for layer in checkout.glob("LAYER_*")
            if layer.is_dir()
            for root in layer.rglob("FEATURE_WORKBENCH_BACKEND")
        ]
        paths = [p for root in roots for p in root.rglob("query_store.py")]
        paths += list(
            checkout.glob("LAYER_*/KERNEL_MIXER_C59/_result_lifecycle.py")
        )
        if len(paths) != 1:
            raise ValueError("expected one rebuild source")
    for path in paths:
        rel = str(path.relative_to(checkout))
        try:
            text = path.read_text()
            if not all(
                term in text
                for term in (
                    "prepare_result_rebuild",
                    "_materialize",
                    "workbench_results",
                )
            ):
                continue
            tree = ast.parse(text)
            methods = [
                n
                for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef)
                and n.name == "prepare_result_rebuild"
            ]
            if not methods:
                continue
            if len(methods) != 1:
                raise ValueError("expected one rebuild method")
            expand_helper(tree, methods[0])
            failed = check(
                extract(methods[0], order, tree, released), order, edges
            )
            seen += 1
            for a, b in failed:
                result["findings"].append(
                    {
                        "path": rel,
                        "detail": (
                            f"The dependent saved query {b} reads {a} before "
                            "its replacement is bound to its stable table."
                        ),
                    }
                )
        except (
            OSError,
            SyntaxError,
            ValueError,
            subprocess.TimeoutExpired,
        ) as error:
            result["unresolved"].append({"path": rel, "detail": str(error)})
    if not seen and not result["unresolved"]:
        result["unresolved"].append(
            {"path": ".", "detail": "rebuild source not found"}
        )
except (
    OSError,
    ValueError,
    KeyError,
    TypeError,
    json.JSONDecodeError,
) as error:
    result["unresolved"].append({"path": ".", "detail": str(error)})
print(json.dumps(result))
