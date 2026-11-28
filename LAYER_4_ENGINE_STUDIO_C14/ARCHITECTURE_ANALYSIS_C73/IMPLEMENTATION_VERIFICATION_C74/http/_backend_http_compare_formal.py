"""Build the formal HTTP comparison report."""

import shutil


def _compare_formal(root, lean, emit):
    from ..backend_http_compare import _actual, _checks_report, _run_lean
    from .backend_http_formal import _expected_lean, _facts

    expected, observed, facts, outcomes, extra, solution, sources = _facts(
        root
    )
    expected_lean = _expected_lean(expected)
    required = (
        "operation",
        "interface.protocol",
        "interface.transport",
        "input_format.fields",
        "error_handling.error_fields",
    )
    executable = shutil.which(str(lean))
    if executable is None:
        raise ValueError("Lean executable unavailable: " + str(lean))
    results = _checks_report(
        _run_lean(executable, expected_lean, _actual([], observed), emit)
    )
    for row in results:
        row["manifest"] = row.pop("expected")
        row["contract"] = row.pop("observed")
    results.extend(
        {
            "check": key,
            "contract": observed.get(key),
            "manifest": None,
            "status": "unresolved",
        }
        for key in required
        if key not in expected
    )
    return _formal_report(
        results, observed, facts, outcomes, extra, solution, sources
    )


def _formal_report(
    results, observed, facts, outcomes, extra, solution, sources
):
    relation = (
        "ANSWERS" if solution.metadata.get("tier") == 0 else "IS_SOLUTION_FOR"
    )
    pins = solution.metadata.get("relations", {}).get(relation, [])
    target = f"AN-S-3059@{sources['manifest']['version']}"
    reason = (
        "Solution binding targets a retired Contract, not the active Manifest"
        if target not in pins
        else (
            "Workflow event and trace semantics have no modeled mapping "
            "to HTTP Contract facts"
        )
    )
    manifest_solution, contract_solution = _solution_rows(
        results, observed, facts, outcomes, extra, reason
    )
    statuses = {row["status"] for row in results}
    return {
        "status": "mismatch" if "mismatch" in statuses else "unresolved",
        "sources": sources,
        "manifest_contract": results,
        "manifest_unmodeled_count": len(extra),
        "manifest_unmodeled": [
            {
                "check": key,
                "manifest": value,
                "status": "unresolved",
                "reason": "No modeled Contract mapping",
            }
            for key, value in sorted(extra.items())
        ],
        "manifest_solution": manifest_solution,
        "contract_solution": contract_solution,
        "solution_contract": {
            "status": "unresolved",
            "declared_pins": pins,
            "active_contract": target,
            "reason": reason,
        },
    }


def _solution_rows(results, observed, facts, outcomes, extra, reason):
    manifest_solution = [
        {
            "check": row["check"],
            "manifest": row["manifest"],
            "status": "unresolved",
            "reason": reason,
        }
        for row in results
    ]
    manifest_solution.extend(
        {
            "check": key,
            "manifest": value,
            "status": "unresolved",
            "reason": reason,
        }
        for key, value in sorted(extra.items())
    )
    contract_solution = [
        {
            "check": key,
            "contract": value,
            "status": "unresolved",
            "reason": reason,
        }
        for key, value in sorted(facts.items())
    ]
    contract_solution.append(_operation_row(observed, reason))
    contract_solution.extend(
        {
            "check": "outcomes." + name,
            "contract": [status, kind],
            "status": "unresolved",
            "reason": reason,
        }
        for name, status, kind in outcomes
    )
    return manifest_solution, contract_solution


def _operation_row(observed, reason):
    return {
        "check": "operation",
        "contract": observed.get("operation"),
        "status": "unresolved",
        "reason": reason,
    }
