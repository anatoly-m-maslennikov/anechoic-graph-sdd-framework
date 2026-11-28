"""Prepare Lean cases and project verified findings."""

import json


def _lean_case(path, case, policy, units):
    result = {
        "sourcePath": path,
        "line": case["line"],
        "input": case["input"],
        "reachable": case["reachable"],
        "declaredNoOp": case["declaredNoOp"],
        "complete": case["complete"] and isinstance(case["input"], dict),
        "events": [
            {
                **event,
                "name": policy["owner"]
                if event["name"] == "$owner"
                else event["name"],
            }
            for event in case["events"]
        ],
        "policy": policy,
    }
    if case.get("inlineable"):
        unit = units.get((path, case["line"], case["column"]))
        if unit is not None:
            result["unit"] = unit
    return result


def _unresolved(path, source, detail):
    return (
        f"module:{path}",
        path,
        source.language,
        "<module>",
        1,
        None,
        "unresolved",
        False,
        "[]",
        "[]",
        detail,
    )


def _finding(source, action, case, result, *, graph_mode):
    path = case["sourcePath"]
    status = result["status"]
    detail = (
        "Control flow, effects, or input are not fully modeled"
        if status == "unresolved"
        else None
    )
    witness = None if case["input"] is None else json.dumps(case["input"])
    violations = (
        result["violations"] if case["reachable"] and case["complete"] else []
    )
    events = result["events"] if graph_mode else case["events"]
    for event in (*events, *violations):
        if event.get("sourcePath") is None:
            event.pop("sourcePath", None)
    if action == "<module>" and status == "deadEnd":
        return None
    return (
        f"module:{path}",
        path,
        source.language,
        action,
        case["line"],
        witness,
        status,
        status == "deadEnd",
        json.dumps(events),
        json.dumps(violations),
        detail,
    )
