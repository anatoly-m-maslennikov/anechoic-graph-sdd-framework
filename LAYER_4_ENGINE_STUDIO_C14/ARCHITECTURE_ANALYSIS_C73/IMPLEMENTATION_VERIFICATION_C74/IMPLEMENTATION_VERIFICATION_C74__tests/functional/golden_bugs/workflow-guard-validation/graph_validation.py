"""Validate the bounded workflow graph used by the replay analyzer."""

import re


def validate_branch(branch, nodes):
    if (
        not isinstance(branch, dict)
        or set(branch) != {"target", "guard"}
        or not safe(branch["target"])
        or branch["target"] not in nodes
        or not isinstance(branch["guard"], dict)
        or set(branch["guard"]) != {"type", "params"}
        or branch["guard"]["type"] != "matchesTrace"
        or not isinstance(branch["guard"]["params"], dict)
    ):
        raise ValueError("unsupported graph: invalid transition")
    guard = branch["guard"]["params"]
    if set(guard) - {"kind", "target", "outcome", "detail"} or guard.get(
        "kind"
    ) not in ("trigger", "effect", "output"):
        raise ValueError("unsupported graph: invalid guard")
    if any(
        k in guard
        and guard[k] is not None
        and (not isinstance(guard[k], str) or len(guard[k]) > 256)
        for k in ("target", "outcome")
    ):
        raise ValueError("unsupported graph: invalid guard constraint")
    detail = guard.get("detail", {})
    if (
        not isinstance(detail, dict)
        or any(not isinstance(k, str) for k in detail)
        or any(
            v is not None
            and (
                not isinstance(v, (str, bool, int))
                or isinstance(v, int)
                and abs(v) > 2**53 - 1
            )
            for v in detail.values()
        )
    ):
        raise ValueError(
            "unsupported graph: detail constraints must be scalar strings, "
            "safe integers, booleans, or null"
        )
    return branch["guard"]["params"]


def safe(value):
    return (
        isinstance(value, str)
        and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]{0,63}", value)
        and value not in ("__proto__", "constructor", "prototype")
    )


def graph_transitions(nodes, final, transitions):
    for name, node in nodes.items():
        if not isinstance(node, dict):
            raise ValueError("unsupported graph: invalid state")
        if node == {"type": "final"}:
            final.append(name)
            continue
        if set(node) != {"on"} or not isinstance(node["on"], dict):
            raise ValueError("unsupported graph: invalid state")
        for event, branches in node["on"].items():
            if not safe(event):
                raise ValueError("unsupported graph: invalid event")
            branches = branches if isinstance(branches, list) else [branches]
            if not branches:
                raise ValueError("unsupported graph: empty transitions")
            for branch in branches:
                guard = validate_branch(branch, nodes)
                transitions.append(
                    {
                        "source": name,
                        "event": event,
                        "target": branch["target"],
                        "guard": guard,
                    }
                )


def validate_graph(config):
    if (
        not isinstance(config, dict)
        or set(config) != {"id", "initial", "states"}
        or not safe(config["id"])
        or not safe(config["initial"])
        or not isinstance(config["states"], dict)
    ):
        raise ValueError("unsupported graph: invalid config")
    nodes = config["states"]
    states, final, transitions = list(nodes), [], []
    if (
        not 1 <= len(states) <= 100
        or any(not safe(s) for s in states)
        or config["initial"] not in nodes
    ):
        raise ValueError("unsupported graph: invalid states or initial")
    graph_transitions(nodes, final, transitions)
    if not final or len(transitions) > 1000:
        raise ValueError("unsupported graph: final state or transition count")
    reached = {config["initial"]}
    while True:
        expanded = reached | {
            t["target"] for t in transitions if t["source"] in reached
        }
        if expanded == reached:
            break
        reached = expanded
    if len(reached) != len(states):
        raise ValueError(
            "unsupported graph: unreachable states fail compiler admission"
        )
    return {
        "initial": config["initial"],
        "states": states,
        "final": final,
        "transitions": transitions,
    }
