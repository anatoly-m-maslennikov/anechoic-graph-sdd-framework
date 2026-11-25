"""Render a Component Solution or check one recorded flow against it."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import formal_claim_fences
from SPEC_ENGINE_C75.workflow_model__pub import compile_workflow
from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.workflow_model__pub import parse_workflow

_HERE = Path(__file__).resolve().parent
_OBSERVABLE = {"trigger", "effect", "output"}
_EVENT_FIELDS = ("kind", "name", "target", "outcome", "detail")
_TRACE_FIELDS = {"run_id", "component", "action", "sequence", *_EVENT_FIELDS}


def load_workflow(path):
    fences = list(formal_claim_fences(path.read_text(encoding="utf-8")))
    if len(fences) != 1 or fences[0][0] != "python":
        raise ValueError("Expected one Python Formal Claim")
    return parse_workflow(fences[0][1])


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
