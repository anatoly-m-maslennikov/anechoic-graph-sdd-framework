"""Check the formal Manifest, Contract and Solution for a Tool API \
invocation."""

from ..LAYER_1_DIAGNOSTICS_C90._package__shared import finding
from ..LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model
from ..LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    select_formal_claims,
)  # fmt: skip
from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from ..LAYER_3_MERMAID_RENDERER_C87._package__shared import render_solution
from ._direct_comparison import comparison_claims, report_comparison
from .tool_api_obligations__pub import (
    contract_tool_api,
    manifest_tool_api,
    solution_tool_api,
)
from .top_down__pub import compare_obligations

_UNRENDERED = object()


def _tool_contract(claim):
    profiles = claim.get("operations", {"": claim})
    contracts = [
        profile
        for profile in profiles.values()
        if "facts" in profile
        and profile.get("profile") != "http"
        and profile.get("operation") == "POST /tools"
    ]
    return contracts[0] if len(contracts) == 1 else {}


def _tool_solution(workflow, operation, action, expected=None):
    if "operations" in workflow:
        profiles = workflow["operations"]
        if action is None:
            candidates = [
                facts
                for profile in profiles.values()
                if (
                    observed := (
                        facts := solution_tool_api(profile, expected)
                    ).get("operation")
                )
                == [operation]
                or (
                    isinstance(observed, dict)
                    and [operation] in observed["conflicting_values"]
                )
            ]
            return candidates[0] if len(candidates) == 1 else {}
        workflow = profiles.get(action, {})
    if not workflow or (
        action is not None and workflow.get("action") != action
    ):
        return {}
    return solution_tool_api(workflow, expected)


def check_tool_api_spec(
    root,
    component_id,
    manifest,
    contract=None,
    solution=None,
    *,
    action=None,
    lean="lean",
):
    """Compare an exact specification chain and keep unmodeled obligations \
visible."""
    model = select_formal_claims(
        load_boundary_model(root, component_id, manifest, contract, solution),
        action,
    )
    return compare_tool_api_spec(
        model, compile_lean(model), action=action, lean=lean
    )


def _tool_obligations(claims, action):
    manifest_fields = claims.get("manifest", {}).get("boundaries") or {}
    io = manifest_fields.get("io")
    server = io.get("server") if isinstance(io, dict) else None
    api = server.get("tool_api") if isinstance(server, dict) else None
    declared, extra = (
        manifest_tool_api(api) if isinstance(api, dict) else ({}, {})
    )
    tool_contract = _tool_contract(claims.get("contract", {}))
    contract = contract_tool_api(tool_contract) if tool_contract else {}
    obligations = {
        "manifest": declared,
        "contract": contract,
        "solution": _tool_solution(
            claims.get("solution", {}),
            tool_contract.get("operation"),
            action,
            contract,
        ),
    }
    return obligations, extra


def _tool_conflicts(source, solution):
    return [
        finding(
            source,
            key,
            f"Solution declares inconsistent {key}: "
            f"{value['conflicting_values']}",
        )
        for key, value in solution.items()
        if isinstance(value, dict) and "conflicting_values" in value
    ]


def compare_tool_api_spec(
    model,
    compiled,
    *,
    action=None,
    lean="lean",
    mermaid=_UNRENDERED,
    observe=None,
):
    claims = comparison_claims(compiled, observe, action, "tool_api")
    sources = {
        role: model[role]["source"]
        for role in ("manifest", "contract", "solution")
    }
    obligations, extra = _tool_obligations(claims, action)
    unclassified = obligations["solution"].pop("_unclassified_terminal", False)
    if mermaid is _UNRENDERED:
        mermaid = render_solution(model, claims.get("solution"), action=action)
    report = compare_obligations(sources, obligations, lean=lean)
    conflicts = _tool_conflicts(sources["solution"], obligations["solution"])
    unresolved = list(compiled["unresolved"])
    if unclassified:
        unresolved.append(
            finding(
                sources["solution"],
                "http_outcome",
                "Solution has an unclassified terminal output",
            )
        )
    report.update(
        issues=[*compiled["issues"], *conflicts],
        unresolved=unresolved,
        unmodeled_tool_api=extra,
        mermaid=mermaid,
    )
    if conflicts:
        report["status"] = "conflicting"
    if report["status"] == "matched" and (
        report["issues"] or report["unresolved"] or extra
    ):
        report["status"] = "unresolved"
    return report_comparison(model, report, action=action)
