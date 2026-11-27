import ast
from decimal import Decimal
import json
import re


def parse_workflow(source):
    tree = ast.parse(source)
    call = (
        tree.body[0].value
        if len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr)
        else None
    )
    if (
        not isinstance(call, ast.Call)
        or not isinstance(call.func, ast.Name)
        or call.func.id != "component_workflow"
        or call.args
        or {item.arg for item in call.keywords}
        not in (
            {"component", "action", "machine"},
            {"component", "action", "machine", "startup"},
        )
        or len(call.keywords) != len({item.arg for item in call.keywords})
    ):
        raise ValueError(
            "Expected component_workflow(component=..., action=..., machine=..., startup=...)"
        )
    for node in ast.walk(call):
        if isinstance(node, ast.Dict):
            keys = [key.value for key in node.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)]
            if len(keys) != len(node.keys) or len(set(keys)) != len(keys):
                raise ValueError("Workflow objects require unique string keys")
    values = {item.arg: ast.literal_eval(item.value) for item in call.keywords}
    if (not isinstance(values["component"], str) or not re.fullmatch(r"CS?[0-9]+", values["component"])
            or not isinstance(values["action"], str) or not values["action"].strip()
            or not isinstance(values["machine"], dict)):
        raise ValueError("Invalid Component, action, or statechart")
    if "startup" in values:
        startup = values["startup"]
        if not isinstance(startup, dict) or set(startup) != {
            "required_arguments"
        }:
            raise ValueError("startup must contain only required_arguments")
        arguments = startup["required_arguments"]
        if (not isinstance(arguments, list)
                or any(not isinstance(arg, str) or not re.fullmatch(r"--[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", arg)
                       for arg in arguments)
                or len(set(arguments)) != len(arguments)):
            raise ValueError("required_arguments must contain unique CLI option names")
    return values


def _fields(value, allowed, where):
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be an object")
    for key in value:
        if key not in allowed:
            raise ValueError(f"{where}: unsupported field {key}")


def _safe(value, where):
    if (
        not isinstance(value, str)
        or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]{0,63}", value)
        or value in {"__proto__", "constructor", "prototype"}
    ):
        raise ValueError(f"{where}: invalid identifier")


def json_equal(a, b):
    if type(a) in (int, float, Decimal) and type(b) in (int, float, Decimal):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(json_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(json_equal(x, y) for x, y in zip(a, b))
    return a == b


def _overlap(a, b):
    def bound(value):
        if (isinstance(value, dict) and set(value) == {'at_most'}
                and type(value['at_most']) is int and value['at_most'] >= 0):
            return value['at_most']

    def compatible(left, right):
        left_bound, right_bound = bound(left), bound(right)
        if left_bound is not None and right_bound is not None:
            return True
        if right_bound is not None:
            left, right, left_bound = right, left, right_bound
        if left_bound is not None:
            return (type(right) in (int, float) and 0 <= right <= left_bound
                    and (type(right) is int or right.is_integer()))
        return json_equal(left, right)

    details = b.get("detail", {})
    return all(
        k not in a or k not in b or a[k] == b[k]
        for k in ("kind", "target", "outcome")
    ) and all(
        k not in details or compatible(v, details[k])
        for k, v in a.get("detail", {}).items()
    )


def _transition(event, branch, states):
    if isinstance(branch, dict) and ({"to", "expect"} & branch.keys()):
        _fields(branch, {"to", "expect"}, "transition")
        branch = {
            "target": branch.get("to"),
            "guard": {"type": "matchesTrace", "params": branch.get("expect")},
        }
    _fields(branch, {"target", "guard"}, "transition")
    target = branch.get("target")
    _safe(target, "target")
    if target not in states:
        raise ValueError(f"target {target} does not exist")
    guard = branch.get("guard")
    _fields(guard, {"type", "params"}, "guard")
    if guard.get("type") != "matchesTrace":
        raise ValueError("guard must be matchesTrace")
    params = guard.get("params")
    _fields(
        params,
        {"kind", "target", "outcome", "detail", "bind", "same_as"},
        "guard.params",
    )
    if params.get("kind") not in ("trigger", "effect", "output"):
        raise ValueError("invalid trace kind")
    for field in ("target", "outcome"):
        value = params.get(field)
        if value is not None and (
            not isinstance(value, str)
            or len(value.encode("utf-16-le", errors="surrogatepass")) // 2
            > 256
        ):
            raise ValueError(f"{field} must be a string or null")
    if "detail" in params and not isinstance(params["detail"], dict):
        raise ValueError("detail must be an object")
    _validate_binding_fields(params)
    return {"event": event, "target": target, "expect": params}


def _validate_binding_fields(expect):
    for name in ("bind", "same_as"):
        bindings = expect.get(name, {})
        if not isinstance(bindings, dict):
            raise ValueError(f"{name} must be an object")
        for key, value in bindings.items():
            alias, detail = (key, value) if name == "bind" else (value, key)
            _safe(alias, name)
            if not isinstance(detail, str) or not detail:
                raise ValueError(f"{name} requires a nonempty detail key")


def _transitions(name, events, states, remaining):
    if not isinstance(events, dict):
        raise ValueError(f"state {name}.on must be an object")
    transitions = []
    for event, value in events.items():
        _safe(event, "event")
        branches = value if isinstance(value, list) else [value]
        if not branches:
            raise ValueError(f"event {event}: empty transitions")
        if len(transitions) + len(branches) > remaining:
            raise ValueError("too many transitions")
        alternatives = []
        for branch in branches:
            transition = _transition(event, branch, states)
            for prior in alternatives:
                if _overlap(prior["expect"], transition["expect"]):
                    raise ValueError(
                        f"state {name}, event {event}: overlapping guards for targets "
                        f"{prior['target']} and {transition['target']}"
                    )
            alternatives.append(transition)
        transitions.extend(alternatives)
    return transitions


def _normalize_states(source):
    states = []
    remaining = 1000
    for name, state in source.items():
        _safe(name, "state")
        _fields(state, {"type", "on"}, f"state {name}")
        final = state.get("type") == "final"
        if final and "on" in state:
            raise ValueError(f"final state {name} cannot have transitions")
        if not final and "type" in state:
            raise ValueError(f"state {name}: unsupported type")
        transitions = (
            []
            if final
            else _transitions(name, state.get("on"), source, remaining)
        )
        remaining -= len(transitions)
        states.append(
            {"name": name, "final": final, "transitions": transitions}
        )
    return states


def normalize_workflow(config):
    encoded = json.dumps(config, allow_nan=False)
    if len(encoded) > 1_000_000:
        raise ValueError("input exceeds 1 MB")
    config = json.loads(encoded)
    _fields(config, {"id", "initial", "states"}, "config")
    _safe(config.get("id"), "id")
    _safe(config.get("initial"), "initial")
    source = config.get("states")
    if not isinstance(source, dict):
        raise ValueError("states must be an object")
    if not 1 <= len(source) <= 100:
        raise ValueError("states must contain 1 to 100 states")
    if config["initial"] not in source:
        raise ValueError("initial state does not exist")
    states = _normalize_states(source)
    if not any(state["final"] for state in states):
        raise ValueError("at least one final state is required")
    _validate_graph(config, source, states)
    return {"initial": config["initial"], "states": states}


def _validate_graph(config, source, states):
    by_name = {state["name"]: state for state in states}
    reached = {config["initial"]}
    queue = [config["initial"]]
    for name in queue:
        for transition in by_name[name]["transitions"]:
            target = transition["target"]
            if target not in reached:
                reached.add(target)
                queue.append(target)
    missing = [name for name in source if name not in reached]
    if missing:
        raise ValueError(f"unreachable states: {', '.join(missing)}")
    can_finish = {state["name"] for state in states if state["final"]}
    while True:
        expanded = can_finish | {
            state["name"]
            for state in states
            if any(t["target"] in can_finish for t in state["transitions"])
        }
        if expanded == can_finish:
            break
        can_finish = expanded
    dead = [name for name in source if name not in can_finish]
    if dead:
        raise ValueError(
            f"states with no path to a final state: {', '.join(dead)}"
        )
    _validate_references(config["initial"], by_name)


def _validate_references(initial, states):
    if not any(
        t["expect"].get("same_as")
        for state in states.values()
        for t in state["transitions"]
    ):
        return
    bound = {initial: set()}
    pending = [initial]
    while pending:
        name = pending.pop()
        for transition in states[name]["transitions"]:
            expect, target = transition["expect"], transition["target"]
            incoming = bound[name] | expect.get("bind", {}).keys()
            guaranteed = (
                incoming & bound[target] if target in bound else incoming
            )
            if guaranteed != bound.get(target):
                bound[target] = guaranteed
                pending.append(target)
    for name, state in states.items():
        for transition in state["transitions"]:
            refs = set(transition["expect"].get("same_as", {}).values())
            if missing := sorted(refs - bound[name]):
                raise ValueError(
                    f"state {name}, event {transition['event']}: binding {missing[0]!r} "
                    "must be set on every path by an earlier event"
                )
