import json
import os
from pathlib import Path
import subprocess
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

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_placement__pub import (
    TICKET_DIRECTORY,
)
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


import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.drafts.test_native_lifecycle_draft as fixtures


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.tickets import (  # noqa: E402
    _native_task_middle_cases as middle,
    _native_task_extra_cases as extra,
)


class NewNativeTaskTests(
    middle.NativeTaskMiddleCases,
    extra.NativeTaskExtraCases,
    fixtures.NewNativeTaskTests,
    unittest.TestCase,
):
    def test_indexed_cli_creates_without_capture_or_model(self):
        request = {
            "binding": {
                "root": str(self.root),
                "control_root": self.control.name,
                "manifest_path": self.selection.manifest_path.relative_to(
                    self.root
                ).as_posix(),
                "manifest_sha256": self.selection.manifest_sha256,
                "project_prefix": "AN",
            },
            "name": "atom_lifecycle_create_draft",
            "arguments": self.new,
            "indexed_task": {
                "max_number": "2",
                "manifest_ref": "AN-S-1@1",
                "component_ids": ["C00"],
                "ticket_labels": ["Task"],
            },
        }
        self.selection.manifest_path.unlink()
        process = subprocess.run(
            [
                sys.executable,
                "-B",
                "-P",
                "-m",
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle_cli",
            ],
            cwd=ENGINE,
            env={**os.environ, "PYTHONPATH": str(ENGINE)},
            input=json.dumps(request),
            text=True,
            capture_output=True,
            timeout=15,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual("AN-T-3@1-draft", result["savedDraft"]["ref_id"])
        self.assertTrue((self.root / result["savedDraft"]["path"]).is_file())

    def test_new_task_allocates_across_history_and_promotes_version_one(self):
        self.write(
            "001_TICKETS/ISSUES/09_archived/AN-T-8@2-QUESTION--old.md",
            "AN-T-8",
            version=2,
            status="archived",
            template="question",
        )
        before = (
            self.path.read_bytes(),
            self.selection.manifest_path.read_bytes(),
        )
        result = create_draft(self.selection, self.new, current_rows=self.rows)
        self.assertEqual("AN-T-9@1-draft", result["savedDraft"]["ref_id"])
        draft = self.root / result["savedDraft"]["path"]
        header = yaml.safe_load(draft.read_text().split("---", 2)[1])
        self.assertEqual(
            ("TKT", "AN-T-9", 2),
            (header["atom_family"], header["atom_id"], header["priority"]),
        )
        self.assertEqual(
            {"template": "task", "label": "Task"}, header["context"]
        )
        self.assertEqual("AN-T-9@1-draft-TASK--create-a-task.md", draft.name)
        rows = capture_native(self.selection).atoms
        result = promote_draft(
            self.selection,
            {
                "target": {"ref_id": "AN-T-9@1-draft", "version": 1},
                "targetStatus": "backlog",
            },
            current_rows=rows,
        )
        self.assertEqual(
            ("AN-T-9", 1, "backlog"),
            (
                result["artifact"]["ref_id"],
                result["artifact"]["version"],
                result["artifact"]["status"],
            ),
        )
        self.assertFalse(draft.exists())
        self._assert_new_task_transitions(before)

    def _assert_new_task_transitions(self, before):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
            change_ticket_status,
        )

        target = {"ref_id": "AN-T-9", "version": 1}
        queued = change_ticket_status(
            self.selection,
            {"target": target, "targetStatus": "in_queue"},
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual(
            self.control / TICKET_DIRECTORY / "TASKS",
            (self.root / queued["artifact"]["path"]).parent,
        )
        with self.assertRaises(InputError):
            change_ticket_status(
                self.selection,
                {"target": target, "targetStatus": "in_progress"},
                current_rows=capture_native(self.selection).atoms,
                check_definition=lambda: None,
            )
        done = change_ticket_status(
            self.selection,
            {"target": target, "targetStatus": "done"},
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual("done", done["artifact"]["status"])
        capture = capture_native(self.selection)
        self.assertFalse(capture.errors)
        self.assertIn("AN-T-9@1", [row["_exact_ref"] for row in capture.atoms])
        self.assertEqual(
            before,
            (
                self.path.read_bytes(),
                self.selection.manifest_path.read_bytes(),
            ),
        )

    def test_new_draft_publishes_nested_drafts_and_preserves_assets(self):
        ref, draft, child_id, grand_result = self._create_nested_drafts()
        outcome = promote_draft(
            self.selection,
            {
                "target": {"ref_id": ref, "version": 1},
                "targetStatus": "backlog",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self._assert_nested_publication(outcome, draft, child_id, grand_result)

    def _create_nested_drafts(self):
        created = create_draft(
            self.selection, self.new, current_rows=self.rows
        )
        ref = created["savedDraft"]["ref_id"]
        draft = self.root / created["savedDraft"]["path"]
        labels = ("Task", "Epic", "Version")
        child_result = create_draft(
            self.selection,
            {
                "newAtom": {
                    "template": "task",
                    "label": "Epic",
                    "container": {"atom": ref.split("@")[0]},
                    "body": "\n## Summary\n\nChild\n",
                }
            },
            current_rows=capture_native(self.selection).atoms,
            ticket_labels=labels,
        )
        child = self.root / child_result["savedDraft"]["path"]
        self.assertEqual(draft.with_suffix("") / "01_draft", child.parent)
        child_id = child_result["savedDraft"]["atom_id"]
        grand_result = create_draft(
            self.selection,
            {
                "newAtom": {
                    "template": "task",
                    "label": "Version",
                    "container": {"atom": child_id},
                    "body": "\n## Summary\n\nGrand\n",
                }
            },
            current_rows=capture_native(self.selection).atoms,
            ticket_labels=labels,
        )
        grand = self.root / grand_result["savedDraft"]["path"]
        asset = grand.parent.parent / "notes.txt"
        asset.write_text("keep")
        return ref, draft, child_id, grand_result

    def _assert_nested_publication(
        self, outcome, draft, child_id, grand_result
    ):
        self.assertEqual("completed", outcome["outcome"], outcome)
        parent = self.root / outcome["artifact"]["path"]
        child_current = (
            parent.with_suffix("") / f"backlog/{child_id}-EPIC--child.md"
        )
        grand_id = grand_result["savedDraft"]["atom_id"]
        grand_current = (
            child_current.with_suffix("")
            / f"backlog/{grand_id}-VERSION--grand.md"
        )
        header = yaml.safe_load(grand_current.read_text().split("---", 2)[1])
        self.assertEqual("backlog", header["state"]["status"])
        self.assertEqual(
            {"template": "task", "label": "Version"}, header["context"]
        )
        self.assertEqual(
            "keep", (child_current.with_suffix("") / "notes.txt").read_text()
        )
        self.assertFalse(draft.exists())
