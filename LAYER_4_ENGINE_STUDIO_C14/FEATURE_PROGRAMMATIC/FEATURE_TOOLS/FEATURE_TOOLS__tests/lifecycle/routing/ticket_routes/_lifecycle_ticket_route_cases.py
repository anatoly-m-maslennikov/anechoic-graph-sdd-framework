"""Ticket revision and issue route scenarios."""

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_header__pub import (
    canonical_native_header,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_placement__pub import (
    native_carrier_path,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
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


class TicketRouteCases:
    def test_revision_and_archived_routes(self):
        for template in ("task", "epic"):
            for contained in (False, True):
                with self.subTest(template=template, contained=contained):
                    self._revision_case(template, contained)

    def _revision_case(self, template, contained):
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
        draft = created["savedDraft"]
        first = promote_draft(
            project,
            {
                "target": {
                    "ref_id": draft["ref_id"],
                    "version": 1,
                },
                "targetStatus": "backlog",
            },
            current_rows=rows(),
        )
        current = {
            "ref_id": first["artifact"]["ref_id"],
            "version": 1,
        }
        before = self.files(project)
        with self.assertRaises(InputError):
            direct_update(
                project,
                {
                    "target": current,
                    "changes": {"body": "\n## Summary\n\nExample\n"},
                },
                current_rows=rows(),
            )
        self.assertEqual(before, self.files(project))
        self._assert_revision_steps(project, rows, current)

    def _assert_revision_steps(self, project, rows, current):
        revision = create_draft(
            project,
            {"sourceCurrent": current},
            current_rows=rows(),
        )
        self.assertEqual("completed", revision["outcome"])
        next_draft = revision["savedDraft"]
        before = self.files(project)
        with self.assertRaises(InputError):
            archive_ticket(
                project,
                {
                    "target": {
                        "ref_id": next_draft["ref_id"],
                        "version": 2,
                    }
                },
                current_rows=rows(),
            )
        self.assertEqual(before, self.files(project))
        self._assert_revision_published(project, rows, next_draft, current)

    def _assert_revision_published(self, project, rows, next_draft, current):
        published = promote_draft(
            project,
            {
                "target": {
                    "ref_id": next_draft["ref_id"],
                    "version": 2,
                },
                "targetStatus": "backlog",
            },
            current_rows=rows(),
        )
        self.assertEqual("completed", published["outcome"], published)
        before = self.files(project)
        with self.assertRaises(InputError):
            create_draft(
                project,
                {
                    "sourceCurrent": {
                        "ref_id": current["ref_id"] + "@1",
                        "version": 1,
                    }
                },
                current_rows=rows(),
            )
        self.assertEqual(before, self.files(project))

    def test_issue_current_transitions_and_new_route_rejection(self):
        for template in (
            "problem",
            "question",
            "code_spec_mismatch",
            "opportunity",
        ):
            for contained in (False, True):
                with self.subTest(template=template, contained=contained):
                    self._issue_case(template, contained)

    def _issue_case(self, template, contained):
        project = self.project()

        def rows():
            return capture_native(project).atoms

        container = {"atom": "AN-T-1"} if contained else {"component": "C00"}
        before = self.files(project)
        with self.assertRaises(InputError):
            create_draft(
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
        self.assertEqual(before, self.files(project))
        self._write_issue(project, container, template, contained)
        target = {"ref_id": "AN-T-2", "version": 1}
        before = self.files(project)
        with self.assertRaises(InputError):
            archive_ticket(project, {"target": target}, current_rows=rows())
        self.assertEqual(before, self.files(project))
        for status in ("resolved", "done", "in_progress"):
            before = self.files(project)
            with self.assertRaises(InputError):
                change_ticket_status(
                    project,
                    {"target": target, "targetStatus": status},
                    current_rows=rows(),
                    check_definition=lambda: None,
                )
            self.assertEqual(before, self.files(project))
        for status in ("in_queue", "resolved"):
            result = change_ticket_status(
                project,
                {"target": target, "targetStatus": status},
                current_rows=rows(),
                check_definition=lambda: None,
            )
            self.assertEqual("completed", result["outcome"], result)
            self.assertEqual(status, result["artifact"]["status"])

    def _write_issue(self, project, container, template, contained):
        header = canonical_native_header(
            {
                "identity": {"atom_id": "AN-T-2"},
                "context": {
                    "container": container,
                    "template": template,
                },
                "state": {
                    "status": "backlog",
                    "version": 1,
                    "updated_at": "2026-01-01",
                },
            }
        )
        owner = project.control_root / "001_TICKETS/TASKS/AN-T-1-TASK--owner"
        path = native_carrier_path(
            header,
            "Example",
            project_root=project.control_root,
            owner_directory=owner if contained else project.control_root,
            owner_template="task" if contained else None,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "---\n"
            + yaml.safe_dump(header, sort_keys=False)
            + "---\n\n## Summary\n\nExample\n"
        )
