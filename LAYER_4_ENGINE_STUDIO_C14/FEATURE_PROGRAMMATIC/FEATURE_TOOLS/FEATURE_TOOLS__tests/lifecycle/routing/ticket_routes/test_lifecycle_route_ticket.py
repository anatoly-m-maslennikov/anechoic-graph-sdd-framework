"""Generated native lifecycle paths; each case uses a fresh project."""

from pathlib import Path
import sys
import unittest


sys.path.insert(
    0,
    str(
        (ENGINE := (TOOLS := Path(__file__).resolve().parents[4]).parents[1])
        / "IWE_CONSOLE_C43"
    ),
)
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
    SourceChanged,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_asset import (
    create_asset,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update_archive import (
    archive_ticket,
    direct_update,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
    change_ticket_status,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle.lifecycle_route_support import (
    LifecycleRouteSupport,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle.routing.ticket_routes import (  # noqa: E402
    _lifecycle_ticket_route_cases as cases,
)


class LifecycleRouteMatrix(
    cases.TicketRouteCases, LifecycleRouteSupport, unittest.TestCase
):
    def test_new_planning_ticket_paths(self):
        for template in ("task", "epic"):
            for contained in (False, True):
                with self.subTest(template=template, contained=contained):
                    self._planning_case(template, contained)

    def _planning_case(self, template, contained):
        project = self.project()

        def rows():
            return capture_native(project).atoms

        container = {"atom": "AN-T-1"} if contained else {"component": "C00"}
        created = create_draft(
            project,
            {
                "newAtom": {
                    "template": template,
                    "container": container,
                    "body": "\n## Summary\n\nExample\n",
                }
            },
            current_rows=rows(),
        )
        self.assertEqual("completed", created["outcome"])
        draft = created["savedDraft"]
        target = {"ref_id": draft["ref_id"], "version": 1}
        for forbidden in ("in_queue", "done", "in_progress"):
            before = self.files(project)
            with self.assertRaises(InputError):
                promote_draft(
                    project,
                    {"target": target, "targetStatus": forbidden},
                    current_rows=rows(),
                )
            self.assertEqual(before, self.files(project))
        published = promote_draft(
            project,
            {"target": target, "targetStatus": "backlog"},
            current_rows=rows(),
        )
        self.assertEqual("backlog", published["artifact"]["status"])
        target = {
            "ref_id": published["artifact"]["ref_id"],
            "version": 1,
        }
        self._assert_planning_transitions(project, rows, target)

    def _assert_planning_transitions(self, project, rows, target):
        for forbidden in ("done", "in_progress"):
            before = self.files(project)
            with self.assertRaises(InputError):
                change_ticket_status(
                    project,
                    {"target": target, "targetStatus": forbidden},
                    current_rows=rows(),
                    check_definition=lambda: None,
                )
            self.assertEqual(before, self.files(project))
        for status in ("in_queue", "done"):
            result = change_ticket_status(
                project,
                {"target": target, "targetStatus": status},
                current_rows=rows(),
                check_definition=lambda: None,
            )
            self.assertEqual("completed", result["outcome"], result)
            self.assertEqual(status, result["artifact"]["status"])

    def test_pmeta_and_spec_reject_ticket_only_routes(self):
        for family, atom_id in (
            ("PROJECT_CONFIG", "AN-P-2"),
            ("SPEC", "AN-S-2"),
        ):
            for contained in (False, True):
                with self.subTest(family=family, contained=contained):
                    self._pmeta_case(family, atom_id, contained)

    def _pmeta_case(self, family, atom_id, contained):
        project = self.project()
        container = {"atom": "AN-T-1"} if contained else {"component": "C00"}
        before = self.files(project)
        for template in (family.lower(),):
            with self.assertRaises(InputError):
                create_asset(
                    project,
                    {
                        "newAtom": {
                            "template": template,
                            "container": container,
                            "body": "\n## Summary\n\nExample\n",
                        }
                    },
                    current_rows=capture_native(project).atoms,
                )
        for operation, params in (
            (
                direct_update,
                {
                    "target": {"ref_id": atom_id, "version": 1},
                    "changes": {"body": "Example"},
                },
            ),
            (
                archive_ticket,
                {"target": {"ref_id": atom_id, "version": 1}},
            ),
        ):
            with self.assertRaises((InputError, SourceChanged)):
                operation(
                    project,
                    params,
                    current_rows=capture_native(project).atoms,
                )
        self.assertEqual(before, self.files(project))
