"""Render a Component Solution or check one recorded flow against it."""

import argparse
import ast
import json
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


def _tool(command, payload):
    result = subprocess.run(command, input=json.dumps(payload, allow_nan=False), text=True,
                            capture_output=True, timeout=60, check=False)
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
        compiled = _tool(["node", str(_HERE / "WORKFLOW_SPEC/compile.mjs")], workflow["machine"])
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
