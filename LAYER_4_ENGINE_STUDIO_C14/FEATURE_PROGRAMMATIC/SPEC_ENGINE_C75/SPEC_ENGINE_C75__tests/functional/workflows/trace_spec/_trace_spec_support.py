"""Shared trace contract and transition fixtures."""

CONTRACT = (
    "declare_trace_contract(action='admit', "
    "output='ready', must_effect=(('kernel', 'ready'),))"
)


def transition(target, kind, observed=None, outcome=None):
    params = {"kind": kind}
    if observed is not None:
        params["target"] = observed
    if outcome is not None:
        params["outcome"] = outcome
    return {
        "target": target,
        "guard": {"type": "matchesTrace", "params": params},
    }
