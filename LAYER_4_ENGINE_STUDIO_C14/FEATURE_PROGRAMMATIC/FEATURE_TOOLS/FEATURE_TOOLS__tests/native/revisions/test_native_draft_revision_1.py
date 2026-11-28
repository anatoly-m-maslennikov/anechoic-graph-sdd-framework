from dataclasses import replace
from hashlib import sha256
from pathlib import Path
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
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.spec.native_update_spec__shared import (
    change_spec_status,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_header__pub import (
    canonical_native_header,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    resolve_native_project,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    validate_manifest,
)


import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.drafts.test_native_lifecycle_draft as fixtures
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__tests.native.revisions.details.native_draft_revision_cases import (
    FirstSpecRevisionCases,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__tests.native.revisions.details import (  # noqa: E402
    _native_revision_extra_cases as cases,
)


class NativeRevisionCarrierTests(
    cases.NativeRevisionExtraCases,
    FirstSpecRevisionCases,
    fixtures.NativeRevisionCarrierTests,
    unittest.TestCase,
):
    def test_project_goal_revision_returns_active_to_repository_root(self):
        manifest = self.selection.manifest_path.rename(
            self.root / self.selection.manifest_path.name
        )
        manifest.write_text(
            manifest.read_text().replace("component: C0", "component: C00")
        )
        self.selection = replace(
            self.selection,
            manifest_path=manifest,
            manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
        )
        goal = self.root / "AN-S-1233-SPEC-PROJECT_GOAL--goal.md"
        goal.write_text(
            "---\natom_family: SPEC\natom_id: AN-S-1233\ncontainer: {component: C00}\ntier: -1\n"
            "context: {template: project_goal, lens: SPEC}\n"
            "state: {status: active, version: 1, updated_at: '2026-11-19T00:00:00Z'}\n"
            "---\n## Summary\n\nGoal\n\nOriginal.\n",
        )
        draft = create_draft(
            self.selection,
            {
                "sourceCurrent": {"ref_id": "AN-S-1233", "version": 1},
                "changes": {"body": "\n## Summary\n\nGoal\n\nRevised.\n"},
            },
            current_rows=capture_native(self.selection).atoms,
        )["savedDraft"]
        self.assertEqual(
            self.control / "01_draft", (self.root / draft["path"]).parent
        )
        ready = promote_draft(
            self.selection,
            {
                "target": {"ref_id": draft["ref_id"], "version": 2},
                "targetStatus": "ready",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", ready["outcome"], ready)
        self.assertEqual(
            self.control / "02_ready",
            (self.root / ready["artifact"]["path"]).parent,
        )
        self._assert_goal_active(goal)

    def _assert_goal_active(self, goal):
        active = change_spec_status(
            self.selection,
            {
                "target": {"ref_id": "AN-S-1233", "version": 2},
                "targetStatus": "active",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", active["outcome"], active)
        self.assertEqual(goal.name, active["artifact"]["path"])
        self.assertIn("Revised.", goal.read_text())

    def test_revision_archives_existing_epic_spec_and_pmeta(self):
        cases = [
            (
                "001_TICKETS/TASKS/AN-T-4-EPIC--example.md",
                "AN-T-4",
                "epic",
                "001_TICKETS/TASKS",
            ),
            (
                "UNIT_C9/__DES/__DOM/AN-S-4-DOM--example.md",
                "AN-S-4",
                "spec",
                "UNIT_C9",
            ),
            ("_PMETA/AN-P-4-ACTION--example.md", "AN-P-4", "action", "_PMETA"),
            (
                "UNIT_C9/AN-S-5-SPEC--example.md",
                "AN-S-5",
                "root_spec",
                "UNIT_C9",
            ),
        ]
        for name, atom_id, kind, owner in cases:
            with self.subTest(kind=kind):
                self._check_archived_revision(name, atom_id, kind, owner)

    def _check_archived_revision(self, name, atom_id, kind, owner):
        if kind in {"spec", "root_spec"}:
            path = self.spec(
                name, atom_id, "DES/DOM" if kind == "spec" else "SPEC"
            )
        else:
            path = self.write(name, atom_id, template=kind)
        old = path.read_bytes().split(b"---\n", 2)[2]
        rows = capture_native(self.selection).atoms
        output = create_draft(
            self.selection,
            {
                "sourceCurrent": {"ref_id": atom_id, "version": 1},
                "changes": {"body": old.decode().replace("Old", "New")},
            },
            current_rows=rows,
        )
        self._assert_archived_revision(atom_id, owner, output, old)

    def _assert_archived_revision(self, atom_id, owner, output, old):
        draft = self.root / output["savedDraft"]["path"]
        self.assertEqual(self.control / owner / "01_draft", draft.parent)
        ref = output["savedDraft"]["ref_id"]
        result = promote_draft(
            self.selection,
            {
                "target": {"ref_id": ref, "version": 2},
                "targetStatus": "ready"
                if atom_id.startswith("AN-S-")
                else "active",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"])
        rows = capture_native(self.selection)
        self.assertFalse(rows.errors)
        archived = next(
            row for row in rows.atoms if row["_exact_ref"] == atom_id + "@1"
        )
        self.assertEqual(old, archived["_content_bytes"])
        self.assertIn(
            b"New",
            (self.root / result["artifact"]["path"]).read_bytes(),
        )
        self.assertFalse(draft.exists())

    def test_canonical_tier_one_and_two_active_revisions(self):
        layouts = (
            (1, "01_TIER_1_ARCHITECTURE"),
            (2, "_DES"),
            (1, "01_CUSTOM_ARCHITECTURE"),
        )
        for number, (tier, folder) in enumerate(layouts, 31):
            with self.subTest(tier=tier, folder=folder):
                self._check_tier_revision(tier, folder, number)

    def _check_tier_revision(self, tier, folder, number):
        self._set_custom_tier_layout(folder)
        atom_id = f"AN-S-{number}"
        source = self.spec(
            f"UNIT_C9/{folder}/{atom_id}-DES--example.md", atom_id
        )
        header, body = source.read_text().split("---\n", 2)[1:]
        metadata = yaml.safe_load(header)
        metadata["context"]["tier"] = tier
        metadata = canonical_native_header(metadata)
        source.write_text("---\n" + yaml.safe_dump(metadata) + "---\n" + body)

        def rows():
            return capture_native(self.selection).atoms

        draft = create_draft(
            self.selection,
            {
                "sourceCurrent": {"ref_id": atom_id, "version": 1},
                "changes": {"body": body.replace("Old", "New")},
            },
            current_rows=rows(),
        )["savedDraft"]
        ready = promote_draft(
            self.selection,
            {
                "target": {"ref_id": draft["ref_id"], "version": 2},
                "targetStatus": "ready",
            },
            current_rows=rows(),
        )
        self.assertEqual("completed", ready["outcome"], ready)
        self.assertTrue(
            (
                self.control
                / f"UNIT_C9/09_archived/{atom_id}@1-DES--example.md"
            ).exists()
        )
        self._assert_tier_active(source, atom_id, rows)

    def _assert_tier_active(self, source, atom_id, rows):
        active = change_spec_status(
            self.selection,
            {
                "target": {"ref_id": atom_id, "version": 2},
                "targetStatus": "active",
            },
            current_rows=rows(),
        )
        self.assertEqual("completed", active["outcome"], active)
        self.assertEqual(source, self.root / active["artifact"]["path"])
        self.assertIn("New", source.read_text())

    def _set_custom_tier_layout(self, folder):
        if folder == "01_CUSTOM_ARCHITECTURE":
            manifest = self.selection.manifest_path
            layout = {
                "0": ".",
                "1": folder,
                "2+": "_{lens}/{sublenses}",
            }
            parameters = {
                "project": {"folder_layout": {"active_spec_by_tier": layout}}
            }
            manifest.write_text(
                manifest.read_text().replace(
                    "lens_whitelist=['DES', 'SPEC']",
                    f"lens_whitelist=['DES', 'SPEC'], parameters={parameters!r}",
                )
            )
            self.selection = resolve_native_project(
                self.root,
                self.control.name,
                validate_manifest=validate_manifest,
            )

    def test_legacy_pmeta_revision_serializes_project_config(self):
        path = self.write(
            "002_PROJECT_CONFIG/AN-P-4-ACTION--example.md",
            "AN-P-4",
            template="action",
        )
        _, text, body = path.read_text().split("---", 2)
        header = canonical_native_header(yaml.safe_load(text))
        header["atom_family"] = "PMETA"
        header["relations"] = {"REFERENCES": ["AN-S-1@1"]}
        path.write_text(
            "---\n" + yaml.safe_dump(header, sort_keys=False) + "---" + body
        )
        original = path.read_bytes()

        def rows():
            return capture_native(self.selection).atoms

        output = create_draft(
            self.selection,
            {"sourceCurrent": {"ref_id": "AN-P-4", "version": 1}},
            current_rows=rows(),
        )
        draft = self.root / output["savedDraft"]["path"]
        _, draft_text, draft_body = draft.read_text().split("---", 2)
        self.assertEqual(
            "PROJECT_CONFIG", yaml.safe_load(draft_text)["atom_family"]
        )
        self.assertEqual(body, draft_body)
        self.assertEqual(original, path.read_bytes())
        result = promote_draft(
            self.selection,
            {
                "target": {"ref_id": "AN-P-4@2-draft", "version": 2},
                "targetStatus": "active",
            },
            current_rows=rows(),
        )
        self._assert_pmeta_serialization(result, header, body)

    def _assert_pmeta_serialization(self, result, header, body):
        for saved in (
            self.root / result["artifact"]["path"],
            self.control
            / "002_PROJECT_CONFIG/09_archived/AN-P-4@1-ACTION--example.md",
        ):
            _, saved_text, saved_body = saved.read_text().split("---", 2)
            saved_header = yaml.safe_load(saved_text)
            self.assertEqual("PROJECT_CONFIG", saved_header["atom_family"])
            self.assertEqual(header["relations"], saved_header["relations"])
            self.assertEqual(body, saved_body)
