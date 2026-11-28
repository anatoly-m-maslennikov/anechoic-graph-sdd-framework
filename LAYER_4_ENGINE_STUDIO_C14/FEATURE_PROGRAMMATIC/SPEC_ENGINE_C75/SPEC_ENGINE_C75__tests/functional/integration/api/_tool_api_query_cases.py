import copy

from importlib import import_module

_tool_api = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
    "LAYER_2_FORMAL_SPECIFICATION_C94."
    "LAYER_4_SPEC_COMPARISON_C88._package__shared"
)
_tool_solution = _tool_api._tool_solution
check_tool_api_spec = _tool_api.check_tool_api_spec
solution_tool_api = _tool_api.solution_tool_api


def _query_workflow(effect, success):
    claim = {
        "initial": "start",
        "states": [
            {
                "name": "start",
                "final": False,
                "transitions": [
                    {"target": "report", "expect": effect},
                    {"target": "report", "expect": copy.deepcopy(effect)},
                ],
            },
            {
                "name": "report",
                "final": False,
                "transitions": [
                    {"target": "report", "expect": {"kind": "trigger"}},
                    {"target": "done", "expect": success},
                ],
            },
            {"name": "done", "final": True, "transitions": []},
        ],
    }
    return claim


def _query_inputs():
    sql = {
        "statement_count": 1,
        "read_only": True,
        "cursor_metadata_only": True,
        "uses_full_submitted_sql": True,
        "uses_selected_project": True,
    }
    effect = {
        "kind": "effect",
        "target": "C59",
        "outcome": "succeeded",
        "detail": {"operation": "run", "sql": sql},
    }
    success = {
        "kind": "output",
        "outcome": "succeeded",
        "detail": {"http_outcome": "success"},
    }
    return effect, success


def check_query_evidence(self):
    effect, success = _query_inputs()
    claim = _query_workflow(effect, success)
    self.assertEqual(
        ["one_complete_read_only_statement"],
        solution_tool_api(claim)["guarantees.query"],
    )
    claim["states"][0]["transitions"].append(
        {"target": "report", "expect": {"kind": "trigger"}}
    )
    self.assertNotIn("guarantees.query", solution_tool_api(claim))
    claim["states"][0]["transitions"].pop()
    other = claim["states"][0]["transitions"][1]["expect"]
    other["detail"]["sql"] = {}
    self.assertNotIn("guarantees.query", solution_tool_api(claim))
    other["detail"]["sql"] = {"statement_count": 1, "read_only": False}
    self.assertEqual(
        [{"statement_count": 1, "read_only": False}],
        solution_tool_api(claim)["guarantees.query"],
    )
    other["detail"]["sql"] = {"read_only": 0}
    self.assertNotIn("guarantees.query", solution_tool_api(claim))
    other["detail"]["sql"] = {"read_only": False}
    claim["states"][0]["transitions"][1]["target"] = "dead"
    claim["states"].append({"name": "dead", "final": True, "transitions": []})
    self.assertEqual(
        ["one_complete_read_only_statement"],
        solution_tool_api(claim)["guarantees.query"],
    )
    other["detail"]["sql"] = {"read_only": 0}
    claim["states"][1]["transitions"] = [{"target": "later", "expect": other}]
    claim["states"].append(
        {
            "name": "later",
            "final": False,
            "transitions": [{"target": "done", "expect": success}],
        }
    )
    self.assertNotIn("guarantees.query", solution_tool_api(claim))


def _query_effect():
    effect = {
        "kind": "effect",
        "target": "C59",
        "outcome": "succeeded",
        "detail": {
            "operation": "run",
            "input_types": {
                "name": "string",
                "arguments": "object",
                "nullable_strings": ["session_id"],
            },
            "matches_admitted_instance": True,
            "tool_enabled": True,
            "tool_in_registry": True,
            "sql": {
                "statement_count": 1,
                "read_only": True,
                "cursor_metadata_only": True,
                "uses_full_submitted_sql": True,
                "uses_selected_project": True,
            },
        },
    }
    return effect


def _query_success():
    success = {
        "kind": "output",
        "outcome": "succeeded",
        "detail": {
            "http_outcome": "success",
            "result_types": {"text": "string_or_null", "value": "object"},
            "delivery_mode": "requested",
            "include_submitted_sql": False,
            "retain_result_by": "query_id",
            "bookmark_requires_save": True,
        },
    }
    return success


def _invalid_input():
    invalid = {
        "kind": "output",
        "outcome": "failed",
        "detail": {
            "http_outcome": "invalid_input",
            "provider_dispatched": False,
        },
    }
    return invalid


def _explicit_facts_workflow(effect, invalid, success):
    claim = {
        "initial": "validating",
        "startup": {"required_arguments": ["--socket"]},
        "states": [
            {
                "name": "validating",
                "final": False,
                "transitions": [
                    {"target": "executing", "expect": effect},
                    {"target": "failed", "expect": invalid},
                ],
            },
            {
                "name": "executing",
                "final": False,
                "transitions": [{"target": "done", "expect": success}],
            },
            {"name": "done", "final": True, "transitions": []},
            {"name": "failed", "final": True, "transitions": []},
        ],
    }
    return claim


def check_explicit_facts(self):
    effect = _query_effect()
    success = _query_success()
    invalid = _invalid_input()
    claim = _explicit_facts_workflow(effect, invalid, success)
    facts = solution_tool_api(claim)
    self.assertEqual(
        ["matching_instance"], facts["preconditions.project_binding"]
    )
    self.assertEqual(
        ["one_complete_read_only_statement"], facts["guarantees.query"]
    )
    self.assertEqual(["none"], facts["effects.invalid_input_dispatch"])
    self.assertEqual(["--socket"], facts["interface.cli_required"])
    self.assertEqual(["explicit_save_only"], facts["effects.bookmark"])
    changed = copy.deepcopy(claim)
    detail = changed["states"][0]["transitions"][0]["expect"]["detail"]
    detail["sql"]["read_only"] = False
    del detail["tool_in_registry"]
    changed["states"][1]["transitions"][0]["expect"]["detail"][
        "provider_dispatched"
    ] = False
    del changed["states"][0]["transitions"][1]["expect"]["detail"][
        "provider_dispatched"
    ]
    facts = solution_tool_api(changed)
    self.assertNotEqual(
        ["one_complete_read_only_statement"], facts["guarantees.query"]
    )
    self.assertNotIn("preconditions.tool", facts)
    self.assertNotIn("effects.invalid_input_dispatch", facts)
    changed["states"][1]["transitions"].append(
        {"target": "failed", "expect": invalid}
    )
    with self.assertRaisesRegex(ValueError, "follows provider dispatch"):
        solution_tool_api(changed)


def _inconsistent_operation_workflow():
    workflow = {
        "initial": "start",
        "states": [
            {
                "name": "start",
                "final": False,
                "transitions": [
                    {
                        "target": "done",
                        "expect": {
                            "kind": "trigger",
                            "detail": {"operation": operation},
                        },
                    }
                    for operation in ("POST /tools", "POST /other")
                ],
            },
            {"name": "done", "final": True, "transitions": []},
        ],
    }
    return workflow


def check_inconsistent_operation(self):
    workflow = _inconsistent_operation_workflow()
    facts = _tool_solution(
        {"operations": {"invoke": workflow}}, "POST /tools", None
    )
    self.assertEqual(
        {"conflicting_values": [["POST /tools"], ["POST /other"]]},
        facts["operation"],
    )
