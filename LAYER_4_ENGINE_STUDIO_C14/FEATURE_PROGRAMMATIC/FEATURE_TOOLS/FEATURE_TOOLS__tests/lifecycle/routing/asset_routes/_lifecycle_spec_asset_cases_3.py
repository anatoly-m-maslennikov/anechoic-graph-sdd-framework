"""Native project SPEC and asset route scenarios."""

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
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_asset import (
    create_asset,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update_archive import (
    archive_ticket,
    direct_update,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
    change_ticket_status,
)


class LifecycleSpecAssetCases3:
    def test_asset_body_update_current_and_draft(self):
        for template in (
            "analysis_report",
            "work_report",
            "work_log",
            "spec_proposal",
        ):
            for situation in ("current", "draft"):
                for contained in (False, True):
                    with self.subTest(
                        route="direct_update",
                        family="TKT",
                        template=template,
                        situation=situation,
                        contained=contained,
                    ):
                        self._asset_update_case(template, situation, contained)

    def _asset_update_case(self, template, situation, contained):
        project = self.project()
        header, path, ref = self._write_asset_source(
            project, template, situation, contained
        )
        body = "\n## Summary\n\nExample\n\n## Details\n\nNew\n"
        before = self.files(project)
        with self.assertRaises(InputError):
            direct_update(
                project,
                {
                    "target": {"ref_id": ref, "version": 1},
                    "changes": {"body": body.replace("Example", "Changed")},
                },
                current_rows=capture_native(project).atoms,
            )
        self.assertEqual(before, self.files(project))
        result = direct_update(
            project,
            {
                "target": {"ref_id": ref, "version": 1},
                "changes": {"body": body},
            },
            current_rows=capture_native(project).atoms,
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(
            ["modify"],
            [effect["operation"] for effect in result["effects"]],
        )
        capture = capture_native(project)
        self.assertFalse(capture.errors, capture.errors)
        row = next(
            row
            for row in capture.atoms
            if row["_exact_ref"]
            == (ref if situation == "draft" else ref + "@1")
        )
        self.assertEqual(header, row["header_json"])
        self.assertEqual(body.encode(), row["_content_bytes"])
        self.assertEqual(
            path.relative_to(project.root).as_posix(),
            row["source_path"],
        )

    def _write_asset_source(self, project, template, situation, contained):
        container = {"atom": "AN-T-1"} if contained else {"component": "C00"}
        header = canonical_native_header(
            {
                "identity": {"atom_id": "AN-T-2"},
                "context": {
                    "container": container,
                    "template": template,
                },
                "state": {
                    "status": "draft" if situation == "draft" else "in_queue",
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
            + "---\n\n## Summary\n\nExample\n\n## Details\n\nOld\n"
        )
        ref = "AN-T-2@1-draft" if situation == "draft" else "AN-T-2"
        return header, path, ref

    def test_asset_create_is_direct_in_queue(self):
        for template in (
            "analysis_report",
            "work_report",
            "work_log",
            "spec_proposal",
        ):
            for contained in (False, True):
                with self.subTest(template=template, contained=contained):
                    self._asset_create_case(template, contained)

    def _asset_create_case(self, template, contained):
        project = self.project()
        container = {"atom": "AN-T-1"} if contained else {"component": "C00"}
        result = create_asset(
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
        self.assertEqual("completed", result["outcome"])
        self.assertEqual("in_queue", result["artifact"]["status"])
        path = project.root / result["artifact"]["path"]
        self.assertTrue(path.is_file())
        self.assertNotIn("01_draft", path.parts)
        target = {
            "ref_id": result["artifact"]["ref_id"],
            "version": 1,
        }
        self._assert_asset_status(project, contained, target)

    def _assert_asset_status(self, project, contained, target):
        before = self.files(project)
        with self.assertRaises(InputError):
            archive_ticket(
                project,
                {"target": target},
                current_rows=capture_native(project).atoms,
            )
        self.assertEqual(before, self.files(project))
        if contained:
            before = self.files(project)
            with self.assertRaises(InputError):
                change_ticket_status(
                    project,
                    {"target": target, "targetStatus": "complete"},
                    current_rows=capture_native(project).atoms,
                    check_definition=lambda: None,
                )
            self.assertEqual(before, self.files(project))
        status = "done" if contained else "complete"
        result = change_ticket_status(
            project,
            {"target": target, "targetStatus": status},
            current_rows=capture_native(project).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(status, result["artifact"]["status"])
        if not contained:
            self.assertIn(
                "08_complete",
                (project.root / result["artifact"]["path"]).parts,
            )
