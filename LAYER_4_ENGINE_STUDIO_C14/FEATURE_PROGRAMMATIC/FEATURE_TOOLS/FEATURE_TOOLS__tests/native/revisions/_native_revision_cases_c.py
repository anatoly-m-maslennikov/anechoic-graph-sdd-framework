"""First specification revision scenarios."""

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
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native._native_draft_revision_fixture import (
    DRAFT_4856,
)


class NativeRevisionCasesC:
    def test_constraints_callback_and_non_formal_predecessor(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft_guards import (
            _validate_c9_typed_manifest,
            _has_formal_declaration,
        )

        header = {
            "atom_family": "SPEC",
            "atom_id": "AN-S-3147",
            "container": {"component": "C9"},
            "tier": 2,
            "context": {"lens": "SPEC", "template": "manifest_node"},
            "state": {
                "status": "draft",
                "version": 2,
                "updated_at": "2026-11-24T00:00:00Z",
            },
        }
        body = (
            "## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Node//Atom.Constraints\n\n## Formal Manifest\n\n"
            "```python anechoic-edsl\nfrom anechoic.model import Atom, NodeConstraints\n"
            "def check_atom(atom: Atom) -> bool:\n    return True\n"
            "class Constraints(NodeConstraints):\n    bearer = Atom\n    instance_check = check_atom\n```\n"
        )
        _validate_c9_typed_manifest(header, body)
        with self.assertRaises(InputError):
            _validate_c9_typed_manifest(
                header,
                body.replace(
                    "class Constraints", "print(1)\nclass Constraints"
                ),
            )
        self.assertFalse(_has_formal_declaration("## Claim\n\nProse.\n"))

    def test_continuant_typed_manifest_requires_concern_and_no_claim_scope(
        self,
    ):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft_guards import (
            is_c9_typed_manifest,
            _validate_c9_typed_manifest,
        )

        header = {
            "atom_family": "SPEC",
            "atom_id": "AN-S-100",
            "container": {"component": "C9"},
            "tier": 2,
            "state": {
                "status": "draft",
                "version": 1,
                "updated_at": "2026-11-24T00:00:00Z",
            },
            "concern": {
                "subject": "Atom",
                "path": "Model/Graph/Node",
                "relation": "is_narrower_than",
            },
            "context": {"lens": "DOM/CONT", "template": "manifest_node"},
        }
        body = (
            "## Formal Manifest\n\n```python anechoic-edsl\n"
            "from anechoic.model import Node\nclass Atom(Node):\n    pass\n```\n"
        )
        self.assertTrue(is_c9_typed_manifest(header))
        _validate_c9_typed_manifest(header, body)
        self._assert_invalid_concerns(header, body)

    def _assert_invalid_concerns(self, header, body):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft_guards import (
            _validate_c9_typed_manifest,
        )

        for concern in (
            None,
            {},
            {"subject": "Atom"},
            {**header["concern"], "relation": "unknown"},
        ):
            with self.subTest(concern=concern), self.assertRaises(InputError):
                _validate_c9_typed_manifest(
                    {**header, "concern": concern}, body
                )
        with self.assertRaises(InputError):
            _validate_c9_typed_manifest(
                header,
                "## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Node//Atom\n\n"
                + body,
            )

    def test_continuant_revision_accepts_legacy_typed_header_migration(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.revision.native_draft_revision__shared import (
            _check_revision_headers,
        )

        previous = {
            "atom_family": "SPEC",
            "container": {"component": "C9"},
            "tier": 2,
            "context": {"lens": "SPEC", "template": "manifest_node"},
        }
        draft = {
            **previous,
            "concern": {
                "subject": "Atom",
                "path": "Model/Graph/Node",
                "relation": "is_narrower_than",
            },
            "context": {"lens": "DOM/CONT", "template": "manifest_node"},
        }
        body = "## Summary\n\nExample\n"
        _check_revision_headers(draft, previous, body, body, True)
        with self.assertRaises(InputError):
            _check_revision_headers(
                {**draft, "tier": 3}, previous, body, body, True
            )

    def test_first_continuant_manifest_promotes_to_ready(self):
        header_text, body = DRAFT_4856.split("---\n", 2)[1:]
        header = yaml.safe_load(header_text)
        header["context"]["lens"] = "DOM/CONT"
        header["concern"] = {
            "subject": "Artifact Kind",
            "path": "Model/Graph/Classification",
            "relation": "classifies",
        }
        body = body.replace(
            "## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Classification >| Artifact Kind\n\n",
            "",
        )
        path = (
            self.control
            / "UNIT_C9/01_draft/AN-S-4856@1-draft-CONT-MANIFEST_PROPERTY--declare-artifact-kind-classification.md"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "---\n" + yaml.safe_dump(header, sort_keys=False) + "---\n" + body
        )
        result = promote_draft(
            self.selection,
            {
                "target": {"ref_id": "AN-S-4856@1-draft", "version": 1},
                "targetStatus": "ready",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(
            "AN-S-4856-CONT-MANIFEST_PROPERTY--declare-artifact-kind-classification.md",
            (self.root / result["artifact"]["path"]).name,
        )

    def test_continuant_revision_promotes_legacy_typed_manifest(self):
        self._write_legacy_continuant()

        def rows():
            return capture_native(self.selection).atoms

        saved = create_draft(
            self.selection,
            {"sourceCurrent": {"ref_id": "AN-S-4856", "version": 1}},
            current_rows=rows(),
        )["savedDraft"]
        draft = self.root / saved["path"]
        _, text, body = draft.read_text().split("---\n", 2)
        header = yaml.safe_load(text)
        header["context"]["lens"] = "DOM/CONT"
        header["concern"] = {
            "subject": "Artifact Kind",
            "path": "Model/Graph/Classification",
            "relation": "classifies",
        }
        body = body.replace(
            "## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Classification >| Artifact Kind\n\n",
            "",
        )
        draft.rename(
            draft.with_name(
                "AN-S-4856@2-draft-CONT-MANIFEST_PROPERTY--declare-artifact-kind-classification.md"
            )
        )
        draft = draft.with_name(
            "AN-S-4856@2-draft-CONT-MANIFEST_PROPERTY--declare-artifact-kind-classification.md"
        )
        draft.write_text(
            "---\n" + yaml.safe_dump(header, sort_keys=False) + "---\n" + body
        )
        result = promote_draft(
            self.selection,
            {
                "target": {"ref_id": "AN-S-4856@2-draft", "version": 2},
                "targetStatus": "ready",
            },
            current_rows=rows(),
        )
        self._assert_continuant_revision(result)

    def _write_legacy_continuant(self):
        current = (
            self.control
            / "UNIT_C9/_SPEC/AN-S-4856-SPEC-MANIFEST_PROPERTY--declare-artifact-kind-classification.md"
        )
        current.parent.mkdir(parents=True, exist_ok=True)
        current.write_text(
            DRAFT_4856.replace("status: draft", "status: active")
        )

    def _assert_continuant_revision(self, result):
        self.assertEqual("completed", result["outcome"], result)
        self.assertTrue(
            (
                self.control
                / "UNIT_C9/09_archived/AN-S-4856@1-SPEC-MANIFEST_PROPERTY--declare-artifact-kind-classification.md"
            ).exists()
        )
        self.assertTrue((self.root / result["artifact"]["path"]).exists())
