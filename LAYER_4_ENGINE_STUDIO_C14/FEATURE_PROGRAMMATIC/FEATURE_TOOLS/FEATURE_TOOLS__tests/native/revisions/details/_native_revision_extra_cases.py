"""Additional native draft revision cases."""

from dataclasses import replace
from hashlib import sha256

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
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


class NativeRevisionExtraCases:
    def test_task_promotion_rejects_status_change_with_flat_child(self):
        child = self.write("001_TICKETS/TASKS/AN-T-2-TASK--child.md", "AN-T-2")
        _, header, body = child.read_text().split("---", 2)
        metadata = yaml.safe_load(header)
        metadata["context"]["container"] = {"atom": "AN-T-1"}
        child.write_text("---\n" + yaml.safe_dump(metadata) + "---" + body)
        result = create_draft(
            self.selection,
            self.params,
            current_rows=capture_native(self.selection).atoms,
        )
        draft = self.root / result["savedDraft"]["path"]
        before = self.path.read_bytes(), child.read_bytes(), draft.read_bytes()
        with self.assertRaisesRegex(InputError, "container"):
            promote_draft(
                self.selection,
                {
                    "target": {
                        "ref_id": result["savedDraft"]["ref_id"],
                        "version": 2,
                    },
                    "targetStatus": "done",
                },
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertEqual(
            before,
            (self.path.read_bytes(), child.read_bytes(), draft.read_bytes()),
        )

    def test_epic_body_revision_preserves_child_carrier(self):
        epic = self.write(
            "001_TICKETS/TASKS/AN-T-4-EPIC--example.md",
            "AN-T-4",
            template="epic",
        )
        child = self.write(
            (
                "001_TICKETS/TASKS/AN-T-4-EPIC--example/done/"
                "AN-T-5-TASK--example.md"
            ),
            "AN-T-5",
            status="done",
        )
        _, header, body = child.read_text().split("---", 2)
        metadata = yaml.safe_load(header)
        metadata["context"]["container"] = {"atom": "AN-T-4"}
        child.write_text("---\n" + yaml.safe_dump(metadata) + "---" + body)
        before = child.read_bytes()
        result = create_draft(
            self.selection,
            {
                "sourceCurrent": {"ref_id": "AN-T-4", "version": 1},
                "changes": {
                    "body": epic.read_text()
                    .split("---", 2)[2]
                    .replace("Old", "New")
                },
            },
            current_rows=capture_native(self.selection).atoms,
        )
        result = promote_draft(
            self.selection,
            {
                "target": {
                    "ref_id": result["savedDraft"]["ref_id"],
                    "version": 2,
                },
                "targetStatus": "active",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"])
        self.assertEqual(before, child.read_bytes())

    def test_existing_component_lens_can_override_project_whitelist(self):
        path, previous_header = self._component_lens_fixture()
        output = create_draft(
            self.selection,
            {
                "sourceCurrent": {"ref_id": "AN-S-6", "version": 1},
                "changes": {
                    "body": path.read_text()
                    .split("---\n", 2)[2]
                    .replace("Old", "New")
                },
            },
            current_rows=capture_native(self.selection).atoms,
        )
        ref = output["savedDraft"]["ref_id"]
        result = promote_draft(
            self.selection,
            {"target": {"ref_id": ref, "version": 2}, "targetStatus": "ready"},
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"])
        current = next(
            row
            for row in capture_native(self.selection).atoms
            if row["_exact_ref"] == "AN-S-6@2"
        )
        self.assertEqual(
            previous_header["context"], current["header_json"]["context"]
        )
        self.assertIn(b"New", current["_content_bytes"])

    def _component_lens_fixture(self):
        manifest = self.selection.manifest_path
        manifest.write_text(
            manifest.read_text().replace("['DES', 'SPEC']", "['SPEC']")
        )
        self.selection = replace(
            self.selection,
            manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
        )
        component = self.spec(
            "AN-S-7-SPEC-COMPONENT_MANIFEST--unit.md", "AN-S-7", "SPEC", "C0"
        )
        header, body = component.read_text().split("---\n", 2)[1:]
        component_header = yaml.safe_load(header)
        component_header["context"]["template"] = "component_manifest"
        component.write_text(
            "---\n"
            + yaml.safe_dump(component_header)
            + "---\n"
            + body
            + (
                '\n### Component ID\n\nC9\n\n### Lens Whitelist\n\n["DevOps/'
                'RunTime"]\n'
            )
        )
        path = self.spec(
            "UNIT_C9/__DEVOPS/__RUNTIME/AN-S-6-RUNTIME--example.md",
            "AN-S-6",
            "DevOps/RunTime",
        )
        previous_header = next(
            row
            for row in capture_native(self.selection).atoms
            if row["id"] == "AN-S-6"
        )["header_json"]
        return path, previous_header

    def test_rejects_manifest_and_nested_paths(self):
        cases = [
            (self.selection.manifest_path, "AN-S-1"),
            (
                self.spec(
                    "UNIT_C9/__DES/nested/AN-S-9-DES--example.md", "AN-S-9"
                ),
                "AN-S-9",
            ),
            (
                self.spec("UNIT_C9/DES/AN-S-10-DES--example.md", "AN-S-10"),
                "AN-S-10",
            ),
            (
                self.write(
                    "_PMETA/nested/AN-P-9-ACTION--example.md", "AN-P-9"
                ),
                "AN-P-9",
            ),
        ]
        for _path, atom_id in cases:
            with self.subTest(atom_id=atom_id):
                with self.assertRaises(InputError):
                    create_draft(
                        self.selection,
                        {"sourceCurrent": {"ref_id": atom_id, "version": 1}},
                        current_rows=capture_native(self.selection).atoms,
                    )
