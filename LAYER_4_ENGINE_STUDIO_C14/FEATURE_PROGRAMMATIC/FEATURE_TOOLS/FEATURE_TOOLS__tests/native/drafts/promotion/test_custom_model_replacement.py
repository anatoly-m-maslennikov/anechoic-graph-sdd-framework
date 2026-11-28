from pathlib import Path
import sys

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
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.drafts import (
    test_native_lifecycle_draft as fixtures,
)


class CustomModelReplacementTests(fixtures.NativeDraftTests):
    def setUp(self):
        super().setUp()
        root = self.control / "__PROJECT_CONFIG/CUSTOM_MODEL"
        (root / "01_draft").mkdir(parents=True)

        def carrier(
            atom_id,
            template,
            status,
            version,
            summary,
            relation="",
            manifest="",
        ):
            return (
                f"---\natom_family: PROJECT_CONFIG\natom_id: {atom_id}\n"
                "structure:\n  container:\n    component: C00\ncontext:\n  "
                f"template: {template}\n"
                f"{relation}state:\n  status: {status}\n  version: {version}\n"
                "  updated_at: '2026-01-01T00:00:00+00:00'\n---\n\n"
                f"## Summary\n\n{summary}\n\n## Formal Manifest\n\n{manifest}\n"
            )

        self.old = root / "AN-C-1-MODEL_MANIFEST--declare-axiom.md"
        self.old.write_text(
            carrier("AN-C-1", "model_manifest", "active", 2, "Declare Axiom")
        )
        self.new = (
            root / "01_draft/AN-C-2@1-draft-MANIFEST_NODE--declare-axiom-spec-"
            "template.md"
        )
        self.new.write_text(
            carrier(
                "AN-C-2",
                "manifest_node",
                "draft",
                1,
                "Declare Axiom Spec Template",
                "relations:\n  IS_REPLACEMENT_FOR:\n  - AN-C-1\n",
                "```python anechoic-edsl\nfrom anechoic.model import "
                "SpecAtom\nclass Axiom(SpecAtom):\n    pass\n```",
            )
        )
        self.target = {
            "target": {"ref_id": "AN-C-2@1-draft", "version": 1},
            "targetStatus": "active",
        }

    def test_replacement_archives_predecessor_and_publishes_new_identity(self):
        result = promote_draft(
            self.selection,
            self.target,
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"])
        self.assertFalse(self.old.exists())
        self.assertFalse(self.new.exists())
        archive = (
            self.old.parent
            / "09_archived/AN-C-1@2-MODEL_MANIFEST--declare-axiom.md"
        )
        self.assertIn(
            "updated_at: '2026-01-01T00:00:00+00:00'", archive.read_text()
        )
        self.assertTrue(
            (
                self.old.parent
                / "AN-C-2-MANIFEST_NODE--declare-axiom-spec-template.md"
            ).exists()
        )

    def test_missing_predecessor_refuses_without_effects(self):
        self.old.unlink()
        with self.assertRaises(SourceChanged):
            promote_draft(
                self.selection,
                self.target,
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertTrue(self.new.exists())

    def test_direct_to_active_refuses_an_active_successor_before_archival(
        self,
    ):
        peer = self.old.with_name("AN-C-3-MODEL_MANIFEST--declare-other.md")
        peer.write_text(
            self.old.read_text()
            .replace("AN-C-1", "AN-C-3")
            .replace("Declare Axiom", "Declare Other")
            .replace(
                "state:",
                "relations:\n  IS_REPLACEMENT_FOR:\n  - AN-C-2\nstate:",
            )
        )
        with self.assertRaisesRegex(InputError, "cannot both be Active"):
            promote_draft(
                self.selection,
                self.target,
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertTrue(self.old.exists())
        self.assertTrue(self.new.exists())
        self.assertFalse((self.old.parent / "09_archived").exists())

    def test_invalid_manifest_and_stale_predecessor_have_no_effects(self):
        for invalid in (True, False):
            original = self.new.read_text()
            if invalid:
                self.new.write_text(
                    original.replace(
                        "class Axiom(SpecAtom):",
                        "class Axiom(SpecAtom):\n    bad()",
                    )
                )
            rows = capture_native(self.selection).atoms
            if not invalid:
                self.old.write_text(self.old.read_text() + "\nchanged\n")
            with self.assertRaises((InputError, SourceChanged)):
                promote_draft(self.selection, self.target, current_rows=rows)
            self.assertTrue(self.old.exists())
            self.assertTrue(self.new.exists())
            self.assertFalse((self.old.parent / "09_archived").exists())
            self.new.write_text(original)
