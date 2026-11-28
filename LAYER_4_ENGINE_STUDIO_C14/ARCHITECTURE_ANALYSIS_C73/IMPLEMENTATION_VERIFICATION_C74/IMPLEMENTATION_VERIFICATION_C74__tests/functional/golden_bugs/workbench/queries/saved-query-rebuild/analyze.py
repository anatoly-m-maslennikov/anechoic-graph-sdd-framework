"""Check case normalization in historical saved-query rebuild selection."""

import argparse
import ast
import json
import subprocess
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("checkout", type=Path)
parser.add_argument("--lean", required=True)
parser.add_argument("--emit", type=Path)
args = parser.parse_args()
result = {"findings": [], "unresolved": []}
seen = 0
roots = list(args.checkout.rglob("FEATURE_WORKBENCH_BACKEND"))
if len(roots) != 1:
    result["unresolved"].append(
        {"path": ".", "detail": "expected one Workbench backend directory"}
    )
for root in roots:
    paths = list(root.rglob("*.py"))
    if len(paths) > 10000:
        result["unresolved"].append(
            {"path": str(root), "detail": "source file limit exceeded"}
        )
        continue
    for path in paths:
        rel = str(path.relative_to(args.checkout))
        try:
            text = path.read_text()
            if not all(
                word in text
                for word in (
                    "prepare_result_rebuild",
                    "affected_tables",
                    "get_table_names",
                )
            ):
                continue
            tree = ast.parse(text)
            methods = [
                n
                for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef)
                and n.name == "prepare_result_rebuild"
            ]  # fmt: skip
            if not methods:
                continue
            if len(methods) != 1:
                raise ValueError("expected one rebuild method")
            method = methods[0]
            assignments = [
                n
                for n in ast.walk(method)
                if isinstance(n, ast.Assign)
                and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name)
            ]
            affected = [
                n for n in assignments if n.targets[0].id == "affected_tables"
            ]  # fmt: skip
            deps = [
                n
                for n in assignments
                if n.targets[0].id == "dependencies"
                and isinstance(n.value, ast.SetComp)
            ]
            if len(affected) != 1 or len(deps) != 1:
                raise ValueError("unsupported dependency assignments")
            left = ast.unparse(affected[0].value)
            right = ast.unparse(deps[0].value)
            lowered_tables = (
                "{name.rsplit('.', 1)[-1].lower() for name in tables "
                "or ()}"
            )  # fmt: skip
            supported_left = {
                "{name.rsplit('.', 1)[-1] for name in tables or ()}": False,
                lowered_tables: True,
            }
            supported_right = {
                "{name.rsplit('.', 1)[-1] for name in dependencies}": False,
                (
                    "{name.lower() for name in self._connection."
                    "get_table_names(old.sql)}"
                ): True,  # fmt: skip
            }
            if left not in supported_left or right not in supported_right:
                detail = (
                    "unsupported normalization expression: "
                    + left
                    + "; "
                    + right
                )  # fmt: skip
                raise ValueError(detail)
            gates = [
                n
                for n in ast.walk(method)
                if isinstance(n, ast.If)
                and ast.unparse(n.test)
                == "not affected_tables.intersection(dependencies)"
            ]
            if (
                len(gates) != 1
                or len(gates[0].body) != 1
                or not isinstance(gates[0].body[0], ast.Continue)
            ):
                raise ValueError("unsupported rebuild selection gate")
            if not any(
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == "get_table_names"
                for n in ast.walk(method)
            ):
                raise ValueError("table-name source not found")
            source = (
                "def leftLower : Bool := "
                f"{str(supported_left[left]).lower()}\n"
            )  # fmt: skip
            source += (
                "def rightLower : Bool := "
                f"{str(supported_right[right]).lower()}\n"
            )  # fmt: skip
            source += (
                "def norm (s : String) (lower : Bool) : String := "
                "if lower then s.toLower else s\n"
                'def rebuilds : Bool := norm "atoms" leftLower == '
                'norm "ATOMS" rightLower\n'
                "#eval rebuilds\n"
            )
            if args.emit:
                args.emit.write_text(source)
            with tempfile.TemporaryDirectory() as tmp:
                leanfile = Path(tmp) / "check.lean"
                leanfile.write_text(source)
                run = subprocess.run(
                    [args.lean, str(leanfile)],
                    capture_output=True,
                    text=True,
                    timeout=45,
                )
            if run.returncode or run.stdout.strip() not in ("true", "false"):
                raise ValueError("Lean failed: " + run.stderr + run.stdout)
            seen += 1
            if run.stdout.strip() == "false":
                result["findings"].append(
                    {
                        "path": rel,
                        "detail": (
                            "A lowercase changed table and uppercase SQL "
                            "dependency do not match, so the dependent saved "
                            "result is skipped."
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
    )  # fmt: skip
print(json.dumps(result))
