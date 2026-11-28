"""Project the declared HTTP Tool API behavior onto comparable obligations."""

from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared \
    import http_routes  # fmt: skip

from ..tool_response.facts__shared import (
    _delivery_coverage,
    _derived,
    _error_facts,
    _outcome_facts,
    _record,
    _response_coverage,
    _terminal_facts,
)


def manifest_tool_api(api):
    """Return modeled invocation fields and remaining declarations."""
    observed = {}
    routes = http_routes(api["routes"]) if "routes" in api else {}
    invoke = next(
        (route for route, name in routes.items() if name == "invoke"), None
    )
    if invoke is not None:
        observed["operation"] = [invoke]
    if isinstance(api.get("transport"), str):
        observed["interface.protocol"] = [api["transport"]]
    if isinstance(api.get("socket"), str):
        observed["interface.transport"] = [
            "unix_socket"
            if api["socket"] == "private Unix socket"
            else api["socket"]
        ]
    for key, name in (
        ("input_format.fields", "request_fields"),
        ("error_handling.error_fields", "failure_fields"),
    ):
        value = api.get(name)
        if isinstance(value, list) and all(
            isinstance(item, str) for item in value
        ):
            if len(value) != len(set(value)):
                raise ValueError("duplicate Manifest " + name)
            observed[key] = sorted(value)
    extra = _manifest_extra(api, routes)
    return observed, extra


def _manifest_extra(api, routes):
    extra = {
        key: value
        for key, value in api.items()
        if key
        not in {
            "transport",
            "socket",
            "routes",
            "request_fields",
            "failure_fields",
        }
    }
    extra.update(
        {
            "routes." + (name or route): route
            for route, name in routes.items()
            if name != "invoke"
        }
    )
    return extra


def contract_tool_api(claim):
    """Project the Contract operation, public facts and response outcomes."""
    return {
        "operation": [claim["operation"]],
        **dict(claim["facts"]),
        **{
            f"outcomes.{name}": [code, envelope]
            for name, code, envelope in claim["outcomes"]
        },
    }


def _request_facts(detail):
    facts = {}
    for key, field in (
        ("operation", "operation"),
        ("interface.protocol", "protocol"),
        ("interface.transport", "transport"),
        ("interface.request_format", "request_format"),
    ):
        if isinstance(value := detail.get(field), str):
            facts[key] = [value]
    if isinstance(fields := detail.get("request_fields"), list) and all(
        isinstance(field, str) for field in fields
    ):
        facts["input_format.fields"] = sorted(fields)
    return facts


def _branch_coverage(facts, branches, expected):
    observed = {}
    for branch in branches:
        for key, value in branch.items():
            observed.setdefault(key, []).append(value)
    for key, rows in observed.items():
        distinct = []
        for value in rows:
            if value not in distinct:
                distinct.append(value)
        value = rows[0]
        mismatch = (
            expected is not None and key in expected and value != expected[key]
        )
        if len(distinct) > 1:
            facts[key] = {"conflicting_values": distinct}
        elif mismatch or len(rows) == len(branches):
            facts[key] = value


def _effect_facts(detail):
    facts = {}
    types = detail.get("input_types")
    if isinstance(types, dict):
        for name in ("name", "arguments"):
            if isinstance(types.get(name), str):
                _record(facts, "input_format." + name, [types[name]])
        nullable = types.get("nullable_strings")
        if isinstance(nullable, list) and all(
            isinstance(item, str) for item in nullable
        ):
            _record(facts, "input_format.nullable_strings", sorted(nullable))
    _derived(
        facts,
        "preconditions.project_binding",
        detail,
        {"matches_admitted_instance": True},
        "matching_instance",
    )
    _derived(
        facts,
        "preconditions.tool",
        detail,
        {"tool_enabled": True, "tool_in_registry": True},
        "enabled_and_in_registry",
    )
    return facts


def _query_facts(claim):
    expected = {
        "statement_count": 1,
        "read_only": True,
        "cursor_metadata_only": True,
        "uses_full_submitted_sql": True,
        "uses_selected_project": True,
    }
    states = {state["name"]: state for state in claim["states"]}
    pending, visited, successes = (
        [(claim["initial"], False, True, ())],
        set(),
        [],
    )
    while pending:
        state = pending.pop()
        if state in visited:
            continue
        visited.add(state)
        for transition in states[state[0]]["transitions"]:
            next_state, success = _query_step(
                state, transition, states, expected
            )
            if success is not None:
                successes.append(success)
            pending.append(next_state)
    conflict = next((value for _, value in successes if value), ())
    if conflict:
        return {"guarantees.query": [dict(conflict)]}
    if successes and all(covered for covered, _ in successes):
        return {"guarantees.query": ["one_complete_read_only_statement"]}
    return {}


def _query_step(state, transition, states, expected):
    _, observed, complete, conflict = state
    expect = transition["expect"]
    detail = expect.get("detail", {})
    observation = ()
    query = (
        expect["kind"] == "effect"
        and expect.get("target") == "C59"
        and expect.get("outcome") == "succeeded"
    )
    if query and isinstance(sql := detail.get("sql"), dict):
        observation = tuple(
            (key, sql[key])
            for key, value in expected.items()
            if key in sql and type(sql[key]) is type(value)
        )
    mismatch = observation and any(
        value != expected[key] for key, value in observation
    )
    next_conflict = conflict or (observation if mismatch else ())
    next_observed = observed or query
    next_complete = complete and (
        not query
        or (detail.get("operation") == "run" and dict(observation) == expected)
    )
    target = transition["target"]
    if (
        states[target]["final"]
        and expect["kind"] == "output"
        and expect.get("outcome") == "succeeded"
    ):
        success = (next_observed and next_complete, next_conflict)
    else:
        success = None
    return (target, next_observed, next_complete, next_conflict), success


def _dispatched_states(claim):
    states = {state["name"]: state for state in claim["states"]}
    pending, visited = [(claim["initial"], False)], set()
    while pending:
        name, dispatched = pending.pop()
        if (name, dispatched) in visited:
            continue
        visited.add((name, dispatched))
        for transition in states[name]["transitions"]:
            expect = transition["expect"]
            is_dispatch = (
                expect["kind"] == "effect" and expect.get("target") == "C59"
            )
            pending.append((transition["target"], dispatched or is_dispatch))
    return {name for name, _ in visited}, {
        name for name, dispatched in visited if dispatched
    }


def _solution_branches(claim, facts, errors, outcomes):
    requests, effects, responses = [], [], []
    reachable, dispatched_states = _dispatched_states(claim)
    finals = {state["name"] for state in claim["states"] if state["final"]}
    for state in claim["states"]:
        if state["name"] not in reachable:
            continue
        for transition in state["transitions"]:
            expect = transition["expect"]
            detail = expect.get("detail", {})
            if state["name"] == claim["initial"]:
                requests.append(
                    _request_facts(detail)
                    if expect["kind"] == "trigger"
                    else {}
                )
            if (
                expect["kind"] == "effect"
                and expect.get("target") == "C59"
                and expect.get("outcome") == "succeeded"
            ):
                effects.append(_effect_facts(detail))
            if transition["target"] not in finals:
                continue
            if expect["kind"] == "output":
                detail = _terminal_facts(
                    facts,
                    errors,
                    outcomes,
                    detail,
                    expect.get("outcome"),
                    state["name"] in dispatched_states,
                )
                if expect.get("outcome") in ("succeeded", "failed"):
                    responses.append((detail, expect["outcome"]))
            else:
                facts["_unclassified_terminal"] = True
    return requests, effects, responses


def solution_tool_api(claim, expected=None):
    """Read explicit HTTP observations on a validated Solution workflow."""
    facts, errors, outcomes = _query_facts(claim), {}, {}
    startup = claim.get("startup", {})
    required = (
        startup.get("required_arguments")
        if isinstance(startup, dict)
        else None
    )
    if isinstance(required, list) and all(
        isinstance(item, str) for item in required
    ):
        _record(facts, "interface.cli_required", sorted(required))
    requests, effects, responses = _solution_branches(
        claim, facts, errors, outcomes
    )
    _branch_coverage(facts, requests, expected)
    _branch_coverage(facts, effects, expected)
    _outcome_facts(facts, outcomes, expected)
    _error_facts(facts, errors, expected)
    _response_coverage(facts, responses, expected)
    _delivery_coverage(facts, responses, expected)
    return facts
