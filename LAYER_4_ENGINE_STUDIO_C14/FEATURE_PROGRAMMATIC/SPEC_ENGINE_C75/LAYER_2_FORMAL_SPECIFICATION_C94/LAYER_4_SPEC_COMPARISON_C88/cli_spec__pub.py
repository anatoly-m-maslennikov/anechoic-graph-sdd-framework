"""Compare a pinned CLI declaration, public Contract and Solution workflow."""

from ..LAYER_1_DIAGNOSTICS_C90._package__shared import verdict
from ..LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model
from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85.\
    _package__shared import select_formal_claims  # fmt: skip
from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from ..LAYER_3_MERMAID_RENDERER_C87._package__shared import render_solution
from .cli_selection import _cli_profiles, _initial_trigger, _manifest_endpoint
from .cli_facts._package__shared import (
    _common_checks,
    _first_dispatch,
    _query_checks,
    _reachable_without,
    _release_checks,
    _solution_outcomes,
    _success_outputs,
)
from .cli_facts._package__shared import _BINDING_FIELDS, _manifest_facts
from ._direct_comparison import comparison_claims, report_comparison
from .top_down__pub import compare_obligations
from .trace_spec__pub import (
    _add_manifest_outcomes,
    _compare_cases,
    _trace_cases,
    _uncovered_outcomes,
)

_UNRENDERED = object()


def _solution_binding(claim, terminals):
    trigger = _initial_trigger(claim)
    if trigger is None or not terminals:
        return {}
    bypass = _reachable_without(claim, trigger)
    if any(name in bypass for name, _ in terminals):
        return {}
    expected = trigger["expect"]
    detail = expected.get("detail", {})
    return {
        "interface": expected.get("target"),
        **{key: detail[key] for key in _BINDING_FIELDS if key in detail},
    }


def _dispatch_facts(workflow, *, detail_fields=()):
    trigger = _initial_trigger(workflow)
    if trigger is None:
        return {}
    states = {state["name"]: state for state in workflow["states"]}
    routes, generic = {}, []
    for edge in states[trigger["target"]]["transitions"]:
        expect = edge["expect"]
        if expect["kind"] != "trigger":
            return {}
        detail = expect.get("detail", {})
        command = detail.get("command")
        if isinstance(command, str):
            routes.setdefault(command, []).append(edge["target"])
        elif "command" not in detail:
            generic.append(edge["target"])
    if not routes:
        return {}
    return {
        "subcommands": {
            command: _first_dispatch(states, starts + generic, detail_fields)
            for command, starts in routes.items()
        }
    }


def _outcome_stdout(terminals):
    expected = [edge["expect"] for _, edge in terminals]
    outcomes = {
        event.get("outcome")
        for event in expected
        if event["kind"] == "output"
        and isinstance(event.get("outcome"), str)
        and event["outcome"].strip()
    }
    facts = {}
    for outcome in outcomes:
        events = [
            event
            for event in expected
            if event["kind"] != "output" or event.get("outcome") in (outcome, None)
        ]
        values = [event.get("detail", {}).get("stdout") for event in events]
        if all(
            event["kind"] == "output" and event.get("outcome") == outcome
            for event in events
        ) and all(isinstance(value, str) and value.strip() for value in values):
            facts[f"stdout.{outcome}"] = values[0] if len(set(values)) == 1 else values
    return facts


def _terminal_stdout(terminals):
    terminal_details = [
        edge["expect"].get("detail", {}) if edge["expect"]["kind"] == "output" else {}
        for _, edge in terminals
    ]
    values = [detail.get("stdout") for detail in terminal_details]
    stdout = (
        {"stdout": values[0] if all(value == values[0] for value in values) else values}
        if values and all(isinstance(value, str) and value.strip() for value in values)
        else {}
    )
    return stdout


def _workflow_facts(workflow, component_id, *, contract=None):
    if "states" not in workflow:
        return {}
    edges = [
        (state["name"], transition)
        for state in workflow["states"]
        for transition in state["transitions"]
    ]
    finals = {state["name"] for state in workflow["states"] if state["final"]}
    terminals = [row for row in edges if row[1]["target"] in finals]
    successes = _success_outputs(terminals)
    output = _common_checks(
        [detail for _, detail in successes],
        (
            ("encoding", "output_format.encoding", str),
            ("output_fields", "output_fields", list),
            ("record_properties", "output_format.record_properties", list),
            ("record_role", "output_format.record_role", str),
        ),
    )
    stdout = _terminal_stdout(terminals)
    return {
        "action": workflow["action"],
        **_solution_binding(workflow, terminals),
        **stdout,
        **_solution_outcomes(workflow, contract or {}),
        **_outcome_stdout(terminals),
        **output,
        **_query_checks(workflow, edges, successes, component_id),
        **_release_checks(workflow, edges),
        **_dispatch_facts(workflow),
    }


def _add_trace(report, contract, workflow, lean):
    direction = report["directions"]["contract_solution"]
    comparison = _compare_cases(_trace_cases(contract), workflow, lean)
    direction["facts"].extend(
        fact for fact in comparison["facts"] if fact["key"] != "action"
    )
    direction["status"] = verdict([fact["status"] for fact in direction["facts"]])


def check_cli_spec(
    root,
    component_id,
    manifest,
    contract=None,
    solution=None,
    *,
    interface,
    action=None,
    lean="lean",
):
    """Check the selected CLI binding and supported workflow obligations."""
    model = select_formal_claims(
        load_boundary_model(root, component_id, manifest, contract, solution),
        action,
    )
    return compare_cli_spec(
        model,
        compile_lean(model),
        interface=interface,
        action=action,
        lean=lean,
    )


def _finish_report(
    report,
    claims,
    compiled,
    contract_claim,
    workflow,
    endpoint,
    interface,
    lean,
    mermaid,
):
    _add_trace(report, contract_claim, workflow, lean)
    _add_manifest_outcomes(
        report["directions"],
        {"io": {"server": {interface: endpoint}}},
        contract_claim,
        workflow,
        lean,
    )
    report["status"] = verdict(
        [item["status"] for item in report["directions"].values()]
    )
    uncovered = _uncovered_outcomes(
        claims.get("manifest", {}).get("boundaries"),
        contract_claim,
        workflow,
        contract_claim.get("action"),
    )
    report.update(
        issues=compiled["issues"],
        unresolved=compiled["unresolved"],
        uncovered_outcomes=uncovered,
        mermaid=mermaid,
    )
    if report["status"] == "matched" and (
        report["issues"] or report["unresolved"] or uncovered
    ):
        report["status"] = "unresolved"


def _compare_cli_facts(sources, declared, contract_facts, solution_facts, lean):
    report = compare_obligations(
        sources,
        {
            "manifest": declared,
            "contract": contract_facts,
            "solution": solution_facts,
        },
        lean=lean,
    )
    return report


def compare_cli_spec(
    model,
    compiled,
    *,
    interface,
    action=None,
    lean="lean",
    mermaid=_UNRENDERED,
    observe=None,
):
    claims = comparison_claims(compiled, observe, action, "cli")
    sources = {
        role: model[role]["source"] for role in ("manifest", "contract", "solution")
    }
    endpoint = _manifest_endpoint(claims.get("manifest", {}), interface)
    declared = _manifest_facts(endpoint, interface)
    contract_claim, workflow = _cli_profiles(claims, interface, action=action)
    contract_facts = {
        key: value
        for key, value in contract_claim.items()
        if key not in ("trace", "cases", "invariant")
    }
    if mermaid is _UNRENDERED:
        mermaid = render_solution(
            model, claims.get("solution"), action=contract_claim.get("action")
        )
    solution_facts = _workflow_facts(
        workflow, model["component_id"], contract=contract_facts
    )
    report = _compare_cli_facts(sources, declared, contract_facts, solution_facts, lean)
    _finish_report(
        report,
        claims,
        compiled,
        contract_claim,
        workflow,
        endpoint,
        interface,
        lean,
        mermaid,
    )
    return report_comparison(model, report, action=action)
