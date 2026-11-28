"""Build provider outcome claims for delegation comparisons."""

# fmt: off
from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared \
    import (outcome_cases)
# fmt: on
from .._package__shared import (
    _manifest_binding,
    _manifest_contract,
    _operation_claims,
    compare_trace_workflow,
)
from .trace_requirement import _CALL_BINDING


def _declared_outcome(cases, required, lean="lean"):
    for case in cases:
        if (
            case.get("action") != required["action"]
            or case.get("output") != required["output"]
        ):
            continue
        facts = {"action": case["action"], "output": case["output"]}
        if any(
            tuple(effect[:2]) == tuple(required["effect"][:2])
            for effect in case.get("must_effect", ())
        ):
            if (
                len(required["effect"]) == 2
                or _manifest_contract(
                    [{**facts, "must_effect": [required["effect"]]}],
                    case,
                    lean,
                )["status"]
                == "matched"
            ):
                facts["effect"] = required["effect"]
            else:
                facts["effect"] = None
        elif required["effect"][0] in case.get("forbid_effect", ()):
            facts["effect"] = "forbidden"
        return facts
    return {}


def _modeled_outcome(workflow, required, lean):
    if "states" not in workflow:
        return {}
    trace = {
        "action": required["action"],
        "output": required["output"],
        "must_effect": [required["effect"]],
    }
    proof = compare_trace_workflow(trace, workflow, lean=lean)
    (effect,) = (
        fact for fact in proof["facts"] if fact["key"] == "must_effect"
    )
    facts = {"action": workflow["action"]}
    if effect["status"] != "unresolved":
        facts.update(
            output=required["output"],
            effect=required["effect"]
            if effect["status"] == "matched"
            else None,
        )
    return facts


def _require_provider_interface(contract, workflow, interface):
    declared = contract.get("interface")
    if declared is not None and declared != interface:
        raise ValueError(
            f"The provider Contract does not use interface {interface}"
        )
    bound = declared == interface
    initial = next(
        (
            state
            for state in workflow.get("states", ())
            if state["name"] == workflow.get("initial")
        ),
        None,
    )
    for row in initial.get("transitions", ()) if initial else ():
        expect = row["expect"]
        detail = expect.get("detail", {})
        if (
            expect.get("kind") == "trigger"
            and isinstance(expect.get("target"), str)
            and (
                declared is not None
                or detail.get("transport") in ("in_process", "http", "cli")
            )
        ):
            if expect["target"] != interface:
                raise ValueError(
                    f"The provider Solution does not use interface {interface}"
                )
            bound = True
    return bound


def _offerings(compiled, child, required, lean, interface=None):
    if not required:
        return dict.fromkeys(("manifest", "contract", "solution"))
    claims = compiled["claims"]
    cases, _ = outcome_cases(claims.get("manifest", {}).get("boundaries"))
    contract, workflow = (
        claims.get(role, {}) for role in ("contract", "solution")
    )
    if "operations" in contract:
        contract = contract["operations"].get(required["action"], {})
    if "operations" in workflow:
        workflow = workflow["operations"].get(required["action"], {})
    if interface is not None:
        bound = _require_provider_interface(contract, workflow, interface)
        if required["action"] != interface and not bound:
            return dict.fromkeys(("manifest", "contract", "solution"), {})
    if (
        contract.get("transport") != "cli"
        and contract.get("profile") != "http"
        and not any(
            language == "python trace"
            for language, _ in child["contract"]["claims"]
        )
    ):
        contract = {}
    trace = (
        {"action": contract.get("action"), **contract["trace"]}
        if "trace" in contract
        else contract
    )
    offered = _declared_outcome(contract.get("cases", [trace]), required, lean)
    if contract.get("action") == required["action"] and required["effect"][
        0
    ] in contract.get("invariant", {}).get("forbid_effect", ()):
        offered.update(action=required["action"], effect="forbidden")
    manifest = _declared_outcome(cases, required, lean)
    if not cases and child.get("embedded_contract"):
        manifest = offered
    return {
        "manifest": manifest,
        "contract": offered,
        "solution": _modeled_outcome(workflow, required, lean),
    }


def _manifest_outcome(child, contract, required, lean):
    offered = {"component": child["fields"]["component_id"]}
    if not required:
        return offered
    profile = _operation_claims(contract).get(required["action"], {})
    trace = (
        {"action": required["action"], **profile["trace"]}
        if "trace" in profile
        else profile
    )
    offered.update(
        _declared_outcome(profile.get("cases", [trace]), required, lean)
    )
    if required["effect"][0] in profile.get("invariant", {}).get(
        "forbid_effect", ()
    ):
        offered["effect"] = "forbidden"
    binding = {key: profile[key] for key in _CALL_BINDING & profile.keys()}
    request_fields = dict(profile.get("facts", ())).get("input_format.fields")
    if request_fields is not None:
        binding["request_fields"] = request_fields
    if profile.get("transport") in ("http", "in_process"):
        for key, value in _manifest_binding(child, profile).items():
            if key in binding and value != binding[key]:
                binding[key] = {"boundary": value, "contract": binding[key]}
    for key in binding:
        required.setdefault(key, None)
    return {**offered, **binding}
