"""Check supported workflow compiler behavior on a finite supplied graph."""

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

if __package__:
    from .graph_validation import validate_graph
else:
    from graph_validation import validate_graph

HERE = Path(__file__).resolve().parent
SOURCE = (
    "LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/"
    "FEATURE_IMPORT_GRAPH_C61/WORKFLOW_SPEC/WORKFLOW_SPEC__shared.mjs"
)
DETAILS = (
    "Overlapping output guards are accepted for the same event.",
    "A reachable closed cycle with no path to a final state is accepted.",
)
DEFAULT = {
    "id": "pilot",
    "initial": "start",
    "states": {
        "start": {
            "on": {
                "output": [
                    {
                        "target": "stuck",
                        "guard": {
                            "type": "matchesTrace",
                            "params": {"kind": "output"},
                        },
                    },
                    {
                        "target": "done",
                        "guard": {
                            "type": "matchesTrace",
                            "params": {"kind": "output", "outcome": "success"},
                        },
                    },
                ]
            }
        },
        "stuck": {
            "on": {
                "loop": {
                    "target": "stuck",
                    "guard": {
                        "type": "matchesTrace",
                        "params": {"kind": "output"},
                    },
                }
            }
        },
        "done": {"type": "final"},
    },
}


def translate(path, graph):
    run = subprocess.run(
        ["node", str(HERE / "extract.cts"), str(path)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if run.returncode:
        raise ValueError("unsupported JavaScript: " + run.stderr.strip())
    facts = json.loads(run.stdout)
    transitions = graph["transitions"]
    keys, values = {}, {}
    guards = []
    for t in transitions:
        items = [(k, v) for k, v in t["guard"].items() if k != "detail"]
        items += [
            ("detail." + k, v)
            for k, v in t["guard"].get("detail", {}).items()
        ]  # fmt: skip
        encoded = []
        for key, value in items:
            value = json.dumps(value, ensure_ascii=True, separators=(",", ":"))
            keys.setdefault(key, len(keys))
            values.setdefault(value, len(values))
            encoded.append((keys[key], values[value]))
        guards.append(encoded)
    groups = {}
    for i, transition in enumerate(transitions):
        groups.setdefault(
            (transition["source"], transition["event"]), []
        ).append(i)  # fmt: skip
    groups = [indices for indices in groups.values() if len(indices) > 1]
    return render_graph(graph, facts, guards, groups)


def lean_list(items):
    return "[" + ", ".join(items) + "]"


def render_graph(graph, facts, guards, groups):
    states, transitions = graph["states"], graph["transitions"]
    prefix = "set_option maxRecDepth 10000\n" + "".join(
        f"def {name}Check : Bool := {str(facts[key]).lower()}\n"
        for name, key in [("overlap", "overlap"), ("finish", "finish")]
    )
    prefix += (
        "def edges : List (Nat × Nat) := "
        + lean_list(
            [
                f"({states.index(t['source'])}, {states.index(t['target'])})"
                for t in transitions
            ]
        )
        + "\n"
    )
    prefix += (
        "def finals : List Nat := "
        + lean_list([str(states.index(s)) for s in graph["final"]])
        + "\n"
    )
    prefix += (
        "def initial : Nat := "
        + str(states.index(graph["initial"]))
        + "\n"
    )  # fmt: skip
    prefix += "def fuel : Nat := " + str(len(states)) + "\n"
    for i, guard in enumerate(guards):
        prefix += (
            f"def guard{i} : List (Nat × Nat) := "
            + lean_list([f"({k}, {v})" for k, v in guard])
            + "\n"
        )
    code = prefix + (HERE / "model.lean.txt").read_text()
    code = append_graph_queries(code, groups, states)
    return code + "\n", groups, facts


def append_graph_queries(code, groups, states):
    code += "".join(overlap_query(group) for group in groups)
    code += "".join(
        f"\n#eval !finishCheck && reaches fuel initial {i} "
        f"&& !(finishes fuel {i})"  # fmt: skip
        for i in range(len(states))
    )
    return code


def overlap_query(group):
    pairs = [f"({i}, guard{i})" for i in group]
    return "\n#eval firstOverlap " + lean_list(pairs)


def append_overlap_findings(matches, facts, normalized, graph, result):
    for match in matches:
        if match and not facts["overlap"]:
            i, j = map(int, match.groups())
            a, b = normalized["transitions"][i], normalized["transitions"][j]
            witness = {**a["guard"], **b["guard"]}
            if "detail" in a["guard"] or "detail" in b["guard"]:
                witness["detail"] = {
                    **a["guard"].get("detail", {}),
                    **b["guard"].get("detail", {}),
                }
            result["findings"].append(
                {
                    "path": SOURCE,
                    "detail": DETAILS[0]
                    if graph is DEFAULT
                    else "Overlapping guards are accepted for the same event.",
                    "witness": {
                        "state": a["source"],
                        "event": a["event"],
                        "transitions": [i, j],
                        "guard": witness,
                    },
                }
            )


def proof_outcomes(lean, code, groups, states):
    with tempfile.TemporaryDirectory() as tmp:
        proof = Path(tmp) / "check.lean"
        proof.write_text(code)
        run = subprocess.run(
            [lean, str(proof)],
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
    outcomes = run.stdout.strip().splitlines()
    overlaps = outcomes[: len(groups)]
    dead = outcomes[len(groups) :]
    matches = [
        re.fullmatch(r"some \((\d+), (\d+)\)", item)
        for item in overlaps
    ]  # fmt: skip
    invalid_overlap = any(
        item != "none" and not match for item, match in zip(overlaps, matches)
    )
    if (
        run.returncode
        or len(outcomes) != len(groups) + len(states)
        or invalid_overlap
        or any(item not in ("true", "false") for item in dead)
    ):
        raise ValueError("Lean failed: " + run.stderr + run.stdout)
    return matches, dead


def analyze(checkout, lean, graph=DEFAULT):
    result = {"findings": [], "unresolved": []}
    try:
        normalized = validate_graph(graph)
        code, groups, facts = translate(checkout / SOURCE, normalized)
        matches, dead = proof_outcomes(
            lean, code, groups, normalized["states"]
        )  # fmt: skip
        append_overlap_findings(matches, facts, normalized, graph, result)
        if facts["overlap"] and any(matches):
            if graph is DEFAULT:
                alternate = json.loads(json.dumps(DEFAULT))
                start = alternate["states"]["start"]
                output = start["on"]["output"][0]
                guard = output["guard"]
                guard["params"]["outcome"] = "failure"
                independent = analyze(checkout, lean, alternate)
                for finding in independent["findings"]:
                    finding["detail"] = DETAILS[1]
                return independent
            return result
        for outcome, state in zip(dead, normalized["states"]):
            if outcome == "true":
                result["findings"].append(
                    {
                        "path": SOURCE,
                        "detail": DETAILS[1]
                        if graph is DEFAULT
                        else (
                            "A reachable state with no path to a final state "
                            "is accepted."
                        ),
                        "witness": {"state": state},
                    }
                )
    except (
        OSError,
        ValueError,
        TypeError,
        subprocess.TimeoutExpired,
    ) as error:
        result["unresolved"].append({"path": SOURCE, "detail": str(error)})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--lean", required=True)
    parser.add_argument("--scenario", type=Path)
    args = parser.parse_args()
    try:
        graph = (
            json.loads(args.scenario.read_text())
            if args.scenario
            else DEFAULT
        )  # fmt: skip
        print(json.dumps(analyze(args.checkout, args.lean, graph)))
    except (OSError, ValueError) as error:
        print(
            json.dumps(
                {
                    "findings": [],
                    "unresolved": [{"path": SOURCE, "detail": str(error)}],
                }
            )
        )


if __name__ == "__main__":
    main()
