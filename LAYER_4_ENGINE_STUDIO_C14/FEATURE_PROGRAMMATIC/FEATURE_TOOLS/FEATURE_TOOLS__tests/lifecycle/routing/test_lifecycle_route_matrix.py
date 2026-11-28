"""Generated native lifecycle paths; each case uses a fresh project."""

import json
import tempfile
import time
import unittest


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    ATOM_LIFECYCLE.NATIVE_LIFECYCLE.\
    NATIVE_LIFECYCLE__shared import (
    LIFECYCLE_TOOLS,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__tests.lifecycle.lifecycle_route_support import (
    LifecycleRouteSupport,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle.routing import (
    _lifecycle_grid_cases_1 as cases1,
    _lifecycle_grid_cases_2 as cases2,
    _lifecycle_grid_cases_3 as cases3,
)

LIFECYCLE_TEMPLATES = {
    "TKT": (
        "task",
        "epic",
        "problem",
        "question",
        "code_spec_mismatch",
        "opportunity",
        "analysis_report",
        "work_report",
        "work_log",
        "spec_proposal",
    ),
    "SPEC": (
        None,
        "DECISION",
        "PKG",
        "POLICY",
        "action",
        "component_contract",
        "project_contract",
        "component_manifest",
        "project_goal",
        "project_manifest",
        "contract",
        "step",
        "workflow",
        "axiom",
        "applicable_principle",
    ),
    "PROJECT_CONFIG": ("action", "step", "workflow", None),
}
LIFECYCLE_ROUTES = (
    "create_draft",
    "update",
    "create_asset",
    "direct_update",
    "promote_draft",
    "change_status",
    "archive",
)


def lifecycle_cases():
    for family, template in (
        (family, template)
        for family, templates in LIFECYCLE_TEMPLATES.items()
        for template in templates
    ):
        for situation in ("new", "current", "draft", "archived"):
            for contained in (False, True):
                for route in LIFECYCLE_ROUTES:
                    yield {
                        "route": route,
                        "family": family,
                        "template": template,
                        "situation": situation,
                        "contained": contained,
                    }


def lifecycle_transition_cases():
    cases = []
    for template in ("task", "epic"):
        cases.extend(
            {
                "route": "change_status",
                "family": "TKT",
                "template": template,
                "situation": "current",
                "contained": False,
                "source_status": source,
                "target_status": target,
            }
            for source, target in (
                ("backlog", "in_queue"),
                ("in_queue", "done"),
                ("in_queue", "canceled"),
            )
        )
    _add_issue_transitions(cases)
    _add_asset_transitions(cases)
    return cases


def _add_issue_transitions(cases):
    for template in (
        "problem",
        "question",
        "code_spec_mismatch",
        "opportunity",
    ):
        cases.extend(
            {
                "route": "change_status",
                "family": "TKT",
                "template": template,
                "situation": "current",
                "contained": False,
                "source_status": source,
                "target_status": target,
            }
            for source, target in (
                ("in_queue", "resolved"),
                ("in_queue", "canceled"),
            )
        )


def _add_asset_transitions(cases):
    for template in (
        "analysis_report",
        "work_report",
        "work_log",
        "spec_proposal",
    ):
        cases.append(
            {
                "route": "change_status",
                "family": "TKT",
                "template": template,
                "situation": "current",
                "contained": False,
                "source_status": "in_queue",
                "target_status": "complete",
            }
        )


class LifecycleRouteMatrix(
    cases1.LifecycleGridCases1,
    cases2.LifecycleGridCases2,
    cases3.LifecycleGridCases3,
    LifecycleRouteSupport,
    unittest.TestCase,
):
    def test_generated_route_grid(self):
        from unittest.mock import patch

        body = (
            "\n## Summary\n\nExample\n\n## Guarantee\n\nThe graph includes "
            "imports.\n"
        )
        changed = body + "\nMore detail.\n"
        assets = {
            "analysis_report",
            "work_report",
            "work_log",
            "spec_proposal",
        }
        project_specs = {"axiom", "applicable_principle", "project_contract"}
        cases = list(lifecycle_cases())
        self.assertEqual(1624, len(cases))
        cases.extend(lifecycle_transition_cases())
        self.assertEqual(1642, len(cases))
        self.assertEqual(
            set(LIFECYCLE_ROUTES),
            {name.removeprefix("atom_lifecycle_") for name in LIFECYCLE_TOOLS},
        )
        with patch(
            (
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.NATIVE_LIFECYCLE.native_workflow_definition.bind_status_specifications'
            ),
            return_value=lambda: None,
        ):
            for case in cases:
                self._report_grid_case(
                    case, body, changed, assets, project_specs
                )

    def _grid_source_status(self, case):
        source_status = case.get(
            "source_status",
            (
                {
                    "new": "none",
                    "current": "in_queue",
                    "draft": "draft",
                    "archived": "archived",
                }[case["situation"]]
                if case["family"] == "TKT"
                else {
                    "new": "none",
                    "current": "active"
                    if case["route"] == "archive"
                    else "ready",
                    "draft": "draft",
                    "archived": "archived",
                }[case["situation"]]
                if case["family"] == "SPEC"
                else {
                    "new": "none",
                    "current": "active",
                    "draft": "draft",
                    "archived": "archived",
                }[case["situation"]]
            ),
        )
        return source_status

    def _grid_target_status(self, case, source_status):
        target_status = case.get(
            "target_status",
            {
                "create_draft": "draft",
                "update": "draft",
                "create_asset": "in_queue",
                "direct_update": source_status,
                "promote_draft": {
                    "TKT": "backlog",
                    "SPEC": "ready",
                    "PROJECT_CONFIG": "active",
                }[case["family"]],
                "change_status": "active"
                if case["family"] == "SPEC"
                else (
                    "resolved"
                    if case["template"]
                    in {
                        "problem",
                        "question",
                        "code_spec_mismatch",
                        "opportunity",
                    }
                    else "done"
                ),
                "archive": "archived",
            }[case["route"]],
        )
        return target_status

    def _report_grid_case(self, case, body, changed, assets, project_specs):
        source_status = self._grid_source_status(case)
        target_status = self._grid_target_status(case, source_status)
        expected = self._grid_expected(case, assets, project_specs)
        started = time.monotonic()
        outcome = "FAIL"
        actual = "not_observed"
        result = self._outcome.result
        prior_failures = len(result.failures) + len(result.errors)
        try:
            with (
                self.subTest(**case),
                tempfile.TemporaryDirectory() as directory,
            ):
                actual = self._run_grid_case(
                    case,
                    directory,
                    body,
                    changed,
                    assets,
                    project_specs,
                )
            outcome = (
                "PASS"
                if prior_failures == len(result.failures) + len(result.errors)
                else "FAIL"
            )
        finally:
            elapsed = time.monotonic() - started
            report = {
                **case,
                "source_status": source_status,
                "target_status": target_status,
                "expected": "accepted" if expected else "rejected",
                "actual": actual,
                "result": outcome,
                "elapsed_seconds": round(elapsed, 6),
                "coverage": "transition" if expected else "negative_case",
            }
            print(json.dumps(report, sort_keys=True))
