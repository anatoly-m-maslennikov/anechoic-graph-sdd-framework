"""Check the historical real-Manifest release gate port assertions."""

import argparse
import ast
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = (
    "LAYER_5_FRAMEWORK_DELIVERY/RELEASE_VERSION/RELEA"
    "SE_VERSION__tests/test_release_inputs.py"
)
PORT = "selected.parameters['project_mcp']['http_port']"


def extract(path):
    tree = ast.parse(path.read_text())
    methods = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef)
        and n.name == ("test_real_project_manifest")
    ]
    if len(methods) != 1:
        raise ValueError("expected one real Manifest test")
    body = methods[0].body
    accesses = [
        n
        for n in ast.walk(methods[0])
        if isinstance(n, ast.Subscript) and ast.unparse(n) == PORT
    ]
    if len(accesses) != 1:
        raise ValueError("unsupported port access count")
    equal = [
        n.value
        for n in body
        if isinstance(n, ast.Expr)
        and isinstance(n.value, ast.Call)
        and ast.unparse(n.value.func) == "self.assertEqual"
        and len(n.value.args) == 2
        and ast.unparse(n.value.args[1]) == PORT
    ]
    assignments = [
        n
        for n in body
        if isinstance(n, ast.Assign)
        and len(n.targets) == 1
        and ast.unparse(n.targets[0]) == "port"
        and ast.unparse(n.value) == PORT
    ]
    if (
        len(equal) == 1
        and not assignments
        and isinstance(equal[0].args[0], ast.Constant)
        and type(equal[0].args[0].value) is int
    ):
        return "equal", equal[0].args[0].value, 0
    if equal or len(assignments) != 1:
        raise ValueError("unsupported port assertion")
    return extract_range(body, assignments, methods[0])


def extract_range(body, assignments, method):
    calls = [
        n.value
        for n in body
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
    ]
    typed = [
        n
        for n in calls
        if ast.unparse(n.func) == "self.assertIs"
        and [ast.unparse(a) for a in n.args] == ["type(port)", "int"]
    ]
    ranges = [
        n
        for n in calls
        if ast.unparse(n.func) == "self.assertTrue"
        and n.args
        and isinstance(n.args[0], ast.Compare)
        and ast.unparse(n.args[0].left).isdigit()
        and [type(o) for o in n.args[0].ops] == [ast.LtE, ast.LtE]
        and ast.unparse(n.args[0].comparators[0]) == "port"
        and ast.unparse(n.args[0].comparators[1]).isdigit()
    ]
    if len(typed) != 1 or len(ranges) != 1:
        raise ValueError("unsupported port type or bounds")
    allowed = {
        id(n)
        for part in (assignments[0], typed[0], ranges[0])
        for n in ast.walk(part)
    }
    if any(
        isinstance(n, ast.Name) and n.id == "port" and id(n) not in allowed
        for n in ast.walk(method)
    ):
        raise ValueError("unsupported additional port use")
    compare = ranges[0].args[0]
    return "range", compare.left.value, compare.comparators[1].value


def counterexample(kind, low, high):
    if kind == "equal":
        return 51487 if low != 51487 else 1
    if low > 1:
        return 1
    if high < 65535:
        return 65535
    if low < 1:
        return 0
    if high > 65535:
        return 65536
    return None


def lean_source(kind, low, high, witness):
    predicate = (
        f"port == {low}"
        if kind == "equal"
        else f"isInt && ({low} ≤ port) && (port ≤ {high})"
    )
    if witness is None:
        proof = (
            "example (port : Int) (isInt : Bool) : accepts po"
            "rt isInt = contract port isInt := by rfl"
        )
        result = "false"
    else:
        proof = (
            f"example : accepts {witness} true ≠ "
            f"contract {witness} true := by decide"
        )
        result = "true"
    return f"""set_option linter.unusedVariables false
def accepts (port : Int) (isInt : Bool) : Bool := {predicate}
def contract (port : Int) (isInt : Bool) : Bool := isInt && (1 ≤ port) && \
(port ≤ 65535)
{proof}
#eval {result}
"""


def verify(lean, kind, low, high, witness):
    with tempfile.TemporaryDirectory() as tmp:
        program = Path(tmp) / "port.lean"
        program.write_text(lean_source(kind, low, high, witness))
        run = subprocess.run(
            [lean, str(program)],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    if run.returncode or run.stdout.strip() not in ("true", "false"):
        raise ValueError(("Lean failed: ") + (run.stdout + run.stderr)[:1000])
    return run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True)
    parser.add_argument(
        "--file", default=SOURCE, help="Test module relative to checkout"
    )
    args = parser.parse_args()
    report = {"findings": [], "unresolved": []}
    try:
        root = args.checkout.resolve(strict=True)
        if Path(args.file).is_absolute():
            raise ValueError("test module path must be relative")
        path = (root / args.file).resolve(strict=True)
        if not path.is_relative_to(root):
            raise ValueError("test module must be inside checkout")
        kind, low, high = extract(path)
        witness = counterexample(kind, low, high)
        run = verify(args.lean, kind, low, high, witness)
        if run.stdout.strip() == "true":
            report["findings"].append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "detail": (
                        f"The release gate test rejects valid port {witness}."
                        if 1 <= witness <= 65535
                        else (
                            f"The release gate test accepts invalid port "
                            f"{witness}."
                        )
                    ),
                }
            )
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
