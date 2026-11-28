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


def _partial_outcome_workflow(output):
    workflow = {
        "initial": "start",
        "states": [
            {
                "name": "start",
                "final": False,
                "transitions": [{"target": "done", "expect": output}],
            },
            {"name": "done", "final": True, "transitions": []},
        ],
    }
    return workflow


def check_partial_contract_outcome(self):
    sources = {
        role: {"source": {"atom_id": role}}
        for role in ("manifest", "contract", "solution")
    }
    output = {
        "kind": "output",
        "outcome": "succeeded",
        "detail": {"http_outcome": "success"},
    }
    workflow = _partial_outcome_workflow(output)
    contract = {
        "profile": "tool_api",
        "operation": "POST /tools",
        "facts": [],
        "outcomes": [("success", 200, "result")],
    }
    compiled = {
        "claims": {"contract": contract, "solution": workflow},
        "issues": [],
        "unresolved": [],
    }
    module = (
        "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
        "LAYER_2_FORMAL_SPECIFICATION_C94."
        "LAYER_4_SPEC_COMPARISON_C88.tool_api_spec__pub."
    )
    with (
        patch(module + "load_boundary_model", return_value=sources),
        patch(module + "compile_lean", return_value=compiled),
        patch(module + "render_solution"),
    ):
        for detail, status in (
            ({"status_code": 503}, "conflicting"),
            ({"status_code": 200}, "unresolved"),
            ({"envelope": "other"}, "conflicting"),
            ({"status_code": 200, "envelope": "result"}, "matched"),
        ):
            output["detail"] = {"http_outcome": "success", **detail}
            report = check_tool_api_spec(None, "C45", None, None, None)
            facts = report["directions"]["contract_solution"]["facts"]
            outcome = next(
                (fact for fact in facts if fact["key"] == "outcomes.success")
            )
            self.assertEqual(status, outcome["status"])


def _terminal_outputs(full):
    outputs = [
        {
            "kind": "output",
            "outcome": "succeeded",
            "detail": copy.deepcopy(full),
        }
        for _ in range(2)
    ]
    return outputs


def _terminal_workflow(outputs):
    workflow = {
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
    return workflow


def _terminal_contract():
    contract = {
        "operation": "POST /tools",
        "facts": [
            ("interface.response_format", ["json"]),
            ("output_format.result_fields", ["value"]),
        ],
        "outcomes": [("success", 200, "result")],
    }
    return contract


def _terminal_cases(full):
    cases = [
        ({"status_code": 503}, "outcomes.success", "conflicting"),
        (
            {"status_code": 200, "envelope": "result"},
            "outcomes.success",
            "unresolved",
        ),
        (
            {
                "http_outcome": "success",
                "status_code": 200,
                "envelope": "result",
            },
            "interface.response_format",
            "unresolved",
        ),
        (
            {
                "http_outcome": "success",
                "status_code": 200,
                "envelope": "result",
            },
            "output_format.result_fields",
            "unresolved",
        ),
        (
            {**full, "response_format": "text"},
            "interface.response_format",
            "conflicting",
        ),
        (full, "output_format.result_fields", "matched"),
    ]
    return cases


def check_terminal_branches(self):
    sources = {
        role: {"source": {"atom_id": role}}
        for role in ("manifest", "contract", "solution")
    }
    full = {
        "http_outcome": "success",
        "status_code": 200,
        "envelope": "result",
        "response_format": "json",
        "response_fields": ["value"],
    }
    outputs = _terminal_outputs(full)
    workflow = _terminal_workflow(outputs)
    contract = _terminal_contract()
    compiled = {
        "claims": {"contract": contract, "solution": workflow},
        "issues": [],
        "unresolved": [],
    }
    module = (
        "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
        "LAYER_2_FORMAL_SPECIFICATION_C94."
        "LAYER_4_SPEC_COMPARISON_C88.tool_api_spec__pub."
    )
    with (
        patch(module + "load_boundary_model", return_value=sources),
        patch(module + "compile_lean", return_value=compiled),
        patch(module + "render_solution"),
    ):
        cases = _terminal_cases(full)
        for detail, key, status in cases:
            outputs[1]["detail"] = detail
            report = check_tool_api_spec(None, "C45", None, None, None)
            facts = report["directions"]["contract_solution"]["facts"]
            self.assertEqual(
                status,
                next((fact["status"] for fact in facts if fact["key"] == key)),
            )


def _unclassified_failure_claim():
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
                            "detail": detail,
                        },
                    }
                    for detail in (
                        {
                            "http_outcome": "invalid_input",
                            "response_format": "json",
                        },
                        {"response_format": "text"},
                    )
                ],
            },
            {"name": "done", "final": True, "transitions": []},
        ],
    }
    return claim


def check_unclassified_failure(self):
    claim = _unclassified_failure_claim()
    self.assertEqual(
        {"conflicting_values": [["json"], ["text"]]},
        solution_tool_api(claim)["interface.response_format"],
    )
