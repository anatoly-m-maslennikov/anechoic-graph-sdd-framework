"""Build trace comparison facts."""

from ...LAYER_1_DIAGNOSTICS_C90._package__shared import verdict


def workflow_facts(contract, workflow, statuses):
    effects = contract.get("must_effect", [])
    forbidden = contract.get("forbid_effect", [])
    orders = contract.get("must_precede", [])
    facts = [
        {
            "key": "action",
            "left": contract["action"],
            "right": workflow.get("action"),
            "status": statuses[0],
        }
    ]
    facts.extend(
        {"key": "must_effect", "left": effect, "status": status}
        for effect, status in zip(effects, statuses[1 : 1 + len(effects)])
    )
    facts.extend(
        {"key": "forbid_effect", "left": target, "status": status}
        for target, status in zip(
            forbidden,
            statuses[1 + len(effects) : 1 + len(effects) + len(forbidden)],
        )
    )
    facts.extend(
        {"key": "must_precede", "left": order, "status": status}
        for order, status in zip(
            orders, statuses[1 + len(effects) + len(forbidden) : -1]
        )
    )
    facts.append({"key": "terminal_output", "status": statuses[-1]})
    facts.extend(_value_facts(contract))
    performance = _performance_facts(contract)
    return {
        "status": verdict([fact["status"] for fact in facts + performance]),
        "facts": facts + performance,
    }


def _value_facts(contract):
    facts = []
    facts.extend(
        {
            "key": "same_values",
            "left": left,
            "right": right,
            "status": "unresolved",
        }
        for left, right in contract.get("same_values", [])
    )
    facts.extend(
        {
            "key": "value_types",
            "field": field,
            "expected": kind,
            "status": "unresolved",
        }
        for field, kind in contract.get("value_types", [])
    )
    return facts


def _performance_facts(contract):
    performance = contract.get("performance", {})
    return [
        {
            "key": "performance",
            "name": name,
            "left": value,
            "action": contract["action"],
            "output": contract["output"],
            "resources": performance["resources"],
            "status": "unresolved",
        }
        for name, value in performance.get("measurements", {}).items()
    ]


def trace_claims(model, claims, operation_claims):
    contract, workflow = claims.get("contract", {}), claims.get("solution", {})
    has_trace = any(
        language == "python trace" for language, _ in model["contract"]["claims"]
    )
    profiles = operation_claims(contract)
    supported = {
        action: profile
        for action, profile in profiles.items()
        if profile.get("profile") == "http"
        or (has_trace and profile.get("transport") != "cli" and "facts" not in profile)
    }
    if "operations" not in contract:
        return next(iter(supported.values()), {}), workflow
    if "operations" in workflow:
        specialized = profiles.keys() - supported.keys()
        remaining = {
            action: value
            for action, value in workflow["operations"].items()
            if action not in specialized
        }
        workflow = {"operations": remaining} if remaining else {}
    return {"operations": supported} if supported else {}, workflow
