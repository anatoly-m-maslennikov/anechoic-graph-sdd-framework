import copy
import tempfile
from pathlib import Path
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from importlib import import_module

from ...contracts.cli.test_cli_spec import _carrier
from ...workflows.manifest.test_manifest_child_delegation import _manifest

_tool_api = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
    "LAYER_2_FORMAL_SPECIFICATION_C94."
    "LAYER_4_SPEC_COMPARISON_C88._package__shared"
)
_tool_solution = _tool_api._tool_solution
check_tool_api_spec = _tool_api.check_tool_api_spec
solution_tool_api = _tool_api.solution_tool_api


def _delivery_success():
    success = {
        "http_outcome": "success",
        "status_code": 200,
        "envelope": "result",
        "result_types": {"text": "string_or_null", "value": "object"},
        "delivery_mode": "requested",
        "include_submitted_sql": False,
        "retain_result_by": "query_id",
        "bookmark_requires_save": True,
    }
    return success


def _delivery_outputs(failure, success):
    outputs = [
        {"kind": "output", "outcome": outcome, "detail": copy.deepcopy(detail)}
        for outcome, detail in [
            ("succeeded", success),
            ("succeeded", success),
            ("failed", failure),
            ("failed", failure),
        ]
    ]
    return outputs


def _delivery_workflow(outputs):
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


def _delivery_expected():
    expected = {
        "output_format.text": ["string_or_null"],
        "output_format.value": ["object"],
        "guarantees.query_output": [
            "requested_delivery_without_submitted_sql"
        ],
        "effects.query_result": ["retained"],
        "effects.bookmark": ["explicit_save_only"],
        "error_handling.internal_message": ["internal error"],
    }
    return expected


def _delivery_contract(expected):
    contract = {
        "operation": "POST /tools",
        "facts": list(expected.items()),
        "outcomes": [
            ("success", 200, "result"),
            ("internal_error", 500, "error"),
        ],
    }
    return contract


def _check_delivery(self, outputs, expected):
    def statuses():
        report = check_tool_api_spec(None, "C45", None, None, None)
        return {
            fact["key"]: fact["status"]
            for fact in report["directions"]["contract_solution"]["facts"]
        }

    actual = statuses()
    self.assertTrue(all((actual[key] == "matched" for key in expected)))
    outputs[1]["detail"] = {
        "http_outcome": "success",
        "status_code": 200,
        "envelope": "result",
    }
    outputs[3]["detail"] = {
        "http_outcome": "internal_error",
        "status_code": 500,
        "envelope": "error",
    }
    actual = statuses()
    self.assertTrue(all((actual[key] == "unresolved" for key in expected)))
    outputs[0]["detail"]["delivery_mode"] = "wrong"
    del outputs[0]["detail"]["include_submitted_sql"]
    outputs[2]["detail"]["message"] = "wrong"
    actual = statuses()
    self.assertEqual("conflicting", actual["guarantees.query_output"])
    self.assertEqual("conflicting", actual["error_handling.internal_message"])


def check_public_delivery(self):
    sources = {
        role: {"source": {"atom_id": role}}
        for role in ("manifest", "contract", "solution")
    }
    success = _delivery_success()
    failure = {
        "http_outcome": "internal_error",
        "status_code": 500,
        "envelope": "error",
        "message": "internal error",
    }
    outputs = _delivery_outputs(failure, success)
    workflow = _delivery_workflow(outputs)
    expected = _delivery_expected()
    contract = _delivery_contract(expected)
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
        _check_delivery(self, outputs, expected)


def _terminal_machine(transitions):
    machine = {
        "id": "g",
        "initial": "start",
        "states": {
            "start": {
                "on": {
                    "request": {
                        "to": "serve",
                        "expect": {
                            "kind": "trigger",
                            "detail": {"operation": "POST /tools"},
                        },
                    }
                }
            },
            "serve": {"on": transitions},
            "done": {"type": "final"},
        },
    }
    return machine


def _terminal_manifest(body, contract, root):
    manifest = _manifest(
        root,
        "AN-S-1",
        "C1",
        "C2",
        body("python contract", contract),
        {"state": {"reads": [], "writes": []}},
    )
    return manifest


def _claim_body(language, source):
    return f"## Claim\n\n### Formal Claim\n\n```{language}\n{source}\n```\n"


def _terminal_edge(outcome, name, status, envelope):
    return {
        "to": "done",
        "expect": {
            "kind": "output",
            "outcome": outcome,
            "detail": {
                "http_outcome": name,
                "status_code": status,
                "envelope": envelope,
                "response_format": "json",
            },
        },
    }


def _check_terminals(self, contract, transitions, machine):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        manifest = _terminal_manifest(_claim_body, contract, root)
        for terminal in (
            None,
            {
                "kind": "output",
                "outcome": "partial",
                "detail": {"status_code": 503, "response_format": "json"},
            },
            {"kind": "effect", "target": "query", "outcome": "skipped"},
        ):
            if terminal is not None:
                transitions["incomplete"] = {"to": "done", "expect": terminal}
            source = (
                "component_workflow(component='C2', action='invoke', "
                f"machine={machine!r})"
            )
            solution = _carrier(
                root,
                "AN-S-2",
                "solution",
                "C2",
                "{ANSWERS: [AN-S-1@1]}",
                _claim_body("python", source),
            )
            report = verify_formal_chain(root, "C2", manifest, solution)
            self.assertEqual(
                "matched" if terminal is None else "unresolved",
                report["status"],
            )
            if terminal is not None:
                self.assertTrue(
                    any(
                        (
                            row["field"] == "http_outcome"
                            for row in report["unresolved"]
                        )
                    )
                )


def check_unclassified_terminal(self):

    contract = (
        "declare_tool_api_contract(operation='POST /tools', "
        "outcomes={'success': (200, 'result'), "
        "'invalid_input': (400, 'typed_error'), "
        "'internal_error': (500, 'typed_error')}, "
        "checks={'interface': {'response_format': 'json'}})"
    )

    transitions = {
        "good": _terminal_edge("succeeded", "success", 200, "result"),
        "invalid": _terminal_edge(
            "failed", "invalid_input", 400, "typed_error"
        ),
        "failure": _terminal_edge(
            "failed", "internal_error", 500, "typed_error"
        ),
    }
    machine = _terminal_machine(transitions)
    _check_terminals(self, contract, transitions, machine)
