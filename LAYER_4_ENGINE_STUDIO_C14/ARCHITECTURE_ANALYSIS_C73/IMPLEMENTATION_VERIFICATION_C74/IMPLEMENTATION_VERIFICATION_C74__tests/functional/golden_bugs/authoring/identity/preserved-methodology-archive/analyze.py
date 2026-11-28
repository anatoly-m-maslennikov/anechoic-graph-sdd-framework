"""Find the preserved-directory case mismatch in historical release code."""

import argparse
import ast
import json
import subprocess
import tempfile
from pathlib import Path


def fail(message):
    raise ValueError(message)


def functions(root):
    matches = {}
    for path in root.rglob("*.py"):
        if any(
            "test" in part.lower() or part.startswith(".")
            for part in path.relative_to(root).parts
        ):
            continue
        if "RELEASE" not in str(path.relative_to(root)).upper():
            continue
        try:
            tree = ast.parse(path.read_text())
        except (OSError, UnicodeError, SyntaxError) as error:
            fail(f"cannot parse release source {path}: {error}")
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in {
                "_verify_package",
                "_walk_regular_files",
                "copy_product",
            }:
                matches.setdefault(node.name, []).append((path, node))
    if any(
        len(matches.get(name, [])) != 1
        for name in ("_verify_package", "_walk_regular_files", "copy_product")
    ):
        fail(
            (
                "expected one source function per verificatio"
                "n, walk, and copy phase"
            )
        )
    return {name: matches[name][0] for name in matches}


def _directory_exclusion(verify):
    walk_calls = [
        n
        for n in ast.walk(verify)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "_walk_regular_files"
    ]
    if len(walk_calls) != 1:
        fail("verification walk call is not unique")
    keywords = {k.arg: k.value for k in walk_calls[0].keywords}
    if (
        set(keywords) != {"excluded_root_directories", "excluded_root_files"}
        or ast.unparse(keywords["excluded_root_files"]) != "preserve"
    ):
        fail("unsupported walk arguments")
    if not any(
        isinstance(n, ast.If)
        and ast.unparse(n.test) == "actual != expected"
        and len(n.body) == 1
        and ast.unparse(n.body[0])
        == (
            "raise LocalReleaseError('local-release-packa"
            "ge-verification-failed')"
        )
        for n in verify.body
    ):
        fail("unsupported package mismatch check")
    return ast.unparse(keywords["excluded_root_directories"])


def _normalizes_directory(verify, directory_arg):
    if directory_arg == "preserve":
        normalized = False
    elif directory_arg == "preserved_directories":
        assigns = [
            n
            for n in verify.body
            if isinstance(n, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == "preserved_directories"
                for t in n.targets
            )
        ]
        if (
            len(assigns) != 1
            or ast.unparse(assigns[0].value)
            != "frozenset((name.casefold() for name in preserve))"
        ):
            fail("unsupported preserved-directory normalization")
        normalized = True
    else:
        fail("unsupported directory exclusion value")
    return normalized


def _check_copy_preserve(copy):
    assignments = [
        n
        for n in copy.body
        if isinstance(n, ast.Assign)
        and any(
            isinstance(t, ast.Name) and t.id == ("preserve") for t in n.targets
        )
    ]
    if len(assignments) != 1 or ast.unparse(assignments[0].value) != (
        "_PRESERVED_NAMES | {'SUPERLAYER_1_METHODOLOGY_SO"
        "URCES', 'applicable_methodology'}"
    ):
        fail("unsupported preserved names at copy phase")
    calls = [
        n
        for n in ast.walk(copy)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "_verify_package"
    ]
    if (
        sum(
            any(
                k.arg == "preserve" and ast.unparse(k.value) == "preserve"
                for k in n.keywords
            )
            for n in calls
        )
        != 1
    ):
        fail("expected installed-package verification with preserve")


def model(root):
    found = functions(root)
    path, verify = found["_verify_package"]
    walk = found["_walk_regular_files"][1]
    copy = found["copy_product"][1]
    normalized = _normalizes_directory(verify, _directory_exclusion(verify))
    filters = [
        ast.unparse(n) for n in ast.walk(walk) if isinstance(n, ast.Compare)
    ]
    if "name.casefold() not in excluded_root_directories" not in filters:
        fail("walk does not have the expected root directory casefold filter")
    _check_copy_preserve(copy)
    return path.relative_to(root).as_posix(), normalized


def lean_source(normalized):
    selected = "name.toLower" if normalized else "name"
    return (
        "-- ASCII witness from copy_product; Python casefold equals lower "
        "for this name.\n"
        'def name : String := "SUPERLAYER_1_METHODOLOGY_SOURCES"\n'
        f"def excluded : String := {selected}\n"
        "def actualExcluded : Bool := name.toLower == excluded\n"
        "def contract : Bool := actualExcluded\n"
        f"theorem checked : contract = {'true' if normalized else 'false'} "
        ":= by native_decide\n"
        "#eval contract\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True, type=Path)
    args = parser.parse_args()
    report = {"findings": [], "unresolved": []}
    try:
        root = args.checkout.resolve(strict=True)
        path, normalized = model(root)
        with tempfile.TemporaryDirectory() as tmp:
            program = Path(tmp) / "generated.lean"
            program.write_text(lean_source(normalized))
            run = subprocess.run(
                [str(args.lean.resolve(strict=True)), str(program)],
                capture_output=True,
                text=True,
                timeout=120,
            )
        if run.returncode or run.stdout.strip().splitlines()[-1:] != [
            str(normalized).lower()
        ]:
            fail(f"Lean verification failed: {run.stdout} {run.stderr}")
        if not normalized:
            report["findings"].append(
                {
                    "path": path,
                    ("detail"): (
                        "The preserved uppercase methodology directory is"
                        " compared against casefolded directory names wit"
                        "hout normalizing the exclusion set."
                    ),
                }
            )
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        report["unresolved"].append(str(error))
    print(json.dumps(report, sort_keys=True))
    return 2 if report["unresolved"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
