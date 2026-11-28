"""Compare trace Contract obligations with a normalized workflow in Lean."""

from ..LAYER_1_DIAGNOSTICS_C90._package__shared import verdict

from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85.\
    _package__shared import outcome_cases  # fmt: skip
from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    _program,
    run_lean_json,
)
from ..LAYER_3_MERMAID_RENDERER_C87._package__shared import render_solution
from ._direct_comparison import (
    _operation_claims,
    comparison_claims,
    report_comparison,
)
from .trace_facts_impl._package__shared import compare_http_workflow
from .trace_facts_impl._package__shared import trace_claims, workflow_facts
from .trace_facts_impl import _package__shared as _manifest_implementation


def _binding_directions(sources, claims, contract, workflow, lean):
    return _manifest_implementation._binding_directions(
        sources, claims, contract, workflow, lean
    )


def _manifest_binding(manifest, contract):
    return _manifest_implementation._manifest_binding(manifest, contract)


def _manifest_contract(cases, contract, lean):
    return _manifest_implementation._manifest_contract(cases, contract, lean)


def _solution_binding(workflow, binding):
    return _manifest_implementation._solution_binding(workflow, binding)


def _trace_cases(contract):
    return _manifest_implementation._trace_cases(contract)


_UNRENDERED = object()


def compare_trace_workflow(contract, workflow, *, lean="lean"):
    """Compare a parsed trace Contract with a compiled workflow claim."""
    if {"cases", "trace", "invariant"} & contract.keys():
        return _compare_cases(_trace_cases(contract), workflow, lean)
    effects = contract.get("must_effect", [])
    forbidden = contract.get("forbid_effect", [])
    orders = contract.get("must_precede", [])
    count = 2 + len(effects) + len(forbidden) + len(orders)
    has_workflow = all(key in workflow for key in ("action", "initial", "states"))
    statuses = (
        run_lean_json(_program(contract, workflow), lean)
        if has_workflow
        else ["unresolved"] * count
    )
    if (
        not isinstance(statuses, list)
        or len(statuses) != count
        or any(
            status not in ("matched", "conflicting", "unresolved")
            for status in statuses
        )
    ):
        raise ValueError("unexpected Lean trace comparison output")
    return workflow_facts(contract, workflow, statuses)


def _compare_cases(cases, workflow, lean):
    facts, statuses = [], []
    for case in cases:
        result = compare_trace_workflow(case, workflow, lean=lean)
        context = (
            {"scope": "action", "action": case["action"]}
            if "output" not in case
            else {"action": case["action"], "output": case["output"]}
        )
        facts.extend({**fact, **context} for fact in result["facts"])
        statuses.append(result["status"])
    return {"status": verdict(statuses), "facts": facts}


def _merge_direction(directions, key, comparison):
    current = directions[key]
    if current["facts"]:
        current["facts"].extend(comparison["facts"])
        current["status"] = verdict([current["status"], comparison["status"]])
    else:
        directions[key] = comparison


def _add_manifest_outcomes(
    directions, boundaries, contract, workflow, lean, *, action=None
):
    cases, _ = outcome_cases(boundaries)
    if action is not None:
        cases = [case for case in cases if case["action"] == action]
    if cases:
        _merge_direction(
            directions,
            "manifest_contract",
            _manifest_contract(cases, contract, lean),
        )
        _merge_direction(
            directions,
            "manifest_solution",
            _compare_cases(cases, workflow, lean),
        )


def _profile_directions(
    sources, claims, contract_claim, workflow, lean, *, action=None
):
    directions = {
        "manifest_contract": {"status": "unresolved", "facts": []},
        "manifest_solution": {"status": "unresolved", "facts": []},
        "contract_solution": {"status": "unresolved", "facts": []},
    }
    if contract_claim.get("transport") in ("http", "in_process"):
        directions = _binding_directions(
            sources, claims, contract_claim, workflow, lean
        )
    _add_manifest_outcomes(
        directions,
        claims.get("manifest", {}).get("boundaries"),
        contract_claim,
        workflow,
        lean,
        action=action,
    )
    comparison = _compare_cases(_trace_cases(contract_claim), workflow, lean)
    if comparison["facts"]:
        _merge_direction(directions, "contract_solution", comparison)
    if contract_claim.get("profile") == "http":
        _merge_direction(
            directions,
            "contract_solution",
            compare_http_workflow(sources, contract_claim, workflow, lean),
        )
    return directions


def _uncovered_outcomes(boundaries, contract, workflow, selected):
    cases, _ = outcome_cases(boundaries)
    declared = {}
    for case in cases:
        declared.setdefault(case["action"], set()).add(case["output"])
    for action, profile in _operation_claims(contract).items():
        names = declared.setdefault(action, set())
        outcomes = profile.get("cases", [profile, profile.get("trace", {})])
        names.update(case["output"] for case in outcomes if "output" in case)
        if profile.get("profile") == "http":
            names.update(name for name, _, _ in profile["outcomes"])
        if profile.get("transport") == "cli":
            names.update(profile.get("outcomes", {}))
            names.update(profile.get("exit_codes", {}))
            names.update(
                key.removeprefix("stdout.")
                for key in profile
                if key.startswith("stdout.")
            )
    gaps = []
    for action, profile in _operation_claims(workflow).items():
        if not declared.get(action) or (selected is not None and action != selected):
            continue
        states = profile.get("states", ())
        finals = {state["name"] for state in states if state["final"]}
        outputs = {
            edge["expect"]["outcome"]
            for state in states
            for edge in state["transitions"]
            if edge["target"] in finals
            and edge["expect"]["kind"] == "output"
            and (edge["expect"].get("outcome") or "").strip()
        }
        gaps.extend(
            {"action": action, "output": name}
            for name in sorted(outputs - declared[action])
        )
    return gaps


def _operation_directions(sources, claims, contract, workflow, lean):
    boundaries = claims.get("manifest", {}).get("boundaries")
    cases, _ = outcome_cases(boundaries)
    contracts, solutions = (
        _operation_claims(contract),
        _operation_claims(workflow),
    )
    actions = dict.fromkeys(
        (*contracts, *solutions, *(case["action"] for case in cases))
    )
    operations = {
        action: _profile_directions(
            sources,
            claims,
            contracts.get(action, {}),
            solutions.get(action, {}),
            lean,
            action=action,
        )
        for action in actions
    }
    keys = next(iter(operations.values()))
    directions = {}
    for key in keys:
        directions[key] = {
            "status": verdict(
                [report[key]["status"] for report in operations.values()]
            ),
            "facts": [
                {"action": action, **fact}
                for action, report in operations.items()
                for fact in report[key]["facts"]
            ],
        }
    return operations, directions


def check_trace_spec(
    root,
    component_id,
    manifest,
    contract=None,
    solution=None,
    *,
    action=None,
    lean="lean",
):
    """Check the trace Contracts and Solution workflows by declared action."""
    from ..LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model

    from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85.\
        _package__shared import select_formal_claims  # fmt: skip
    from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean

    model = select_formal_claims(
        load_boundary_model(root, component_id, manifest, contract, solution),
        action,
    )
    compiled = compile_lean(model)
    return compare_trace_spec(model, compiled, action=action, lean=lean)


def _trace_claims(model, claims):
    return trace_claims(model, claims, _operation_claims)


def compare_trace_spec(
    model,
    compiled,
    *,
    action=None,
    lean="lean",
    mermaid=_UNRENDERED,
    observe=None,
):
    """Compare a loaded trace chain using its normalized declarations."""
    claims = comparison_claims(compiled, observe, action, "trace")
    if mermaid is _UNRENDERED:
        mermaid = render_solution(model, claims.get("solution"), action=action)
    sources = {
        role: model[role]["source"] for role in ("manifest", "contract", "solution")
    }
    contract_claim, workflow = _trace_claims(model, claims)
    operations, directions = _select_directions(
        sources, claims, contract_claim, workflow, lean, action
    )
    return _trace_report(
        model,
        compiled,
        claims,
        workflow,
        action,
        mermaid,
        sources,
        operations,
        directions,
    )


def _select_directions(sources, claims, contract_claim, workflow, lean, action):
    operations = {}
    if action is not None:
        directions = _profile_directions(
            sources,
            claims,
            _operation_claims(contract_claim).get(action, {}),
            _operation_claims(workflow).get(action, {}),
            lean,
            action=action,
        )
    elif "operations" in contract_claim or "operations" in workflow:
        operations, directions = _operation_directions(
            sources, claims, contract_claim, workflow, lean
        )
    else:
        directions = _profile_directions(
            sources, claims, contract_claim, workflow, lean
        )
    return operations, directions


def _trace_report(
    model,
    compiled,
    claims,
    workflow,
    action,
    mermaid,
    sources,
    operations,
    directions,
):
    statuses = [direction["status"] for direction in directions.values()]
    boundaries = claims.get("manifest", {}).get("boundaries")
    uncovered = _uncovered_outcomes(
        boundaries, claims.get("contract", {}), workflow, action
    )
    if compiled["issues"] or compiled["unresolved"] or uncovered:
        statuses.append("unresolved")
    report = {
        "status": verdict(statuses),
        **({"operations": operations} if operations else {}),
        "sources": sources,
        "directions": directions,
        "issues": compiled["issues"],
        "unresolved": compiled["unresolved"],
        "uncovered_outcomes": uncovered,
        "mermaid": mermaid,
    }
    return report_comparison(model, report, action=action)
