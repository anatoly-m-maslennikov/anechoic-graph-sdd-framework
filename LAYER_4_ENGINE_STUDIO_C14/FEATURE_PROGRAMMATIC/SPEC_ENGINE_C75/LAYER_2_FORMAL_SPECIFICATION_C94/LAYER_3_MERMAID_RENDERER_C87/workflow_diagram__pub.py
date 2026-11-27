import json
import re


def render_workflow_diagram(model, prefix=""):
    state_ids = {state["name"]: f"{prefix}S{index}" for index, state in enumerate(model["states"])}
    lines = ["stateDiagram-v2"]
    lines.extend(f'    state "{name}" as {state_id}' for name, state_id in state_ids.items())
    lines.append(f"    [*] --> {state_ids[model['initial']]}")
    entities = {"\\": "#92;", "#": "#35;", '"': "#quot;", ";": "#59;", "|": "#124;",
                "\t": "#9;", "\n": "#10;", "\r": "#13;", "<": "#60;", ">": "#62;"}
    for state in model["states"]:
        state_id = state_ids[state["name"]]
        if state["final"]:
            lines.append(f"    {state_id} --> [*]")
        for transition in state["transitions"]:
            p = transition["expect"]
            parts = [transition["event"], p["kind"]]
            parts.extend(f"{key}={json.dumps(p[key], ensure_ascii=False)}"
                         for key in ("target", "outcome") if key in p)
            if "detail" in p:
                parts.append(json.dumps(p["detail"], ensure_ascii=False, separators=(",", ":")))
            for key in ("bind", "same_as"):
                if p.get(key):
                    parts.append(f"{key}={json.dumps(p[key], ensure_ascii=False, separators=(',', ':'))}")
            label = re.sub(r"[\r\n]+", " ", " / ".join(v for v in parts if v is not None and v != ""))
            label = "".join(entities.get(c, c) for c in label)
            lines.append(f"    {state_id} --> {state_ids[transition['target']]} : {label}")
    return "\n".join(lines)


def render_operation_diagram(operations):
    """Render independent workflows as separate Mermaid composite states."""
    lines = ["stateDiagram-v2"]
    for index, (action, workflow) in enumerate(operations.items(), 1):
        name = f"operation_{index}_" + re.sub(r"[^A-Za-z0-9_]", "_", action)[:60]
        label = "".join(f"#{ord(c)};" if c.isspace() or c in '#;%&<>\\|"'
                        else c for c in action)
        lines.append(f"    {name}: {label}")
        lines.append(f"    state {name} {{")
        lines.extend("    " + line for line in render_workflow_diagram(
            workflow, prefix=name + "_").splitlines()[1:])
        lines.append("    }")
    return "\n".join(lines)
