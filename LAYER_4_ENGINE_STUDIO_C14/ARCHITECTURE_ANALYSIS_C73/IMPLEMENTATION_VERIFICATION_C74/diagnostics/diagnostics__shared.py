"""Compare C90 finding and verdict Specs with implementation Lean."""

import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from ..export_binding import export_check, export_pin
from ._diagnostic_compare_lean import _VERDICT_STATEMENT, _CHECK

_SOURCE = Path(
    "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/"
    "LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_1_DIAGNOSTICS_C90/"
    "diagnostics__pub.py"
)
_TRANSLATOR = (
    "ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.code_to_lean"
)


def _execute(command, timeout):
    result = subprocess.run(
        command, capture_output=True, text=True, timeout=timeout, check=False
    )
    if result.returncode:
        raise ValueError((result.stderr + result.stdout).strip()[-2000:])
    return result.stdout


def _prove_finding(program, facts, lean):
    expected = {
        (("requested", field), ("result_returned", field))
        for field in ("source", "field", "message")
    }
    if (
        not isinstance(facts, list)
        or len(facts) != len(expected)
        or {
            (tuple(row["left"]), tuple(row["right"]))
            for row in facts
            if row["solution"] == row["implementation"] == "matched"
        }
        != expected
    ):
        return {
            "status": "unresolved",
            "reason": (
                "Finding proof requires all three matching identity bindings."
            ),
        }
    try:
        proof = Path(__file__).with_name("diagnostic_finding_proof.lean")
        with program.open("a", encoding="utf-8") as file:
            file.write("\n" + proof.read_text(encoding="utf-8"))
        _execute([lean, "-DwarningAsError=true", str(program)], 120)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        return {"status": "unresolved", "reason": str(error)}
    return {
        "status": "proved",
        "theorem": "findingPreservesValues",
        "quantified_over": ["heap", "globals", "source", "field", "message"],
    }


def _verdict_spec(root, pins, formal_verifier, lean):
    report = formal_verifier(root, "C90", **pins, action="verdict", lean=lean)
    evidence = report.get("evidence", {})
    findings = evidence.get("coverage", ())
    if (
        report.get("sources") == pins
        and report["translation"]["status"] == "matched"
        and report["status"] != "conflicting"
        and not report["issues"]
        and not report["uncovered_outcomes"]
        and evidence.get("action") == "verdict"
        and findings
        and all(row["status"] == "matched" for row in findings)
    ):
        return report["lean"]
    return None


def _prove_verdict(file, translated, provider, authored, lean):
    if authored is None:
        return {
            "status": "unresolved",
            "reason": "Verdict Contract and Solution are unverified.",
        }
    result = {
        "status": "proved",
        "theorem": "publicVerdictMatchesContract",
        "scope": "Pinned verdict Contract for heap-backed string lists.",
        "authored_lean_sha256": sha256(authored.encode()).hexdigest(),
    }
    try:
        proof_path = Path(__file__).with_name("diagnostic_verdict_proof.lean")
        proof = proof_path.read_bytes()
        result["sha256"] = sha256(proof).hexdigest()
        file.write_text(
            translated
            + authored.removeprefix("import Lean\n")
            + export_check("verdict", provider)
            + proof.decode("utf-8")
            + _VERDICT_STATEMENT,
            encoding="utf-8",
        )
        _execute([lean, "-DwarningAsError=true", str(file)], 120)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        result.update(status="unresolved", reason=str(error))
    return result


def _translate(root, path, export, digest, model):
    _execute(
        [
            sys.executable,
            "-B",
            "-m",
            _TRANSLATOR,
            str(path),
            str(root / export["path"]),
            "--sha256",
            digest,
            "--sha256",
            export["sha256"],
            "--output",
            str(model),
        ],
        1800,
    )


def _observe(root, digest, export, finding, verdict_spec, lean):
    path = root / _SOURCE
    if path.resolve(strict=True) != path:
        raise ValueError(
            "Diagnostics source must be a regular file at its Project path"
        )
    with TemporaryDirectory(prefix="anechoic-diagnostic-lean-") as folder:
        model = Path(folder) / "Implementation.lean"
        _translate(root, path, export, digest, model)
        program = Path(folder) / "Comparison.lean"
        translated = "import Lean\n" + model.read_text(encoding="utf-8") + "\n"
        finding_program = translated + finding.removeprefix("import Lean\n")
        program.write_text(
            finding_program + export_check("finding", path.name) + _CHECK,
            encoding="utf-8",
        )
        facts, formation = json.loads(_execute([lean, str(program)], 120))
        if formation not in ("matched", "conflicting", "unresolved"):
            raise ValueError("Lean returned an invalid finding effect check")
        proof = _prove_finding(program, facts, lean)
        if formation == "matched":
            formation = proof["status"]
        effect = {
            "target": "C90.source_diagnostic",
            "outcome": "formed",
            "status": formation,
        }
        verdict = _prove_verdict(
            Path(folder) / "Verdict.lean",
            translated,
            path.name,
            verdict_spec,
            lean,
        )
        return facts, proof, effect, verdict


def _checked_finding_obligation(fact):
    if (fact.get("action"), fact.get("output")) != ("finding", "reported"):
        return False
    if fact["key"] == "must_effect":
        return tuple(fact["left"]) == ("C90.source_diagnostic", "formed")
    return fact["key"] in ("action", "terminal_output", "same_values")


def _unresolved_obligations(evidence):
    pending = [
        fact
        for fact in evidence["coverage"]
        if not _checked_finding_obligation(fact)
    ]
    pending.extend(
        {"key": "terminal_output", **row}
        for row in evidence.get("uncovered_outcomes", ())
    )
    return [{**fact, "status": "unresolved"} for fact in pending]


def _finding_verdict(report, facts, proof, effect):
    states = {
        fact[role] for fact in facts for role in ("solution", "implementation")
    }
    if states - {"matched", "conflicting", "unresolved"}:
        raise ValueError("Lean returned unknown comparison status")
    if any(fact["solution"] == "unresolved" for fact in facts):
        report["unresolved"].append(
            "C90 Solution binding is outside the supported finding path."
        )
    verdict_proved = report["verdict_proof"]["status"] == "proved"
    if not verdict_proved:
        report["unresolved"].append("C90 verdict policy remains unproved.")
    if "conflicting" in states or effect["status"] == "conflicting":
        return "mismatch"
    if effect["status"] != "proved":
        report["unresolved"].append(
            "C90 finding value preservation remains unproved."
            if proof["status"] != "proved"
            else "C90 diagnostic formation remains unresolved."
        )
    elif verdict_proved and not report["unresolved_obligations"]:
        return "no_mismatch_in_cases"
    return "unresolved"


def _diagnostic_observation(
    root, request, formal_verifier, lean, report, expected
):
    pins = {role: request[role] for role in ("manifest", "solution")}
    formal = report["formal"]
    digest = request["implementation_sha256"]
    root = Path(root).resolve(strict=True)
    export = report["public_export"] = export_pin(
        root / _SOURCE.parent,
        "finding",
        root,
        request.get("export_sha256"),
    )
    verdict_spec = _verdict_spec(root, pins, formal_verifier, lean)
    facts, proof, effect, report["verdict_proof"] = _observe(
        root, digest, export, formal["lean"], verdict_spec, lean
    )
    if (
        not isinstance(facts, list)
        or [(row["left"], row["right"]) for row in facts] != expected
    ):
        raise ValueError(
            "Lean result did not account for the declared equality obligations"
        )
    status = _finding_verdict(report, facts, proof, effect)
    return export, facts, proof, effect, status


def _finding_expected(report, pins):
    formal = report["formal"]
    if (
        formal.get("outcome") != "compared"
        or formal.get("translation", {}).get("status") != "matched"
    ):
        return None
    if formal.get("sources") != pins:
        report["unresolved"].append(
            "C90 Specs differ from their requested pins"
        )
        return None
    if formal.get("status") == "conflicting":
        report["status"] = "mismatch"
        return None
    evidence = formal["evidence"]
    pending = report["unresolved_obligations"] = _unresolved_obligations(
        evidence
    )
    if pending:
        report["unresolved"].append(
            "Declared finding obligations lack implementation evidence."
        )
    expected = [
        (list(fact["left"]), list(fact["right"]))
        for fact in evidence["coverage"]
        if fact["key"] == "same_values"
    ]
    if not expected:
        report["unresolved"].append(
            "C90 finding declares no equality obligations"
        )
        return None
    return expected


def compare_diagnostic(root, request, formal_verifier, lean):
    """Check finding identity bindings and the shared verdict policy."""
    pins = {role: request[role] for role in ("manifest", "solution")}
    formal = formal_verifier(root, "C90", **pins, action="finding", lean=lean)
    report = {
        "status": "unresolved",
        "facts": [],
        "formal": formal,
        "unresolved": ["Unobserved C90 effects require separate evidence."],
    }
    expected = _finding_expected(report, pins)
    if expected is None:
        return report
    digest = request["implementation_sha256"]
    try:
        export, facts, proof, effect, status = _diagnostic_observation(
            root, request, formal_verifier, lean, report, expected
        )
    except (
        OSError,
        ValueError,
        SyntaxError,
        KeyError,
        TypeError,
        subprocess.TimeoutExpired,
    ) as error:
        report["unresolved"].append(str(error))
        return report
    export["status"] = "matched"
    report.update(facts=facts, proof=proof, effect=effect, status=status)
    report["implementation"] = {"path": _SOURCE.as_posix(), "sha256": digest}
    return report
