"""Independent, pinned C46 current-check reply order translation pilot."""

import ast
import json

# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    _package__shared import (
    load_boundary_model,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    json_equal,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84.\
    _package__shared import (
    run_lean_json,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_TRANSLATION_VALIDATOR_C86.\
    LAYER_4_TRANSLATION_VALIDATOR_C86__tests.functional.\
    typed_trace import (
    check_capture,
)
# fmt: on

_BASE = "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/"
PINS = (
    {
        "path": _BASE + "01_draft/AN-S-3060@10-draft-SPEC-COMPONENT_MA"
        "NIFEST--declare-iwe-console-frontend.md",
        "atom_id": "AN-S-3060",
        "version": 10,
        "status": "draft",
        "container_component": "C43",
    },
    {
        "path": _BASE + "FEATURE_IWE_CONSOLE_FRONTEND_C46/01_draft/AN-"
        "S-3306@3-draft-DES-COMPONENT_CONTRACT--show-w"
        "orkbench-query-results-in-the-browser.md",
        "atom_id": "AN-S-3306",
        "version": 3,
        "status": "draft",
        "container_component": "C46",
    },
    {
        "path": _BASE + "FEATURE_IWE_CONSOLE_FRONTEND_C46/01_draft/AN-"
        "S-3372@3-draft-DES-DECISION--run-the-current-"
        "view-in-the-browser.md",
        "atom_id": "AN-S-3372",
        "version": 3,
        "status": "draft",
        "container_component": "C46",
    },
)
_ACTION = "workbench_frontend_check_view"
_OUTPUT = "checked"
_ORDER = (
    ("project_api.view_check", "returned", {"sql": "current"}),
    ("workbench_check_verdict", "shown_for_current_sql"),
)


def _call(source, name):
    body = ast.parse(source).body
    if (
        len(body) != 1
        or not isinstance(body[0], ast.Expr)
        or not isinstance(body[0].value, ast.Call)
    ):
        raise ValueError("expected a single formal call")
    call = body[0].value
    if (
        not isinstance(call.func, ast.Name)
        or call.func.id != name
        or call.args
    ):
        raise ValueError("unexpected formal call")
    keys = [item.arg for item in call.keywords]
    if None in keys or len(keys) != len(set(keys)):
        raise ValueError("duplicate or expanded formal arguments")
    return {item.arg: ast.literal_eval(item.value) for item in call.keywords}


def _select(claims, name):
    values = [_call(source, name) for _, source in claims]
    matches = [
        value
        for value in values
        if value.get("action") == _ACTION
        and (
            name != "declare_trace_contract" or value.get("output") == _OUTPUT
        )
    ]
    if len(matches) != 1:
        raise ValueError("expected one selected C46 claim")
    return matches[0]


def _source_edges(machine):
    states = machine["states"]
    edges = []
    for source, state in states.items():
        for event, branches in state.get("on", {}).items():
            for branch in (
                branches if isinstance(branches, list) else [branches]
            ):
                expect = (
                    branch["expect"]
                    if "expect" in branch
                    else branch["guard"]["params"]
                )
                next_state = (
                    branch["to"] if "to" in branch else branch["target"]
                )
                outcome = expect.get("outcome")
                target = expect.get("target")
                bindings = [
                    [
                        list(pair)
                        for pair in sorted(expect.get(key, {}).items())
                    ]
                    for key in ("bind", "same_as")
                ]
                edges.append(
                    [
                        source,
                        next_state,
                        expect["kind"],
                        target or "",
                        outcome or "",
                        outcome is None,
                        states[next_state].get("type") == "final",
                        target is None,
                        not (outcome or "").strip(),
                        expect.get("detail", {}),
                        event,
                        *bindings,
                    ]
                )
    return edges


def _order_position(
    kind, observed, outcome, wildcard, target_wildcard, detail
):
    before = (
        kind == "effect"
        and observed == _ORDER[0][0]
        and outcome == _ORDER[0][1]
        and detail.get("sql") == "current"
    )
    after = (
        kind == "effect"
        and (target_wildcard or observed == _ORDER[1][0])
        and (wildcard or outcome == _ORDER[1][1])
    )
    return before, after


def _oracle(initial, edges):
    if any(edge[11] or edge[12] for edge in edges):
        return "unresolved"
    pending = [(initial, False, False)]
    seen = set()
    selected = False
    while pending:
        state, replied, displayed_early = pending.pop()
        if (state, replied, displayed_early) in seen:
            continue
        seen.add((state, replied, displayed_early))
        for (
            source,
            target,
            kind,
            observed,
            outcome,
            wildcard,
            final,
            target_wildcard,
            _,
            detail,
            *_,
        ) in edges:
            if source != state:
                continue
            if kind == "output" and final and (wildcard or outcome == _OUTPUT):
                selected |= not wildcard
                if displayed_early:
                    return "conflicting"
            before, after = _order_position(
                kind, observed, outcome, wildcard, target_wildcard, detail
            )
            pending.append(
                (
                    target,
                    replied or before,
                    displayed_early or (after and not replied),
                )
            )
    return "matched" if selected else "unresolved"


def _capture(program, lean):
    evaluation = """
#eval IO.println (Lean.Json.arr #[Lean.toJson initial, Lean.toJson output,
  Lean.Json.arr ((edges.map (fun e => Lean.Json.arr #[Lean.toJson e.source,\
 Lean.toJson e.target,
    Lean.toJson e.kind, Lean.toJson e.observed, Lean.toJson e.outcome,\
 Lean.toJson e.wildcard,
    Lean.toJson e.final, Lean.toJson e.targetWildcard, Lean.toJson\
 e.missingOutcome,
    Lean.toJson e.detail, Lean.toJson e.event, Lean.toJson e.bind,\
 Lean.toJson e.sameAs])).toArray),
  Lean.Json.arr ((orders.map (fun p => Lean.Json.arr #[Lean.toJson\
 p.1.observed, Lean.toJson p.1.outcome,
    Lean.toJson p.1.detail, Lean.toJson p.2.observed, Lean.toJson\
 p.2.outcome, Lean.toJson p.2.detail])).toArray),
  Lean.toJson (orders.map orderStatus)]).compress
"""
    marker = "#eval IO.println (Lean.toJson (actionStatus"
    if program.count(marker) != 1:
        raise ValueError("unexpected trace artifact")
    actual = run_lean_json(program[: program.index(marker)] + evaluation, lean)
    actual_edges = actual[2]
    for edge in actual_edges:
        edge[9] = {json.loads(k): json.loads(v) for k, v in edge[9]}
    actual_orders = actual[3]
    for order in actual_orders:
        order[2] = {json.loads(k): json.loads(v) for k, v in order[2]}
        order[5] = {json.loads(k): json.loads(v) for k, v in order[5]}
    return actual


def validate_c46_trace(root, program, *, lean="lean"):
    """Validate the selected emitted C46 trace."""
    model = load_boundary_model(root, "C46", *PINS)
    if model["issues"]:
        raise ValueError(str(model["issues"]))
    contract = _select(model["contract"]["claims"], "declare_trace_contract")
    solution = _select(model["solution"]["claims"], "component_workflow")
    if contract["must_precede"] != (_ORDER,) or solution["component"] != "C46":
        raise ValueError("pinned current-reply order changed")
    manifest = model["manifest"]["boundaries"]["io"]["server"][_ACTION][
        "outcomes"
    ][_OUTPUT]
    if any(effect not in manifest["must_effect"] for effect in _ORDER):
        raise ValueError("manifest does not contain the selected effects")
    initial = solution["machine"]["initial"]
    edges = _source_edges(solution["machine"])
    expected_status = _oracle(initial, edges)
    actual = _capture(program, lean)
    expected_order = [[*_ORDER[0], *_ORDER[1], {}]]
    matches = (
        actual[0] == initial
        and actual[1] == _OUTPUT
        and json_equal(actual[2], edges)
        and json_equal(actual[3], expected_order)
        and actual[4] == [expected_status]
    )
    if matches:
        check_capture((initial, edges), (actual[0], actual[2]), lean)
    return {
        "status": "matched" if matches else "conflicting",
        "source_status": expected_status,
        "lean_status": actual[4],
        "sources": [
            model[role]["source"]
            for role in ("manifest", "contract", "solution")
        ],
    }
