"""Shared carrier comparison formatting and reports."""

import re

from .carrier_observations import lean_bytes, python_checks


_CASES = {
    "lf": b"---\na: b\n---\nbody\x00\xff",
    "crlf": b"---\r\na: b\r\n---\r\nbody",
    "empty_lf": b"---\n---\nbody",
    "empty_crlf": b"---\r\n---\r\nbody",
    "missing_open": b"body",
    "missing_close": b"---\na: b\nbody",
    "mixed_lines": b"---\r\na\n---\r\nbody",
    "first_close": b"---\na\n---\nbody\n---\nlast",
}


def _checks(rows):
    checks = []
    for row in rows:
        raw = lean_bytes(row["raw"])
        b = row["bounds"]
        expected = "none" if b is None else f"some ({b[0]}, {b[1]}, {b[2]})"
        if row["body"] is None:
            suffix = "missingDelimiter"
        else:
            suffix = "body " + lean_bytes(row["body"])
        checks.extend(python_checks(row))
        for namespace in ("CarrierBodyContract", "CarrierBodySolution"):
            checks.extend(
                [
                    f"{namespace}.bounds {raw} == {expected}",
                    f"{namespace}.body {raw} == "
                    f"({namespace}.Outcome.{suffix})",
                ]
            )
    return (
        "#eval IO.println (Lean.toJson ["
        + ",\n".join(checks)
        + "]).compress\n"
    )


def _findings(rows, values, evidence):
    findings = []
    for i, row in enumerate(rows):
        code_bounds, code_body, cb, ct, sb, st = values[i * 6 : i * 6 + 6]
        row["code_matches_python"] = code_bounds and code_body
        row["contract_matches_python"] = cb and ct
        row["solution_matches_python"] = sb and st
        if not row["code_matches_python"]:
            evidence["unresolved"].append(
                "Source model differs from Python: " + row["name"]
            )
        else:
            for model, bounds, body in (
                ("contract", cb, ct),
                ("solution", sb, st),
            ):
                if not bounds or not body:
                    findings.append(
                        {
                            "model": model,
                            "case": row["name"],
                            "raw": row["raw"],
                            "bounds": not bounds,
                            "body": not body,
                            "source_symbols": evidence["symbols"],
                        }
                    )
    status = (
        "unresolved"
        if (
            evidence["effects"]["status"] != "permitted"
            or any(not r["code_matches_python"] for r in rows)
        )
        else ("mismatch" if findings else "no_mismatch_in_cases")
    )
    return {
        "status": status,
        "evidence": evidence,
        "cases": rows,
        "findings": findings,
    }


def _formal_program(blocks):
    text = "\n".join(
        re.sub(r"^\s*import Lean\s*\n", "", block, count=1) for block in blocks
    )
    adapters = [
        (
            "def normalizedBounds (b : Option (Nat × Nat × Nat)) : "
            "Option (List Nat) := "
            "b.map (fun (a, c, d) => [a, c, d])"
        )
    ]
    for ns in ("CarrierBodyContract", "CarrierBodySolution"):
        adapters.append(
            f"def {ns}Body (raw : List Nat) : Option (List Nat) := "
            f"match {ns}.body raw with | .missingDelimiter => none "
            f"| .body bytes => some bytes"
        )
    rows = []
    for raw in _CASES.values():
        value = lean_bytes(raw)
        rows.append(
            f"(normalizedBounds ({{ns}}.bounds {value}), {{ns}}Body {value})"
        )
    expr = ", ".join(
        row.format(ns=ns)
        for row in rows
        for ns in ("CarrierBodyContract", "CarrierBodySolution")
    )
    return (
        "import Lean\n"
        + text
        + "\n"
        + "\n".join(adapters)
        + ("\n#eval IO.println (Lean.toJson [" + expr + "]).compress\n")
    )


def _formal_report(status, evidence, cases, findings):
    checked = len(cases) == len(_CASES)
    behavior = []
    for index, operation in enumerate(("bounds", "body")):
        differing = [
            row["name"]
            for row in cases
            if row["contract"][index] != row["solution"][index]
        ]
        behavior.append(
            {
                "contract_operation": operation,
                "solution_operation": operation,
                "verdict": (
                    "mismatch"
                    if differing
                    else "no_mismatch_in_cases"
                    if checked
                    else "unresolved"
                ),
                "differing_cases": differing,
            }
        )
    directions = {
        "manifest_to_contract": {
            "verdict": "unresolved",
            "reason": "No comparable Manifest facts are modeled.",
        },
        "manifest_to_solution": {
            "verdict": "unresolved",
            "reason": "No comparable Manifest facts are modeled.",
        },
        "contract_to_solution": {
            "behavioral_witnesses": behavior,
            "case_count": len(cases),
        },
    }
    return {
        "status": status,
        "evidence": evidence,
        "cases": cases,
        "findings": findings,
        "directions": directions,
    }


def _valid_formal_values(values):
    def naturals(value):
        return isinstance(value, list) and all(
            type(n) is int and n >= 0 for n in value
        )

    def observation(value):
        if not isinstance(value, list) or len(value) != 2:
            return False
        bounds, body = value
        return (
            bounds is None or (naturals(bounds) and len(bounds) == 3)
        ) and (
            body is None or (naturals(body) and all(n <= 255 for n in body))
        )

    return (
        isinstance(values, list)
        and len(values) == len(_CASES) * 2
        and all(map(observation, values))
    )
