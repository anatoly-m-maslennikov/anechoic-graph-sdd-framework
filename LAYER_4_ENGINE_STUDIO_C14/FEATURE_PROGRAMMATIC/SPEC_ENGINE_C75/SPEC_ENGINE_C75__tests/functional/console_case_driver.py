"""Extract executable inputs and observations from pinned Console claims."""

import json
import sys
from pathlib import Path

# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
# fmt: on


def pinned_console_claims(root):
    base = "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/"
    manifest = {
        "path": (
            f"{base}01_TIER_1_ARCHITECTURE/"
            "AN-S-3060-SPEC-COMPONENT_MANIFEST--"
            "declare-iwe-console-frontend.md"
        ),
        "atom_id": "AN-S-3060",
        "version": 18,
        "status": "active",
        "container_component": "C43",
    }
    solution = {
        "path": (
            f"{base}FEATURE_IWE_CONSOLE_FRONTEND_C46/"
            "AN-S-3372-DES-SOLUTION--run-the-current-view-in-the-browser.md"
        ),
        "atom_id": "AN-S-3372",
        "version": 10,
        "status": "active",
        "container_component": "C46",
    }
    model = load_boundary_model(root, "C46", manifest, solution=solution)
    compiled = compile_lean(model)
    if model["issues"] or compiled["issues"]:
        raise ValueError(
            f"Invalid C46 claims: {model['issues'] + compiled['issues']}"
        )
    return compiled["claims"]


def pinned_patchbay_claims(root):
    base = "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/"
    manifest = {
        "path": base + "01_draft/AN-S-3044@68-draft-SPEC-COMPONENT_MANIFEST--"
        "declare-mcp.md",
        "atom_id": "AN-S-3044",
        "version": 68,
        "status": "draft",
        "container_component": "C14",
    }
    solution = {
        "path": base
        + "MCP_PATCHBAY_C21/01_draft/AN-S-5044@1-draft-DES-SOLUTION--"
        "forward-a-console-document.md",
        "atom_id": "AN-S-5044",
        "version": 1,
        "status": "draft",
        "container_component": "C21",
    }
    return _patchbay_claims(root, manifest, solution)


def pinned_patchbay_rest_claims(root):
    base = "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/"
    manifest = {
        "path": base + "01_TIER_1_ARCHITECTURE/AN-S-3044-SPEC-"
        "COMPONENT_MANIFEST--declare-mcp.md",
        "atom_id": "AN-S-3044",
        "version": 76,
        "status": "active",
        "container_component": "C14",
    }
    solution = {
        "path": base + "MCP_PATCHBAY_C21/AN-S-5186-DES-SOLUTION--"
        "bridge-the-canonical-backend-tool-rest-operations.md",
        "atom_id": "AN-S-5186",
        "version": 5,
        "status": "active",
        "container_component": "C21",
    }
    return _patchbay_claims(root, manifest, solution)


def _patchbay_claims(root, manifest, solution):
    model = load_boundary_model(root, "C21", manifest, solution=solution)
    compiled = compile_lean(model)
    if model["issues"] or compiled["issues"]:
        raise ValueError(
            f"Invalid C21 claims: {model['issues'] + compiled['issues']}"
        )
    return compiled["claims"]


def pinned_rebuild_claims(root):
    base = "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/"
    manifest = {
        "path": base + "01_TIER_1_ARCHITECTURE/"
        "AN-S-3047-SPEC-COMPONENT_MANIFEST--declare-kernel-mixer.md",
        "atom_id": "AN-S-3047",
        "version": 35,
        "status": "active",
        "container_component": "C14",
    }
    solution = {
        "path": base + "KERNEL_MIXER_C59/"
        "AN-S-5194-SPEC-SOLUTION--rebuild-only-the-realization-graph.md",
        "atom_id": "AN-S-5194",
        "version": 2,
        "status": "active",
        "container_component": "C59",
    }
    model = load_boundary_model(root, "C59", manifest, solution=solution)
    compiled = compile_lean(model)
    issues = model["issues"] + compiled["issues"]
    if issues:
        raise ValueError(f"Invalid C59 claims: {issues}")
    return compiled["claims"]


def _outputs_after(states, start):
    pending = [start]
    visited = set()
    outputs = set()
    while pending:
        name = pending.pop()
        if name in visited:
            continue
        visited.add(name)
        for edge in states[name]:
            if edge["expect"]["kind"] == "output":
                outputs.add(edge["expect"]["outcome"])
            else:
                pending.append(edge["target"])
    return outputs


def _case_inputs(action, states, initial, selecting):
    inputs = {}
    for edge in states[initial]:
        expect = edge["expect"]
        if expect["kind"] == "output":
            names, arguments = (expect["outcome"],), {}
        elif selecting or expect["kind"] == "trigger":
            names = _outputs_after(states, edge["target"])
            arguments = expect.get("detail", {})
        else:
            continue
        for name in names:
            if selecting and edge["event"] != name:
                raise ValueError(
                    f"{action}: binding {edge['event']} leads to {name}"
                )
            if name in inputs:
                raise ValueError(f"{action}: ambiguous input for {name}")
            inputs[name] = arguments
    return inputs


def _observation(case, arguments, binding):
    obligations = {
        key: case.get(key, [])
        for key in (
            "must_effect",
            "forbid_effect",
            "must_precede",
            "same_values",
        )
    }
    required = obligations["must_effect"]
    result = {
        "name": case["output"],
        "input": arguments,
        "effect": required[-1] if required else None,
        **obligations,
    }
    if binding is not None:
        result["binding"] = binding
    return result


def observable_cases(claims, action, selecting=False):
    contract, workflow = claims["contract"], claims["solution"]
    if "operations" in contract:
        contract = contract["operations"][action]
        workflow = workflow["operations"][action]
    elif contract["action"] != action or workflow["action"] != action:
        raise ValueError(f"{action}: claim actions differ")
    cases = contract["cases"]
    states = {
        state["name"]: state["transitions"] for state in workflow["states"]
    }
    initial, binding = workflow["initial"], None
    if selecting:
        if (
            len(states[initial]) != 1
            or states[initial][0]["target"] != "selecting"
        ):
            raise ValueError(f"{action}: expected one trigger to selecting")
        trigger = states[initial][0]
        if (
            trigger["expect"]["kind"] != "trigger"
            or trigger["expect"]["target"] != "workbench_http"
        ):
            raise ValueError(f"{action}: expected workbench_http trigger")
        binding = trigger["expect"]["detail"]
        if any(
            binding[key] != contract[key]
            for key in ("endpoint", "route_name", "transport")
        ):
            raise ValueError(f"{action}: contract and trigger bindings differ")
        initial = "selecting"
    inputs = _case_inputs(action, states, initial, selecting)
    outputs = {
        edge["expect"]["outcome"]
        for transitions in states.values()
        for edge in transitions
        if edge["expect"]["kind"] == "output"
    }
    if outputs != {case["output"] for case in cases}:
        raise ValueError(f"{action}: contract and workflow outputs differ")
    for case in cases:
        name = case["output"]
        if name not in inputs:
            raise ValueError(f"{action}: no input reaches {name}")
        yield _observation(case, inputs[name], binding)


def main():
    root = Path(__file__).resolve().parents[5]
    actions = sys.argv[1:]
    output = {}
    rebuild = "rebuild_only_realization_graph"
    patchbay = "forward_console_document"
    rest = "forward_tool_rest"
    browser_actions = set(actions) - {patchbay, rebuild, rest}
    if browser_actions:
        claims = pinned_console_claims(root)
        output.update(
            {
                action: list(observable_cases(claims, action))
                for action in actions
                if action in browser_actions
            }
        )
    if rebuild in actions:
        output[rebuild] = list(
            observable_cases(pinned_rebuild_claims(root), rebuild)
        )
    if patchbay in actions:
        claims = pinned_patchbay_claims(root)
        output[patchbay] = list(observable_cases(claims, patchbay, True))
    if rest in actions:
        output[rest] = list(
            observable_cases(pinned_patchbay_rest_claims(root), rest)
        )
    print(json.dumps(output))


if __name__ == "__main__":
    main()
