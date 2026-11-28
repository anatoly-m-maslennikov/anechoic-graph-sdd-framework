import copy
from unittest.mock import patch

from importlib import import_module

_tool_api = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
    "LAYER_2_FORMAL_SPECIFICATION_C94."
    "LAYER_4_SPEC_COMPARISON_C88._package__shared"
)
_tool_solution = _tool_api._tool_solution
check_tool_api_spec = _tool_api.check_tool_api_spec
solution_tool_api = _tool_api.solution_tool_api


def _conflicting_outputs():
    outputs = [
        {
            "kind": "output",
            "outcome": "succeeded",
            "detail": {"http_outcome": "success", "response_format": "json"},
        },
        {
            "kind": "output",
            "outcome": "failed",
            "detail": {
                "http_outcome": "invalid_input",
                "response_format": "text",
            },
        },
        {
            "kind": "output",
            "outcome": "failed",
            "detail": {
                "http_outcome": "internal_error",
                "response_format": "json",
            },
        },
    ]
    return outputs


def _conflicting_workflow(outputs):
    claim = {
        "initial": "start",
        "states": [
            {
                "name": "start",
                "final": False,
                "transitions": [
                    {"target": "done", "expect": output} for output in outputs
                ],
            },
            {"name": "done", "final": True, "transitions": []},
        ],
    }
    return claim


def _matched_directions():
    directions = {
        name: {"status": "matched", "facts": []}
        for name in (
            "manifest_contract",
            "manifest_solution",
            "contract_solution",
        )
    }
    return directions


def check_source_linked_conflict(self):
    outputs = _conflicting_outputs()
    claim = _conflicting_workflow(outputs)
    facts = solution_tool_api(claim)
    self.assertEqual(
        {"conflicting_values": [["json"], ["text"]]},
        facts["interface.response_format"],
    )
    sources = {
        role: {"atom_id": role}
        for role in ("manifest", "contract", "solution")
    }
    model = {role: {"source": source} for role, source in sources.items()}
    compiled = {"claims": {"solution": claim}, "issues": [], "unresolved": []}
    directions = _matched_directions()
    module = (
        "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
        "LAYER_2_FORMAL_SPECIFICATION_C94."
        "LAYER_4_SPEC_COMPARISON_C88.tool_api_spec__pub."
    )
    with (
        patch(module + "load_boundary_model", return_value=model),
        patch(module + "compile_lean", return_value=compiled),
        patch(
            module + "compare_obligations",
            return_value={
                "status": "matched",
                "sources": sources,
                "directions": directions,
            },
        ),
        patch(module + "render_solution"),
    ):
        report = check_tool_api_spec(None, "C45", None, None, None)
    self.assertEqual("conflicting", report["status"])
    self.assertEqual(directions, report["directions"])
    self.assertEqual(sources["solution"], report["issues"][0]["source"])
    self.assertEqual("interface.response_format", report["issues"][0]["field"])


def _error_field_claim():
    claim = {
        "initial": "start",
        "states": [
            {
                "name": "start",
                "final": False,
                "transitions": [
                    {
                        "target": "done",
                        "expect": {
                            "kind": "output",
                            "outcome": "failed",
                            "detail": {
                                "http_outcome": "invalid_input",
                                "response_fields": fields,
                            },
                        },
                    }
                    for fields in (["code"], ["message"], ["code"])
                ],
            },
            {"name": "done", "final": True, "transitions": []},
        ],
    }
    return claim


def check_inconsistent_error_fields(self):
    claim = _error_field_claim()
    self.assertEqual(
        {"conflicting_values": [["code"], ["message"]]},
        solution_tool_api(claim)["error_handling.error_fields"],
    )


def _partial_outcomes_claim(full, output):
    claim = {
        "initial": "start",
        "states": [
            {"name": "start", "final": False, "transitions": [output(full)]},
            {"name": "done", "final": True, "transitions": []},
            {
                "name": "unreachable",
                "final": False,
                "transitions": [output({"status_code": 503})],
            },
        ],
    }
    return claim


def check_partial_outcome_evidence(self):

    def output(detail):
        return {
            "target": "done",
            "expect": {
                "kind": "output",
                "outcome": "succeeded",
                "detail": {"http_outcome": "success", **detail},
            },
        }

    full = {"status_code": 200, "envelope": "result"}
    claim = _partial_outcomes_claim(full, output)
    transitions = claim["states"][0]["transitions"]
    self.assertEqual(
        [200, "result"], solution_tool_api(claim)["outcomes.success"]
    )
    for partial in ({"status_code": 503}, {"envelope": "error"}):
        transitions.append(output(partial))
        self.assertIn(
            "conflicting_values", solution_tool_api(claim)["outcomes.success"]
        )
        transitions.pop()
    transitions.append(output({"status_code": 200}))
    self.assertNotIn("outcomes.success", solution_tool_api(claim))
    transitions.pop()
    transitions.append(output(full))
    self.assertEqual(
        [200, "result"], solution_tool_api(claim)["outcomes.success"]
    )
    for name in ("invalid_input", "internal_error"):
        for transition in transitions:
            transition["expect"]["outcome"] = "failed"
            transition["expect"]["detail"]["http_outcome"] = name
        transitions.append(copy.deepcopy(transitions[0]))
        del transitions[-1]["expect"]["detail"]["envelope"]
        transitions[-1]["expect"]["detail"]["status_code"] = 503
        self.assertIn(
            "conflicting_values", solution_tool_api(claim)[f"outcomes.{name}"]
        )
        transitions.pop()
