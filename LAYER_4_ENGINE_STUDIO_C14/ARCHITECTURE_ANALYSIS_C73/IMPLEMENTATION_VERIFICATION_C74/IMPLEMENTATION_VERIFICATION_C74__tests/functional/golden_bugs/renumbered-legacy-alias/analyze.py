"""Check a path-bound legacy alias with a renumbered target."""

import argparse
import ast
import json
import subprocess
import tempfile
from pathlib import Path

PATTERN = (
    "LAYER_*_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WO"
    "RKBENCH/FEATURE_WORKBENCH_BACKEND/native_project"
    "ion.py"
)


def extract(path):
    tree = ast.parse(path.read_text())
    functions = [
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "_migration_rows"
    ]
    if len(functions) != 1:
        raise ValueError("expected one migration rows function")
    guards = [
        n
        for n in ast.walk(functions[0])
        if isinstance(n, ast.If)
        and any(
            isinstance(x, ast.Constant)
            and x.value == "Invalid legacy migration reference"
            for x in ast.walk(n)
        )
    ]
    if (
        len(guards) != 1
        or not isinstance(guards[0].test, ast.BoolOp)
        or not isinstance(guards[0].test.op, ast.Or)
    ):
        raise ValueError("unsupported legacy reference guard")
    conditions = [ast.unparse(n) for n in guards[0].test.values]
    required = [
        (
            "not re.fullmatch('[A-Z]+-[A-Z]-[0-9]+@[1-9]["
            "0-9]*(?:-draft)?', old_ref)"
        ),
        "key in seen",
    ]
    mismatch = (
        "old_ref.rsplit('@', 1)[1].removesuffix('-draft')"
        " != target_ref.rsplit('@', 1)[1].removesuffix('-"
        "draft')"
    )
    if conditions not in (required, required + [mismatch]):
        raise ValueError("unsupported guard conditions: " + repr(conditions))
    return len(conditions) == 3


def run_lean(code, lean):
    with tempfile.TemporaryDirectory() as tmp:
        leanfile = Path(tmp) / "check.lean"
        leanfile.write_text(code)
        run = subprocess.run(
            [lean, str(leanfile)],
            capture_output=True,
            text=True,
            timeout=45,
        )
    if run.returncode or run.stdout.strip() not in ("true", "false"):
        raise ValueError("Lean failed: " + run.stderr + run.stdout)
    return run.stdout.strip() == "true"


def analyze(checkout, lean):
    result = {"findings": [], "unresolved": []}
    paths = list(checkout.glob(PATTERN))
    if len(paths) != 1:
        result["unresolved"].append(
            {
                ("path"): ("."),
                ("detail"): (
                    "expected one historical native projection module"
                ),
            }
        )
        return result
    path = paths[0]
    rel = str(path.relative_to(checkout))
    try:
        compare_versions = extract(path)
        code = (
            f"def compareVersions : Bool := {str(compare_versions).lower()}\n"
        )
        code += (
            "def rejects (valid seen : Bool) (oldVersion targ"
            "etVersion : String) : Bool :=\n  (!valid) || see"
            "n || (compareVersions && (oldVersion != targetVe"
            'rsion))\n#eval rejects true false "1" "2"\n'
        )
        if run_lean(code, lean):
            result["findings"].append(
                {
                    "path": rel,
                    ("detail"): (
                        "A valid unique legacy alias is rejected when its"
                        " target revision is renumbered."
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
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.checkout, args.lean)))


if __name__ == "__main__":
    main()
