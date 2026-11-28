"""Compare a delegated outcome with the provider's pinned Specs."""

from ...LAYER_2_SPEC_READING_C83._package__shared import (
    load_boundary_model,
    load_formal_claim,
)

# fmt: off
from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared \
    import (normalize_claim, select_formal_claims)
# fmt: on
from ...LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from .._package__shared import compare_delegation
from .manifest_delegation import (
    compare_manifest_call,
    load_manifest_call,
)

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.atom_reference__pub \
    import derive_atom_ref
# fmt: on
from .sibling_delegation__pub import (
    _load_sibling_caller,
    _offered_bindings,
    _require_sibling,
)
from .trace_offerings import (
    _declared_outcome as _declared_outcome,
    _manifest_outcome,
    _offerings,
)
from .trace_requirement import _requirement


def _add_outcome_binding(provider, compiled, required, obligations):
    if "transport" not in required:
        return False
    fields = tuple(
        key
        for key in (
            "interface",
            "transport",
            "entry",
            "endpoint",
            "route_name",
        )
        if key in required
    )
    binding = _offered_bindings(
        compiled["claims"], required, fields, required["action"]
    )
    for role, facts in binding.items():
        obligations[role].update(
            {key: facts[key] for key in fields if key in facts}
        )
    private_fields = (
        {key for key in fields if key not in binding["contract"]}
        if provider.get("embedded_contract")
        else set()
    )
    obligations["contract"].update(
        {key: required[key] for key in private_fields}
    )
    return private_fields


def _check_outcome(
    caller,
    caller_id,
    caller_issues,
    provider,
    *,
    event,
    lean,
    interface=None,
    caller_action=None,
):
    workflow, error = normalize_claim("solution", caller, caller_id)
    required = _requirement(
        workflow or {},
        event,
        interface,
        caller_action=caller_action,
        manifest_pin=True,
        sibling=interface is not None,
    )
    selected_provider = (
        select_formal_claims(provider, required["action"])
        if required.get("action")
        else provider
    )
    compiled = compile_lean(selected_provider)
    sources, obligations, private_fields = _outcome_obligations(
        caller, provider, compiled, required, lean, interface
    )
    diagnostics = caller_issues or ([error] if error else [])
    if not required and not diagnostics:
        diagnostics = [
            "The selected effect has no complete provider action "
            "and output binding"
        ]
    report = compare_delegation(sources, obligations, lean=lean)
    return _outcome_result(
        report, private_fields, compiled, caller, diagnostics, event
    )


def _outcome_obligations(
    caller, provider, compiled, required, lean, interface
):
    sources = {
        "caller": caller["source"],
        **{
            role: provider[role]["source"]
            for role in ("manifest", "contract", "solution")
        },
    }
    obligations = {
        role: {"component": provider["component_id"], **(facts or {})}
        for role, facts in _offerings(
            compiled, provider, required, lean, interface
        ).items()
    }
    if "manifest" in required:
        source = provider["manifest"]["source"]
        ref = derive_atom_ref(
            source["atom_id"], source["version"], source["status"]
        )
        for facts in obligations.values():
            facts["manifest"] = ref
    private_fields = interface is not None and _add_outcome_binding(
        provider, compiled, required, obligations
    )
    obligations["caller"] = required
    return sources, obligations, private_fields


def _outcome_result(
    report, private_fields, compiled, caller, diagnostics, event
):
    if private_fields:
        facts = report["directions"]["caller_contract"]["facts"]
        report["directions"]["caller_contract"]["facts"] = [
            fact for fact in facts if fact["key"] not in private_fields
        ]
    unresolved = []
    unresolved.extend(compiled["unresolved"])
    for issue in diagnostics:
        diagnostic = {
            "source": caller["source"],
            "field": "solution",
            "message": issue,
        }
        unresolved.append(diagnostic)
    return {
        **report,
        "event": event,
        "issues": compiled["issues"],
        "unresolved": unresolved,
        "unmodeled": ["Call arguments and exact returned values"],
    }


def _check_manifest_outcome(
    root,
    parent_manifest,
    parent_solution,
    child_id,
    pin,
    *,
    event,
    caller_action,
    lean,
):
    caller, workflow, child, contract, issues, unresolved = load_manifest_call(
        root, parent_manifest, parent_solution, child_id, pin
    )
    required = _requirement(
        workflow, event, caller_action=caller_action, manifest=True
    )
    offered = (
        _manifest_outcome(child, contract, required, lean)
        if not issues
        else {}
    )
    report = compare_manifest_call(
        caller, child, required, offered, issues, unresolved, lean=lean
    )
    return {
        **report,
        "event": event,
        "unmodeled": ["Exact call argument and return values"],
    }


def check_child_outcome(
    root,
    parent_solution,
    child_id,
    child_pins,
    *,
    event,
    parent_manifest=None,
    caller_action=None,
    lean="lean",
):
    """Check the child outcome guarantees the effect the parent relies on."""
    if parent_manifest is not None:
        return _check_manifest_outcome(
            root,
            parent_manifest,
            parent_solution,
            child_id,
            child_pins,
            event=event,
            caller_action=caller_action,
            lean=lean,
        )
    if isinstance(child_pins, dict):
        raise TypeError(
            "A black-box child call requires the caller Manifest pin"
        )
    parent_id = parent_solution["container_component"]
    _, caller, caller_issues = load_formal_claim(
        root, parent_id, "solution", parent_solution
    )
    child = load_boundary_model(root, child_id, *child_pins)
    _require_child(child, child_id, parent_id)
    return _check_outcome(
        caller,
        parent_id,
        caller_issues,
        child,
        event=event,
        lean=lean,
        caller_action=caller_action,
    )


def check_sibling_outcome(
    root,
    caller_pins,
    provider_id,
    provider_pins,
    *,
    event,
    interface,
    caller_action=None,
    lean="lean",
):
    """Check the required outcome of a declared sibling client."""
    caller = _load_sibling_caller(root, caller_pins)
    caller_id = caller["component_id"]
    provider = load_boundary_model(root, provider_id, *provider_pins)
    workflow, _ = normalize_claim("solution", caller["solution"], caller_id)
    required = _requirement(
        workflow or {}, event, caller_action=caller_action, sibling=True
    )
    route = {
        key: required[key]
        for key in ("endpoint", "route_name")
        if key in required
    } or None
    _require_sibling(
        caller, provider, interface, route, transport=required.get("transport")
    )
    _require_server(provider, provider_id, interface)
    issues = [
        issue for issue in caller["issues"] if issue.startswith("solution:")
    ]
    report = _check_outcome(
        caller["solution"],
        caller_id,
        issues,
        provider,
        event=event,
        lean=lean,
        interface=interface,
        caller_action=caller_action,
    )
    return {**report, "declared_client": caller["manifest"]["source"]}


def _require_child(child, child_id, parent_id):
    if (
        child["manifest"]["source"]["container_component"] != parent_id
        or child_id == parent_id
    ):
        raise ValueError(f"{child_id} is not a declared child of {parent_id}")


def _require_server(provider, provider_id, interface):
    boundaries = provider["manifest"]["boundaries"]
    io = boundaries.get("io") if isinstance(boundaries, dict) else None
    servers = io.get("server") if isinstance(io, dict) else None
    if not isinstance(servers, dict) or interface not in servers:
        raise ValueError(f"{provider_id} does not declare server {interface}")
