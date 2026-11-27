"Recognize the two archived receipt implementations; abstain on other shapes."

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


def check_lean(lean, supported):
    source = (
        "def handled (recordsOrdinary acceptsOrdinary : Bool) : Bool := "
        "recordsOrdinary && acceptsOrdinary\n"
        f"#eval handled {str(supported).lower()} {str(supported).lower()}\n"
        f"example : handled {str(supported).lower()} "
        f"{str(supported).lower()} = {str(supported).lower()} := by decide\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        proof = Path(tmp) / "receipt.lean"
        proof.write_text(source)
        run = subprocess.run(
            [lean, str(proof)], capture_output=True, text=True, timeout=30
        )
    if run.returncode or run.stdout.strip() != str(supported).lower():
        raise ValueError(
            "Lean could not establish the modeled transition: "
            + (run.stderr or run.stdout).strip()
        )


def candidate(checkout):
    candidates = [
        p
        for p in checkout.rglob("watcher_receipts.py")
        if p.parent.name == "ORCHESTRATOR_beta_C68"
    ]
    if len(candidates) != 1:
        raise ValueError(
                "expected one orchestrator receipt module, "
                f"found {len(candidates)}"
        )  # fmt: skip
    return candidates[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True)
    args = parser.parse_args()
    result = {"findings": [], "unresolved": []}
    try:
        path = candidate(args.checkout)
        reference = Path(__file__).parent
        actual = shape(path)
        if actual == shape(reference / "before.py.txt"):
            supported = False
        elif actual == shape(reference / "fixed.py.txt"):
            supported = True
        else:
            raise ValueError("unsupported receipt implementation structure")
        check_lean(args.lean, supported)
        if not supported:
            result["findings"].append(
                {
                    "path": str(path.relative_to(args.checkout)),
                    "detail": (
                        "A known ordinary directory creation with a valid "
                        "carrier witness is not recognized as handled when "
                        "archive_epoch "
                        "is absent."
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
