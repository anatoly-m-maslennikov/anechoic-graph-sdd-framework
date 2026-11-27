"""Compare the admitted Python carrier, its Lean model, and a Spec model."""

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .carrier_direct import compare_direct
from .carrier_formal import formal_inputs
from .carrier_model import _SOURCE, generate
from .carrier_observations import lean_bytes as lean_bytes
from .carrier_observations import observe
from .carrier_observations import python_checks as python_checks
from ._carrier_compare_helpers import (
    _CASES,
    _checks,
    _findings,
    _formal_program,
    _formal_report,
    _valid_formal_values,
)
from .carrier_runtime_effects import analyze_carrier


def compare(
    root,
    lean="lean",
    formal_only=False,
    *,
    manifest=None,
    solution=None,
    formal_verifier=None,
    implementation_sha256=None,
):
    """Return binding evidence, findings, and unresolved gaps."""
    pins = (manifest, solution, formal_verifier, implementation_sha256)
    if any(item is not None for item in pins):
        if (
            formal_only
            or manifest is None
            or solution is None
            or not callable(formal_verifier)
        ):
            raise ValueError(
                "direct comparison requires two pins and a formal verifier"
            )
        return compare_direct(
            root,
            manifest,
            solution,
            formal_verifier,
            lean,
            implementation_sha256=implementation_sha256,
        )
    if formal_only:
        return _formal_compare(root, lean)
    source = (Path(root) / _SOURCE).read_bytes()
    model, evidence = generate(root, source)
    evidence["effects"] = analyze_carrier(source)
    blocks, evidence["formal"] = formal_inputs(root)
    evidence["unresolved"].append(
        "Spec Engine Python-to-Lean compilation is unsupported"
    )
    rows = observe(root, evidence, source, _CASES)
    return _compare_observed(lean, model, evidence, blocks, rows)


def _compare_observed(lean, model, evidence, blocks, rows):
    executable = shutil.which(lean)
    if executable is None:
        evidence["unresolved"].append("Lean executable unavailable")
        return {"status": "unresolved", "evidence": evidence, "cases": rows}
    text = "\n".join(
        re.sub(r"^\s*import Lean\s*\n", "", block, count=1) for block in blocks
    )
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "CarrierComparison.lean"
        path.write_text(model + "\n" + text + "\n" + _checks(rows))
        try:
            result = subprocess.run(
                [executable, str(path)],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
        except subprocess.TimeoutExpired:
            evidence["unresolved"].append("Lean comparison timed out")
            return {
                "status": "unresolved",
                "evidence": evidence,
                "cases": rows,
            }
    try:
        values = json.loads(result.stdout)
    except json.JSONDecodeError:
        values = None
    if (
        result.returncode
        or not isinstance(values, list)
        or len(values) != len(rows) * 6
        or not all(type(value) is bool for value in values)
    ):
        evidence["unresolved"].append(
            "Lean comparison failed: " + (result.stderr + result.stdout)[:2000]
        )
        return {"status": "unresolved", "evidence": evidence, "cases": rows}
    return _findings(rows, values, evidence)


def _formal_compare(root, lean):
    evidence = {
        "scope": (
            "Eight byte witnesses only; no inference for unmodeled "
            "boundary behavior."
        ),
        "coverage_unresolved": [
            "Unmapped Manifest entries and unmodeled code, state, I/O and "
            "boundary behavior are not checked."
        ],
        "unresolved": [],
    }
    try:
        blocks, evidence["formal"] = formal_inputs(root)
    except (OSError, ValueError, SyntaxError) as exc:
        evidence["unresolved"].append("Formal binding: " + str(exc))
        return _formal_report("unresolved", evidence, [], [])
    executable = shutil.which(lean)
    if executable is None:
        evidence["unresolved"].append("Lean executable unavailable")
        return _formal_report("unresolved", evidence, [], [])
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "FormalComparison.lean"
        path.write_text(_formal_program(blocks))
        try:
            result = subprocess.run(
                [executable, str(path)],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
        except subprocess.TimeoutExpired:
            evidence["unresolved"].append("Lean comparison timed out")
            return _formal_report("unresolved", evidence, [], [])
    try:
        values = json.loads(result.stdout)
        if result.returncode or not _valid_formal_values(values):
            raise ValueError("unexpected Lean result")
    except ValueError, TypeError:
        evidence["unresolved"].append(
            "Lean comparison failed: " + (result.stderr + result.stdout)[:2000]
        )
        return _formal_report("unresolved", evidence, [], [])
    return _formal_cases(values, evidence)


def _formal_cases(values, evidence):
    findings = []
    cases = []
    for i, (name, raw) in enumerate(_CASES.items()):
        contract, solution = values[2 * i : 2 * i + 2]
        row = {
            "name": name,
            "raw": list(raw),
            "contract": contract,
            "solution": solution,
        }
        cases.append(row)
        if contract != solution:
            findings.append(
                {
                    "kind": "formal_disagreement",
                    "case": name,
                    "raw": list(raw),
                    "bounds": contract[0] != solution[0],
                    "body": contract[1] != solution[1],
                }
            )
    return _formal_report(
        "mismatch" if findings else "no_mismatch_in_cases",
        evidence,
        cases,
        findings,
    )


def _validate_spec_pins(pins):
    for role in ("manifest", "solution"):
        source = pins.get(role)
        if not isinstance(source, dict) or not _valid_digest(
            source.get("sha256")
        ):
            raise ValueError(f"{role} pin requires a lowercase SHA-256 digest")


def _compare_pinned(root, path, lean, component):
    request = json.loads(path.read_text(encoding="utf-8"))
    keys = {"manifest", "solution", "implementation_sha256"}
    if component == "C87":
        keys.add("witness")
    optional = {"export_sha256"} if component in ("C87", "C90") else set()
    if not isinstance(request, dict) or request.keys() - optional != keys:
        raise ValueError("pins require " + ", ".join(sorted(keys)))
    _validate_spec_pins(request)
    if "export_sha256" in request and not _valid_digest(
        request["export_sha256"]
    ):
        raise ValueError("export_sha256 must be a lowercase SHA-256 digest")

    from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
        verify_formal_chain,
    )

    digests = request["implementation_sha256"]
    if component == "C88":
        from .c88_compare import compare_c88

        return compare_c88(root, request, verify_formal_chain, lean)
    if component == "C87":
        return _compare_renderer_pinned(
            root, request, verify_formal_chain, lean
        )
    if not _valid_digest(digests):
        raise ValueError(
            "implementation_sha256 must be a lowercase SHA-256 digest"
        )
    if component == "C90":
        from .diagnostic_compare import compare_diagnostic

        return compare_diagnostic(root, request, verify_formal_chain, lean)
    return compare(root, lean, formal_verifier=verify_formal_chain, **request)


def _compare_renderer_pinned(root, request, verify_formal_chain, lean):
    digests = request["implementation_sha256"]
    from .renderer_compare import RENDERER_SOURCE_NAMES, compare_renderer

    witness = request["witness"]
    if not isinstance(witness, dict) or witness.keys() != {
        "manifest",
        "solution",
    }:
        raise ValueError(
            "renderer witness requires manifest and solution pins"
        )
    _validate_spec_pins(witness)
    if (
        not isinstance(digests, dict)
        or digests.keys() != set(RENDERER_SOURCE_NAMES)
        or not all(map(_valid_digest, digests.values()))
    ):
        raise ValueError(
            "renderer implementation_sha256 requires both source names and "
            "lowercase SHA-256 digests"
        )
    return compare_renderer(root, request, verify_formal_chain, lean)


def _valid_digest(value):
    return (
        isinstance(value, str)
        and re.fullmatch("[0-9a-f]{64}", value) is not None
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--lean", default="lean")
    parser.add_argument(
        "--component", choices=("C30", "C87", "C88", "C90"), default="C30"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--formal-only", action="store_true")
    mode.add_argument(
        "--pins",
        type=Path,
        help="JSON file with manifest, solution, and implementation_sha256",
    )
    args = parser.parse_args()
    if args.component != "C30" and args.pins is None:
        parser.error(f"{args.component} comparison requires --pins")
    try:
        if args.pins is None:
            report = compare(
                args.root, args.lean, formal_only=args.formal_only
            )
        else:
            report = _compare_pinned(
                args.root, args.pins, args.lean, args.component
            )
    except (OSError, ValueError, SyntaxError) as exc:
        report = {"status": "unresolved", "reason": str(exc)}
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "no_mismatch_in_cases" else 1


if __name__ == "__main__":
    raise SystemExit(main())
