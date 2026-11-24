"""Render a Component Solution or check one recorded flow against it."""

import argparse
import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import formal_claim_fences

_HERE = Path(__file__).resolve().parent
_OBSERVABLE = {"trigger", "effect", "output"}
_EVENT_FIELDS = ("kind", "name", "target", "outcome", "detail")
_TRACE_FIELDS = {"run_id", "component", "action", "sequence", *_EVENT_FIELDS}


def load_workflow(path):
    fences = list(formal_claim_fences(path.read_text(encoding="utf-8")))
    if len(fences) != 1 or fences[0][0] != "python":
        raise ValueError("Expected one Python Formal Claim")
    tree = ast.parse(fences[0][1])
    call = tree.body[0].value if len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr) else None
    if (not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name)
            or call.func.id != "component_workflow" or call.args
            or len(call.keywords) != 3 or {item.arg for item in call.keywords} != {"component", "action", "machine"}):
        raise ValueError("Expected component_workflow(component=..., action=..., machine=...)")
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
    return values


def _fields(value, allowed, where):
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be an object")
    for key in value:
        if key not in allowed:
            raise ValueError(f"{where}: unsupported field {key}")


def _safe(value, where):
    if (not isinstance(value, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]{0,63}", value)
            or value in {"__proto__", "constructor", "prototype"}):
        raise ValueError(f"{where}: invalid identifier")


def _json_equal(a, b):
    if type(a) in (int, float) and type(b) in (int, float):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_json_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_json_equal(x, y) for x, y in zip(a, b))
    return a == b


def _overlap(a, b):
    details = b.get("detail", {})
    return (all(k not in a or k not in b or a[k] == b[k] for k in ("kind", "target", "outcome"))
            and all(k not in details or _json_equal(v, details[k])
                    for k, v in a.get("detail", {}).items()))


def _transition(event, branch, states):
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
    _fields(params, {"kind", "target", "outcome", "detail"}, "guard.params")
    if params.get("kind") not in ("trigger", "effect", "output"):
        raise ValueError("invalid trace kind")
    for field in ("target", "outcome"):
        value = params.get(field)
        if value is not None and (not isinstance(value, str)
                                  or len(value.encode("utf-16-le", errors="surrogatepass")) // 2 > 256):
            raise ValueError(f"{field} must be a string or null")
    if "detail" in params and not isinstance(params["detail"], dict):
        raise ValueError("detail must be an object")
    return {"event": event, "target": target, "expect": params}


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
        transitions = [] if final else _transitions(name, state.get("on"), source, remaining)
        remaining -= len(transitions)
        states.append({"name": name, "final": final, "transitions": transitions})
    return states


def compile_workflow(config):
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
    return {"model": {"initial": config["initial"], "states": states},
            "mermaid": _render_mermaid(config, states)}


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
        expanded = can_finish | {state["name"] for state in states
                                 if any(t["target"] in can_finish for t in state["transitions"])}
        if expanded == can_finish:
            break
        can_finish = expanded
    dead = [name for name in source if name not in can_finish]
    if dead:
        raise ValueError(f"states with no path to a final state: {', '.join(dead)}")


def _render_mermaid(config, states):
    lines = ["stateDiagram-v2", f"    [*] --> {config['initial']}"]
    entities = {"\\": "#92;", "#": "#35;", '"': "#quot;", ";": "#59;", "|": "#124;",
                "\t": "#9;", "\n": "#10;", "\r": "#13;", "<": "#60;", ">": "#62;"}
    for state in states:
        if state["final"]:
            lines.append(f"    {state['name']} --> [*]")
        for transition in state["transitions"]:
            p = transition["expect"]
            parts = [transition["event"], p["kind"], p.get("target"), p.get("outcome")]
            if "detail" in p:
                parts.append(json.dumps(p["detail"], ensure_ascii=False, separators=(",", ":")))
            label = re.sub(r"[\r\n]+", " ", " / ".join(v for v in parts if v is not None and v != ""))
            label = "".join(entities.get(c, c) for c in label)
            lines.append(f"    {state['name']} --> {transition['target']} : {label}")
    return "\n".join(lines)

def _tool(command, payload):
    timeout = None if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0" else 60
    result = subprocess.run(command, input=json.dumps(payload, allow_nan=False), text=True,
                            capture_output=True, timeout=timeout, check=False)
    if result.returncode:
        raise ValueError(result.stderr.strip() or f"{command[0]} exited with status {result.returncode}")
    return json.loads(result.stdout)


def _trace(data, workflow, model):
    if not isinstance(data, dict) or not isinstance(columns := data.get("columns"), list):
        raise ValueError("Expected a JSON matrix from a flow_events query")
    if (any(not isinstance(col, str) for col in columns) or len(columns) != len(set(columns))
            or not _TRACE_FIELDS <= set(columns) or not isinstance(rows := data.get("rows"), list)
            or len(rows) > 512 or any(not isinstance(row, list) or len(row) != len(columns) for row in rows)):
        raise ValueError("Expected at most 512 flow_events rows and all trace columns")
    records = [dict(zip(columns, row, strict=True)) for row in rows]
    if any(type(record["sequence"]) is not int for record in records):
        raise ValueError("Flow sequence indices must be integers")
    records.sort(key=lambda row: row["sequence"])
    if records and (not isinstance(records[0]["run_id"], str)
                    or any(record["run_id"] != records[0]["run_id"] for record in records)):
        raise ValueError("Select exactly one flow run")
    events = []
    for row in records:
        if row["kind"] in _OBSERVABLE:
            event = {key: row[key] for key in _EVENT_FIELDS}
            if isinstance(event["detail"], str):
                event["detail"] = json.loads(event["detail"])
            if not isinstance(event["detail"], dict):
                raise ValueError("Flow event detail must be a JSON object")
            events.append(event)
        elif row["kind"] != "input":
            raise ValueError("Unknown flow event kind")
    return {"complete": _is_complete(records, events, workflow, model), "events": events}


def _is_complete(records, events, workflow, model):
    trigger_names = {edge["event"] for state in model["states"] for edge in state["transitions"]
                     if edge["expect"]["kind"] == "trigger"}
    triggers = {event["name"] for event in events if event["kind"] == "trigger"}
    return (bool(triggers) and triggers <= trigger_names and events[-1]["kind"] == "output"
            and all(row["component"] == workflow["component"] and row["action"] == workflow["action"]
                    and row["sequence"] == index for index, row in enumerate(records))
            and not any("omitted_events" in event["detail"] or "unattributed" in event["detail"]
                        for event in events))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("solution", type=Path, help="Tier 1 Solution Atom")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("render", help="write Mermaid")
    check = commands.add_parser("check", help="check one exported flow_events run")
    check.add_argument("trace", help="Workbench JSON matrix path or - for stdin")
    args = parser.parse_args(argv)
    try:
        workflow = load_workflow(args.solution)
        compiled = compile_workflow(workflow["machine"])
        if args.command == "render":
            print(compiled["mermaid"].rstrip())
            return 0
        raw_trace = sys.stdin.read() if args.trace == "-" else Path(args.trace).read_text(encoding="utf-8")
        model = compiled["model"]
        trace = _trace(json.loads(raw_trace), workflow, model)
        result = _tool(["lean", "--run", str(_HERE / "WorkflowTrace.lean")], {"model": model, **trace})
        print(json.dumps(result, ensure_ascii=False))
        return {"matched": 0, "different": 1, "unresolved": 2}[result["status"]]
    except (OSError, ValueError, TypeError, KeyError, SyntaxError, subprocess.TimeoutExpired) as error:
        print(f"Workflow specification: {error}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
