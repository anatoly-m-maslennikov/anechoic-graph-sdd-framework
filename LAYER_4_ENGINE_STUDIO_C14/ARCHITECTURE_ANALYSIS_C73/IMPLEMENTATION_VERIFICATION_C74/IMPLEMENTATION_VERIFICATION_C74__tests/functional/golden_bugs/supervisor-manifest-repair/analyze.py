"Check the two known supervisor ASTs for initial invalid-Manifest recovery."

import argparse
import ast
import json
from pathlib import Path
import subprocess
import tempfile


def shape(path):
    return ast.dump(
        ast.parse(path.read_text(encoding="utf-8")), include_attributes=False
    )


def classify(checkout, case):
    candidates = [
        p
        for p in checkout.rglob("shared_supervisor.py")
        if p.parent.name == "docker" and p.parent.parent.name == "FEATURE_MCP"
    ]
    if len(candidates) != 1:
        raise ValueError(
            "expected one supervisor module, "
            f"found {len(candidates)}"
        )  # fmt: skip
    path = candidates[0]
    actual = shape(path)
    if actual == shape(case / "before.py.txt"):
        state = False
    elif actual == shape(case / "fixed.py.txt"):
        state = True
    else:
        raise ValueError("unsupported supervisor implementation structure")
    return path, state


def check_lean(lean, source, value):
    with tempfile.TemporaryDirectory() as tmp:
        proof = Path(tmp) / "manifest.lean"
        proof.write_text(source)
        run = subprocess.run(
            [lean, str(proof)], capture_output=True, text=True, timeout=30
        )
    if run.returncode or run.stdout.strip() != str(value).lower():
        raise ValueError(
            "Lean could not establish the modeled transition: "
            + (run.stderr or run.stdout).strip()
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True)
    args = parser.parse_args()
    result = {"findings": [], "unresolved": []}
    try:
        case = Path(__file__).parent
        path, value = classify(args.checkout, case)
        survives = retries = diagnostics = value
        value = survives and retries and diagnostics
        source = (
            f"def failSoft (survives retries diagnostics : Bool) : Bool := "
            "survives && retries && diagnostics\n"
            f"#eval failSoft {str(survives).lower()} {str(retries).lower()} "
            f"{str(diagnostics).lower()}\n"
            f"example : failSoft {str(survives).lower()} "
            f"{str(retries).lower()} {str(diagnostics).lower()} = "
            f"{str(value).lower()} := by decide\n"
        )
        check_lean(args.lean, source, value)
        if not value:
            result["findings"].append(
                {
                    "path": str(path.relative_to(args.checkout)),
                    "detail": (
                        "An initial Manifest selection ValueError exits "
                        "admission "
                        "before diagnostic service and retry can start."
                    ),
                }
            )
    except (
        OSError,
        SyntaxError,
        UnicodeError,
        ValueError,
        subprocess.TimeoutExpired,
    ) as exc:
        result["unresolved"].append({"detail": str(exc)})
    print(json.dumps(result))


if __name__ == "__main__":
    main()
