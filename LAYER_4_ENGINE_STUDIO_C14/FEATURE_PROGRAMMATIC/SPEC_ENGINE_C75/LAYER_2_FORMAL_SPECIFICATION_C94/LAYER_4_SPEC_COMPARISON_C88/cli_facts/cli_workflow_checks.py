"""Extract workflow facts for CLI specification comparison."""

from itertools import pairwise

# fmt: off
from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85.\
    _package__shared import (
    exit_code,
    exit_status_class,
)
# fmt: on
from .cli_reachability import feasible_terminals
from .cli_selection import _status_values


def _outcome_status_facts(outcomes, modeled_key):
    facts = {"outcomes": _status_values(outcomes)}
    if modeled_key == "exit_code":
        classes = {
            name: {"zero" if code == 0 else "nonzero" for code in codes}
            for name, codes in outcomes.items()
        }
        facts = {
            "exit_codes": facts["outcomes"],
            "outcomes": _status_values(classes),
        }
    return facts


def _solution_outcomes(claim, contract):
    feasible = feasible_terminals(claim)
    if feasible is None:
        return {}
    states = {state["name"]: state for state in claim["states"]}
    outcomes, complete = {}, not states[claim["initial"]]["final"]
    modeled_key = None
    for name, index in sorted(feasible):
        expected = states[name]["transitions"][index]["expect"]
        outcome = expected.get("outcome")
        detail = expected.get("detail", {})
        fields = detail.keys() & {"exit_code", "exit_status_class"}
        if expected["kind"] != "output" or not outcome or not fields:
            complete = False
            continue
        if len(fields) != 1 or (modeled_key is not None and modeled_key not in fields):
            raise ValueError("Solution mixes exit codes and exit status classes")
        (modeled_key,) = fields
        validate = exit_code if modeled_key == "exit_code" else exit_status_class
        outcomes.setdefault(outcome, set()).add(validate(detail[modeled_key]))
    facts = _outcome_status_facts(outcomes, modeled_key)
    if complete:
        return facts
    return {
        key: observed
        for key, observed in facts.items()
        if key in contract
        and any(value != contract[key].get(name) for name, value in observed.items())
    }


def _common_checks(details, names):
    facts = {}
    for field, key, expected_type in names:
        values = [detail.get(field) for detail in details]
        if not values or any(type(value) is not expected_type for value in values):
            continue
        if expected_type is list:
            if any(
                any(not isinstance(item, str) for item in value) for value in values
            ):
                continue
            values = [sorted(value) for value in values]
        else:
            values = [[value] for value in values]
        facts[key] = (
            values[0] if all(value == values[0] for value in values) else values
        )
    return facts


def _reachable_without(claim, blocked):
    states = {state["name"]: state["transitions"] for state in claim["states"]}
    reached = {claim["initial"]}
    queue = [claim["initial"]]
    for name in queue:
        for transition in states[name]:
            target = transition["target"]
            if transition is not blocked and target not in reached:
                reached.add(target)
                queue.append(target)
    return reached


def _success_outputs(terminals):
    return [
        (name, transition["expect"].get("detail", {}))
        for name, transition in terminals
        if transition["expect"]["kind"] == "output"
        and transition["expect"].get("outcome") == "succeeded"
    ]


def _query_checks(claim, edges, successes, component_id):
    effects = [
        transition
        for _, transition in edges
        if transition["expect"]["kind"] == "effect"
    ]
    if len(effects) != 1 or not successes:
        return {}
    effect = effects[0]
    expect = effect["expect"]
    if expect.get("target") != component_id or expect.get("outcome") != "succeeded":
        return {}
    bypass = _reachable_without(claim, effect)
    if any(name in bypass for name, _ in successes):
        return {}
    detail = expect.get("detail", {})
    checks = _common_checks(
        [detail],
        (
            ("match_fields", "guarantees.match_fields", list),
            ("rank_first", "guarantees.priority", str),
            ("read_source", "effects.query_scope", str),
        ),
    )
    for key, observation, obligation in (
        ("guarantees.priority", "exact_name_match", "exact_name_first"),
        ("effects.query_scope", "context_argument", "supplied_frozen_context"),
    ):
        if key in checks:
            checks[key] = (
                [obligation]
                if checks[key] == [observation]
                else {"observed": checks[key]}
            )
    return checks


def _stage_bypasses(claim, stages, order):
    if any(len(stages.get(name, ())) != 1 for name in order):
        return None
    return [
        after
        for before, after in pairwise(order)
        if stages[after][0][0] in _reachable_without(claim, stages[before][0][1])
    ]


def _image_checks(claim, edges, stages, image, checks):
    install = stages["install"][0][1]
    finals = {state["name"] for state in claim["states"] if state["final"]}
    reachable = _reachable_without(claim, None)
    successes = [
        source
        for source, edge in edges
        if source in reachable
        and edge["target"] in finals
        and edge["expect"]["kind"] == "output"
        and edge["expect"].get("outcome")
        in ("completed", "completed_with_cleanup_pending")
    ]
    bypass = _reachable_without(claim, install)
    possible = [
        source
        for source, edge in edges
        if edge["target"] in finals
        and edge["expect"]["kind"] == "output"
        and edge["expect"].get("outcome") is None
    ]
    refs = [
        stages[stage][0][1]["expect"]["detail"].get("image_ref")
        for stage in ("build", "verify_image", "install")
    ]
    if image or any(source in bypass for source in successes + possible):
        checks["guarantees.image_checks_before_install"] = {
            "bypassed_before": image or ["completion"]
        }
    elif all(isinstance(ref, str) and ref.strip() for ref in refs):
        if len(set(refs)) != 1:
            checks["guarantees.image_checks_before_install"] = {"image_refs": refs}
        elif successes:
            checks["guarantees.image_checks_before_install"] = ["exact_candidate"]


def _release_checks(claim, edges):
    stages = {}
    for source, edge in edges:
        expect = edge["expect"]
        stage = expect.get("detail", {}).get("release_stage")
        if (
            expect["kind"] == "effect"
            and expect.get("outcome") in ("passed", "succeeded")
            and isinstance(stage, str)
        ):
            stages.setdefault(stage, []).append((source, edge))
    checks = {
        f"guarantees.{stage}_owner": [owner]
        for stage, rows in stages.items()
        if len(rows) == 1 and (owner := rows[0][1]["expect"].get("target"))
    }
    host = _stage_bypasses(claim, stages, ("static", "functional", "build"))
    if host is not None:
        checks["guarantees.host_checks_before_build"] = (
            {"bypassed_before": host} if host else ["static_then_functional"]
        )
    image = _stage_bypasses(claim, stages, ("build", "verify_image", "install"))
    if image is not None:
        _image_checks(claim, edges, stages, image, checks)
    return checks


def _first_dispatch(states, starts, detail_fields):
    reached = set(starts)
    queue = list(starts)
    targets = set()
    details = []
    bypassed = False
    for name in queue:
        state = states[name]
        bypassed |= state["final"]
        for edge in state["transitions"]:
            expect = edge["expect"]
            if expect["kind"] == "effect":
                targets.add(expect.get("target"))
                if detail_fields:
                    details.append(expect.get("detail", {}))
            elif edge["target"] not in reached:
                reached.add(edge["target"])
                queue.append(edge["target"])
    if len(targets) == 1 and None not in targets and not bypassed:
        (target,) = targets
        if not detail_fields:
            return target
        return {
            "component": target,
            **{
                key: details[0][key]
                for key in detail_fields
                if key in details[0]
                and all(
                    key in detail and detail[key] == details[0][key]
                    for detail in details
                )
            },
        }
    return {
        "targets": sorted(target for target in targets if target is not None),
        "unbound_effect": None in targets,
        "terminal_without_dispatch": bypassed,
    }
