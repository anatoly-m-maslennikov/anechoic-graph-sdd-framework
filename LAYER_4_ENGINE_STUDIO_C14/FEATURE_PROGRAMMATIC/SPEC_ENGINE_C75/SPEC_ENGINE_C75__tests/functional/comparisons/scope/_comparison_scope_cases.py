"""Extended comparison-scope cases."""

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.contracts.shape.test_shape_spec import (
    CONTRACT,
    SOLUTION,
)
from .test_comparison_scope import (
    _SHAPES,
    _TOOL,
    _TRACE,
    _compile,
    _fence,
    _response,
    _workflow,
)


def check_shape_comparison_reports_unchecked_logical_outcome(self):
    for kind, values in (
        ("must_effect", [("parser", "called")]),
        ("forbid_effect", ["parser"]),
    ):
        with self.subTest(kind=kind):
            io = {
                "class_shapes": _SHAPES,
                "server": {"compile": {"outcomes": {"done": {kind: values}}}},
            }
            report = self.check(
                _fence("python shape", CONTRACT),
                _fence("python shape", SOLUTION),
                {"io": io},
            )
            self.assertEqual(
                "matched", report["translation"]["status"], report
            )
            self.assertEqual("unresolved", report["status"], report)
            self.assertEqual(
                "unresolved",
                report["directions"]["manifest_solution"]["status"],
            )
            self.assertIn(
                "boundaries.io.server.compile.outcomes.done",
                {gap["field"] for gap in report["unresolved"]},
            )


def _invalid_states(after, provider):
    states = {
        "start": {
            "on": {
                "request": {
                    "to": "routing",
                    "expect": {
                        "kind": "trigger",
                        "detail": {"operation": "POST /tools"},
                    },
                }
            }
        },
        "routing": {
            "on": {
                "reject": _response(
                    "invalid_input",
                    400,
                    "typed_error",
                    provider_dispatched=False,
                ),
                "dispatch": {
                    "to": "called",
                    "expect": {
                        "kind": "effect",
                        "target": provider,
                        "outcome": "succeeded",
                    },
                },
            }
        },
        "called": {"on": after},
    }
    return states


def check_invalid_input_dispatch_is_checked_on_each_reachable_path(self):
    tool = (
        _TOOL[:-1]
        + ", checks={'effects': {'invalid_input_dispatch': 'none'}})"
    )
    contract = (
        _fence("python contract", tool) + "\n" + _fence("python trace", _TRACE)
    )
    responses = {
        "success": _response("success", 200, "result"),
        "internal_error": _response("internal_error", 500, "typed_error"),
    }
    for provider, late, expected in (
        ("C59", None, "matched"),
        ("C59", {}, "conflicting"),
        ("C59", {"provider_dispatched": True}, "conflicting"),
        ("C8", {}, "unresolved"),
    ):
        with self.subTest(provider=provider, late=late):
            after = dict(responses)
            if late is not None:
                after["late_reject"] = _response(
                    "invalid_input", 400, "typed_error", **late
                )
            states = _invalid_states(after, provider)
            solution = _workflow("invoke", states) + "\n" + _compile()
            report = self.check(
                contract,
                solution,
                {"state": {"reads": [], "writes": []}},
                action="invoke",
            )
            self.assertEqual("compared", report["outcome"], report)
            self.assertEqual(expected, report["status"])
            fact = next(
                row
                for row in report["evidence"]["coverage"]
                if row["key"] == "effects.invalid_input_dispatch"
            )
            self.assertEqual(expected, fact["status"])


def _precondition_states():
    states = {
        "start": {
            "on": {
                "request": {
                    "to": "routing",
                    "expect": {
                        "kind": "trigger",
                        "detail": {"operation": "POST /tools"},
                    },
                }
            }
        },
        "routing": {
            "on": {"reject": _response("invalid_input", 400, "typed_error")}
        },
        "called": {
            "on": {
                "success": _response("success", 200, "result"),
                "error": _response("internal_error", 500, "typed_error"),
            }
        },
    }
    return states


def check_provider_precondition(
    self,
):
    contract = _fence(
        "python contract",
        _TOOL[:-1] + ", checks={'preconditions': "
        "{'project_binding': 'matching_instance'}})",
    )
    for detail, status in (
        ({"matches_admitted_instance": True}, "matched"),
        ({}, "unresolved"),
        ({"matches_admitted_instance": False}, "conflicting"),
    ):
        with self.subTest(detail=detail):
            states = _precondition_states()
            for name, evidence in (
                ("primary", {"matches_admitted_instance": True}),
                ("alternate", detail),
            ):
                states["routing"]["on"][name] = {
                    "to": "called",
                    "expect": {
                        "kind": "effect",
                        "target": "C59",
                        "outcome": "succeeded",
                        "detail": evidence,
                    },
                }
            report = self.check(
                contract,
                _workflow("invoke", states),
                {"state": {"reads": [], "writes": []}},
            )
            self.assertEqual("compared", report["outcome"], report)
            fact = next(
                row
                for row in report["evidence"]["coverage"]
                if row["key"] == "preconditions.project_binding"
            )
            self.assertEqual(status, fact["status"])
            self.assertEqual(status, report["status"])


def _query_states(evidence, operation):
    states = {
        "start": {
            "on": {
                "request": {
                    "to": "routing",
                    "expect": {
                        "kind": "trigger",
                        "detail": {"operation": "POST /tools"},
                    },
                }
            }
        },
        "routing": {
            "on": {
                "reject": _response("invalid_input", 400, "typed_error"),
                "dispatch": {
                    "to": "called",
                    "expect": {
                        "kind": "effect",
                        "target": "C59",
                        "outcome": "succeeded",
                        "detail": {
                            "sql": evidence,
                            "operation": operation,
                            "matches_admitted_instance": True,
                        },
                    },
                },
            }
        },
        "called": {
            "on": {
                "success": _response("success", 200, "result"),
                "error": _response("internal_error", 500, "typed_error"),
            }
        },
    }
    return states


def _query_inputs():
    sql = {
        "statement_count": 1,
        "read_only": True,
        "cursor_metadata_only": True,
    }
    complete = {
        **sql,
        "uses_full_submitted_sql": True,
        "uses_selected_project": True,
    }
    return sql, complete


def check_query_guarantee_requires_whole_sql_and_selected_project(self):
    contract = _fence(
        "python contract",
        _TOOL[:-1] + ", checks={'guarantees': "
        "{'query': 'one_complete_read_only_statement'}})",
    )
    sql, complete = _query_inputs()
    for operation, evidence, status in (
        ("run", complete, "matched"),
        ("run", sql, "unresolved"),
        ("run", {**sql, "uses_full_submitted_sql": True}, "unresolved"),
        ("operation", complete, "unresolved"),
        (
            "run",
            {**complete, "uses_full_submitted_sql": False},
            "conflicting",
        ),
        (
            "run",
            {**complete, "uses_selected_project": False},
            "conflicting",
        ),
        ("run", {**sql, "read_only": False}, "conflicting"),
    ):
        with self.subTest(operation=operation, evidence=evidence):
            states = _query_states(evidence, operation)
            report = self.check(
                contract,
                _workflow("invoke", states),
                {"state": {"reads": [], "writes": []}},
            )
            self.assertEqual("compared", report["outcome"], report)
            fact = next(
                row
                for row in report["evidence"]["coverage"]
                if row["key"] == "guarantees.query"
            )
            self.assertEqual(status, fact["status"])
            self.assertEqual(status, report["status"])
