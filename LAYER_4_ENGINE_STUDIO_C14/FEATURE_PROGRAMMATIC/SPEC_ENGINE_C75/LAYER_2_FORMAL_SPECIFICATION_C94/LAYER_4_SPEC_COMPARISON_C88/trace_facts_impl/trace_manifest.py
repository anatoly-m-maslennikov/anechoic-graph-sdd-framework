"""Compare trace bindings and manifest obligations."""

from ...LAYER_1_DIAGNOSTICS_C90._package__shared import verdict

from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85.\
    _package__shared import (
    _HTTP_TRACE_BINDING,
    _IN_PROCESS_TRACE_BINDING,
    http_binding,
)  # fmt: skip
from ...LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    _effect,
    _effect_rules,
    lean_string,
    run_lean_json,
)
from .http_spec import manifest_http_binding
from ..top_down__pub import compare_obligations


def _manifest_binding(manifest, contract):
    boundaries = manifest.get("boundaries")
    io = boundaries.get("io") if isinstance(boundaries, dict) else None
    servers = io.get("server") if isinstance(io, dict) else None
    if not isinstance(servers, dict):
        return {}
    server = servers.get(contract["interface"])
    if server is None:
        return {"interface": None}
    if not isinstance(server, dict):
        return {}
    transport = server.get("transport")
    if contract["transport"] == "in_process":
        if "entry" in contract and not isinstance(transport, str):
            return {}
        return {
            "interface": contract["interface"],
            **{
                key: value
                if isinstance(value := server[key], str) and value.strip()
                else None
                for key in ("transport", "entry")
                if key in server
            },
        }
    if not isinstance(transport, str):
        return {}
    if transport != "http":
        return {"interface": contract["interface"], "transport": transport}
    if "routes" not in server:
        return {}
    return {
        "interface": contract["interface"],
        "transport": transport,
        **manifest_http_binding(server["routes"], contract),
    }


def _solution_binding(workflow, binding):
    states = workflow.get("states")
    if not isinstance(states, list):
        return {}
    initial = next(
        (state for state in states if state["name"] == workflow.get("initial")),
        None,
    )
    if initial is None:
        return {}
    transitions = initial["transitions"]
    if len(transitions) != 1:
        return {"interface": None}
    expect = transitions[0]["expect"]
    if expect.get("kind") != "trigger":
        return {"interface": None}
    detail = expect.get("detail")
    if not isinstance(detail, dict):
        return {}
    if not isinstance(expect.get("target"), str):
        return {}
    observed = detail
    if detail.get("transport") == "http":
        try:
            observed = {**detail, **http_binding(detail)}
        except ValueError:
            observed = {"transport": "http"}
    return {
        "interface": expect["target"],
        **{
            key: observed[key]
            for key in binding[1:]
            if isinstance(observed.get(key), str)
        },
    }


def _binding_directions(sources, claims, contract, workflow, lean):
    binding = (
        _IN_PROCESS_TRACE_BINDING
        if contract["transport"] == "in_process"
        else _HTTP_TRACE_BINDING
    )
    public_in_process = (
        contract["transport"] == "in_process" and "entry" not in contract
    )
    public_binding = binding[:2] if public_in_process else binding
    obligations = {
        "manifest": _manifest_binding(claims.get("manifest", {}), contract),
        "contract": {key: contract[key] for key in public_binding},
        "solution": _solution_binding(workflow, binding),
    }
    directions = compare_obligations(sources, obligations, lean=lean)["directions"]
    if public_in_process:
        consistency = directions["manifest_contract"]
        facts = [fact for fact in consistency["facts"] if fact["key"] != "entry"]
        consistency.update(
            facts=facts, status=verdict([fact["status"] for fact in facts])
        )
    return directions


def _trace_cases(contract):
    action = contract.get("action")
    trace = contract.get("trace", contract)
    legacy = {
        "action": action,
        **{key: value for key, value in trace.items() if key != "invariant"},
    }
    cases = contract.get("cases", [legacy] if "output" in trace else [])
    if "invariant" in contract:
        return [*cases, {"action": action, **contract["invariant"]}]
    return cases


def _manifest_contract(cases, contract, lean):
    facts, expressions = _manifest_expressions(cases, contract)
    program = (
        "import Lean\n"
        + _effect_rules()
        + "#eval IO.println (Lean.toJson ["
        + ", ".join(expressions)
        + "]).compress\n"
    )
    statuses = run_lean_json(program, lean)
    if (
        not isinstance(statuses, list)
        or len(statuses) != len(facts)
        or any(
            status not in ("matched", "conflicting", "unresolved")
            for status in statuses
        )
    ):
        raise ValueError("unexpected Lean manifest comparison output")
    for fact, status in zip(facts, statuses):
        fact["status"] = status
    return {"status": verdict(statuses), "facts": facts}


def _manifest_expressions(cases, contract):
    contracts = _trace_cases(contract)
    facts, expressions = [], []
    for case in cases:
        match = next(
            (
                row
                for row in contracts
                if row.get("action") == case["action"]
                and row.get("output") == case["output"]
            ),
            None,
        )
        for key in ("must_effect", "forbid_effect"):
            for value in case.get(key, []):
                facts.append(
                    {
                        "key": key,
                        "left": value,
                        "action": case["action"],
                        "output": case["output"],
                    }
                )
                action_wide = (
                    contract.get("invariant", {}).get(key, ())
                    if case["action"] == contract.get("action")
                    else ()
                )
                expressions.append(_manifest_expression(key, value, match, action_wide))
    return facts, expressions


def _manifest_expression(key, value, match, action_wide):
    if match is None and not action_wide:
        return '"unresolved"'
    modeled = (match or {}).get(key, ())
    if key == "must_effect":
        candidates = ", ".join(_effect(item) for item in modeled)
        condition = (
            f"([{candidates}] : List Effect).any "
            f"(fun actual => implies actual {_effect(value)})"
        )
    else:
        candidates = ", ".join(lean_string(item) for item in (*modeled, *action_wide))
        condition = f"([{candidates}] : List String).contains {lean_string(value)}"
    return f'if {condition} then "matched" else "conflicting"'
