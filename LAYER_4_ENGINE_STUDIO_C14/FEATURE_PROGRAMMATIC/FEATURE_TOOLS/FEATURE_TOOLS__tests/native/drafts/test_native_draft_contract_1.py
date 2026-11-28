from dataclasses import replace
from pathlib import Path
from unittest.mock import NonCallableMock
import sys
import unittest

import yaml

sys.path.insert(
    0,
    str(
        (ENGINE := (TOOLS := Path(__file__).resolve().parents[3]).parents[1])
        / "IWE_CONSOLE_C43"
    ),
)
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)


import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.drafts.test_native_lifecycle_draft as fixtures


class ComponentContractLifecycleTests(
    fixtures.ComponentContractLifecycleTests, unittest.TestCase
):
    def _revision_snapshot(self):
        return {
            "model_sha256": "model",
            "project": {"ref": "p", "sha256": "h"},
            "components": {
                "C9": {
                    "parent": "C00",
                    "ref": "r",
                    "sha256": "h",
                    "fields": {"name": "Unit"},
                    "source_path": self.record.source_path,
                }
            },
        }

    def existing_contract(self, status):
        directory = {"draft": "01_draft", "ready": "02_ready", "active": ""}[
            status
        ]
        suffix = "@1-draft" if status == "draft" else ""
        path = (
            self.control
            / "UNIT_C9"
            / directory
            / (
                "AN-S-5"
                f"{suffix}"
                "-DES-COMPONENT_CONTRACT--import-graph-contract.md"
            )
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {
            "atom_family": "SPEC",
            "atom_id": "AN-S-5",
            "container": {"component": "C9"},
            "tier": 0,
            "context": {"template": "component_contract", "lens": "DES"},
            "state": {
                "status": status,
                "version": 1,
                "updated_at": "2026-01-01",
            },
        }
        path.write_text("---\n" + yaml.safe_dump(header) + "---\n" + self.body)
        return path

    def test_rejects_standalone_creation_revision_and_publication(self):
        error = "Add the Component Contract to the Component Manifest"
        with self.assertRaisesRegex(InputError, error):
            self.create()
        self.assertFalse((self.control / "UNIT_C9/01_draft").exists())
        draft = self.existing_contract("draft")
        original = draft.read_bytes()
        with self.assertRaisesRegex(InputError, error):
            self.promote("AN-S-5@1-draft", 1)
        self.assertEqual(original, draft.read_bytes())
        draft.unlink()
        active = self.existing_contract("active")
        original = active.read_bytes()
        with self.assertRaisesRegex(InputError, error):
            create_draft(
                self.selection,
                {"sourceCurrent": {"ref_id": "AN-S-5", "version": 1}},
                current_rows=capture_native(self.selection).atoms,
                structure_snapshot=self.snapshot,
            )
        self.assertEqual(original, active.read_bytes())
        self.assertEqual([], list(draft.parent.glob("AN-S-5@*-draft-*.md")))

    def test_revision_uses_selection_snapshot_path_and_validates_its_parent(
        self,
    ):
        import json
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.sources.native_draft_source__shared import (
            _revision_root,
        )

        self.existing_contract("ready")
        rows = capture_native(self.selection).atoms
        row = next(
            row
            for row in rows
            if row["id"] == "AN-S-5" and row["status_group"] == "Current"
        )
        snapshot_path = self.root / "structure.json"
        self.selection = replace(
            self.selection, structure_snapshot=snapshot_path
        )
        data = self._revision_snapshot()
        snapshot_path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(
            self.control / "UNIT_C9", _revision_root(self.selection, row)
        )
        data["components"]["C9"]["source_path"] = "OTHER_C8/component.md"
        snapshot_path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(
            InputError, "SPEC carrier must be in its lens and component root"
        ):
            _revision_root(self.selection, row)
        snapshot_path.write_text("{invalid", encoding="utf-8")
        with self.assertRaises(InputError):
            _revision_root(self.selection, row)
        self.assertEqual(
            self.control / "UNIT_C9",
            _revision_root(self.selection, row, self.snapshot),
        )

    def test_archive_spec_draft_preserves_body_and_allocates_unused_version(
        self,
    ):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_spec_archive import (
            archive_spec_draft,
        )

        draft = self.existing_contract("draft")
        _, header, body = draft.read_text().split("---", 2)
        metadata = yaml.safe_load(header)
        metadata["state"]["status"] = "archived"
        metadata["tier"] = 1
        occupied = (
            draft.parent.parent
            / "09_archived"
            / draft.name.replace("@1-draft-", "@1-")
        )
        occupied.parent.mkdir()
        occupied.write_text("---\n" + yaml.safe_dump(metadata) + "---" + body)
        target = {"ref_id": "AN-S-5@1-draft", "version": 1}
        outcome = archive_spec_draft(
            self.selection,
            {"target": target},
            current_rows=capture_native(self.selection).atoms,
            structure_snapshot=self.snapshot,
        )
        self.assertEqual("AN-S-5@2", outcome["artifact"]["ref_id"])
        self.assertEqual("AN-S-5@1-draft", outcome["sourceRef"])
        archived = self.root / outcome["artifact"]["path"]
        self.assertEqual(body, archived.read_text().split("---", 2)[2])
        self.assertEqual(
            "archived",
            yaml.safe_load(archived.read_text().split("---", 2)[1])["state"][
                "status"
            ],
        )
        self.assertTrue(occupied.exists())
        self.assertEqual(
            1, yaml.safe_load(occupied.read_text().split("---", 2)[1])["tier"]
        )
        self.assertFalse(draft.exists())

    def test_archive_draft_retries_real_collisions_and_preserves_source(self):
        from unittest.mock import Mock, patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_spec_archive import (
            archive_spec_draft,
        )

        draft = self.existing_contract("draft")
        (draft.parent.parent / "09_archived").mkdir(exist_ok=True)
        capture = capture_native(self.selection)
        indexed = Mock(atoms=capture.atoms, errors=[], max_archived_version=7)
        attempts = []

        with (
            patch(
                (
                    'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_update_spec__shared.revalidate_native'
                ),
                return_value=indexed,
            ),
            patch(
                "os.link",
                side_effect=fixtures.collide_first_two_links(attempts),
            ),
        ):
            result = archive_spec_draft(
                self.selection,
                {"target": {"ref_id": "AN-S-5@1-draft", "version": 1}},
                current_rows=capture.atoms,
                structure_snapshot=self.snapshot,
            )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual("AN-S-5@10", result["artifact"]["ref_id"])
        self.assertEqual(3, len(attempts))
        directory = (self.root / result["artifact"]["path"]).parent
        self.assertEqual(
            [b"occupied", b"occupied"],
            [(directory / name).read_bytes() for name in attempts[:2]],
        )
        self.assertFalse(draft.exists())

    def test_archive_draft_does_not_retry_other_write_errors(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_spec_archive import (
            archive_spec_draft,
        )

        draft = self.existing_contract("draft")
        with patch("os.link", side_effect=PermissionError("failed")) as write:
            result = archive_spec_draft(
                self.selection,
                {"target": {"ref_id": "AN-S-5@1-draft", "version": 1}},
                current_rows=capture_native(self.selection).atoms,
                structure_snapshot=self.snapshot,
            )
        self.assertEqual("failed", result["outcome"])
        self.assertEqual(1, write.call_count)
        self.assertTrue(draft.exists())

    def test_activation_is_refused_and_archival_remains_available(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_update_spec__shared import (
            change_spec_status,
        )

        ready = self.existing_contract("ready")
        original = ready.read_bytes()
        target = {"ref_id": "AN-S-5", "version": 1}
        with self.assertRaisesRegex(
            InputError, "Add the Component Contract to the Component Manifest"
        ):
            change_spec_status(
                self.selection,
                {"target": target, "targetStatus": "active"},
                current_rows=capture_native(self.selection).atoms,
                structure_snapshot=self.snapshot,
            )
        self.assertEqual(original, ready.read_bytes())
        ready.unlink()
        active = self.existing_contract("active")
        archived = change_spec_status(
            self.selection,
            {"target": target, "targetStatus": "archived"},
            current_rows=capture_native(self.selection).atoms,
            structure_snapshot=self.snapshot,
        )
        self.assertEqual(
            "09_archived",
            (self.root / archived["artifact"]["path"]).parent.name,
        )
        self.assertFalse(active.exists())

    def test_reader_validates_active_contract(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.components.component_contract__pub import (
            read_component_contract,
        )
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_read__pub import (
            parse_carrier,
        )

        path = self.existing_contract("active")
        carrier = parse_carrier(path.read_bytes(), path)
        fields = read_component_contract(path, carrier, "C9", "AN")
        self.assertEqual(
            ("AN-S-5@1", "AN-S-5", "C9", "The graph includes imports."),
            (
                fields["ref_id"],
                fields["atom_id"],
                fields["component_id"],
                fields["guarantee"],
            ),
        )
        with self.assertRaises(ValueError):
            read_component_contract(path, carrier, "C8", "AN")
        carrier.metadata["tier"] = 1
        with self.assertRaises(ValueError):
            read_component_contract(path, carrier, "C9", "AN")

    def test_reader_ignores_inactive_and_non_contract(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.components.component_contract__pub import (
            read_component_contract,
        )

        carrier = NonCallableMock(
            spec_set=["metadata", "body"],
            metadata={
                "context": {"template": "component_contract"},
                "state": {"status": "draft"},
            },
            body="",
        )
        self.assertIsNone(
            read_component_contract(Path("x"), carrier, "C9", "AN")
        )
        carrier.metadata = {"context": {}, "state": {"status": "active"}}
        self.assertIsNone(
            read_component_contract(Path("x"), carrier, "C9", "AN")
        )
