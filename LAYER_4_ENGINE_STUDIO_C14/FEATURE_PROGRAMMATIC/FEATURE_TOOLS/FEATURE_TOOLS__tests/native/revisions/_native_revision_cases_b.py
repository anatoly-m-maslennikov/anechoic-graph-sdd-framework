"""First specification revision scenarios."""

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_header__pub import (
    canonical_native_header,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
    SourceChanged,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)


class NativeRevisionCasesB:
    def test_first_spec_rejects_unsafe_or_stale_inputs(self):
        for case in (
            "owner",
            "lens",
            "template",
            "manifest_name",
            "filename",
            "history",
            "stale",
            "status",
        ):
            with self.subTest(case=case):
                self._assert_unsafe_revision(case)

    def _assert_unsafe_revision(self, case):
        draft, history = self._unsafe_revision_fixture(case)
        rows = capture_native(self.selection).atoms
        if case == "stale":
            draft.write_bytes(draft.read_bytes() + b"changed")
        before = {
            p.relative_to(self.control): p.read_bytes()
            for p in self.control.rglob("*.md")
        }
        params = {
            "target": {"ref_id": "AN-S-8@1-draft", "version": 1},
            "targetStatus": "done" if case == "status" else "ready",
        }
        with self.assertRaises((InputError, SourceChanged)):
            promote_draft(self.selection, params, current_rows=rows)
        self.assertEqual(
            before,
            {
                p.relative_to(self.control): p.read_bytes()
                for p in self.control.rglob("*.md")
            },
        )
        draft.unlink()
        if history:
            history.unlink()

    def _unsafe_revision_fixture(self, case):
        name = (
            "SPEC-PROJECT_MANIFEST--example.md"
            if case == "manifest_name"
            else "SWD--example.md"
            if case == "filename"
            else "DES--example.md"
        )
        draft = self.spec(
            f"UNIT_C9/01_draft/AN-S-8@1-draft-{name}",
            "AN-S-8",
            "invalid/lens!" if case == "lens" else "DES",
            "C8" if case == "owner" else "C9",
        )
        header, body = draft.read_text().split("---\n", 2)[1:]
        data = yaml.safe_load(header)
        data["state"]["status"] = "draft"
        if case == "filename":
            data["context"]["tier"] = 3
        if case == "template":
            data["context"]["template"] = "component_manifest"
        draft.write_text(
            "---\n"
            + yaml.safe_dump(
                canonical_native_header(data) if case == "filename" else data
            )
            + "---\n"
            + body
        )
        history = None
        if case == "history":
            history = self.spec(
                "UNIT_C9/09_archived/AN-S-8@2-DES--example.md",
                "AN-S-8",
            )
            history.write_text(
                history.read_text()
                .replace("status: active", "status: archived")
                .replace("version: 1", "version: 2")
            )
        return draft, history

    def test_template_recode_preserves_old_draft_and_archive_name(self):
        self._write_recode_current()

        def rows():
            return capture_native(self.selection).atoms

        params = {"sourceCurrent": {"ref_id": "AN-S-44", "version": 1}}
        first = create_draft(self.selection, params, current_rows=rows())[
            "savedDraft"
        ]
        old_draft = self.root / first["path"]
        old_bytes = old_draft.read_bytes()
        second = create_draft(self.selection, params, current_rows=rows())[
            "savedDraft"
        ]
        draft = self.root / second["path"]
        draft = self._write_recoded_draft(draft)
        result = promote_draft(
            self.selection,
            {
                "target": {"ref_id": "AN-S-44@3-draft", "version": 3},
                "targetStatus": "ready",
            },
            current_rows=rows(),
        )
        self._assert_recode_result(result, old_bytes, old_draft, rows)

    def _write_recode_current(self):
        current = self.spec(
            "UNIT_C9/_SPEC/AN-S-44-SPEC--example.md", "AN-S-44", "SPEC"
        )
        _, text, body = current.read_text().split("---", 2)
        metadata = yaml.safe_load(text)
        metadata["context"]["tier"] = 2
        body = body.replace("# Summary", "## Summary")
        body += (
            "\n## Claim\n\n### Formal Claim\n\n```python\nfrom anechoic."
            "formal_claims import declare_relation\n"
            'declare_relation(relation_name="LINK", source_endpoint={}, '
            "target_endpoint={})\n```\n"
        )
        current.write_text(
            "---\n"
            + yaml.safe_dump(
                canonical_native_header(metadata), sort_keys=False
            )
            + "---"
            + body
        )

    def _write_recoded_draft(self, draft):
        _, text, _ = draft.read_text().split("---", 2)
        metadata = yaml.safe_load(text)
        metadata["context"]["template"] = "manifest_relation"
        typed_body = (
            "\n## Summary\n\nExample\n\n## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Relation//LINK\n\n"
            "## Formal Manifest\n\n```python anechoic-edsl\nfrom anechoic.model import Relation\n"
            'class Link(Relation):\n    name = "LINK"\n    source_endpoint = {"level": "model_entities"}\n    target_endpoint = {"level": "model_entities"}\n```\n'
        )
        draft.rename(
            draft.with_name(
                "AN-S-44@3-draft-SPEC-MANIFEST_RELATION--example.md"
            )
        )
        draft = draft.with_name(
            "AN-S-44@3-draft-SPEC-MANIFEST_RELATION--example.md"
        )
        draft.write_text(
            "---\n"
            + yaml.safe_dump(metadata, sort_keys=False)
            + "---"
            + typed_body
        )
        return draft

    def _assert_recode_result(self, result, old_bytes, old_draft, rows):
        self.assertEqual("completed", result["outcome"], result)
        self.assertTrue(
            (
                self.control
                / "UNIT_C9/02_ready/AN-S-44-SPEC-MANIFEST_RELATION--example.md"
            ).exists()
        )
        self.assertTrue(
            (
                self.control / "UNIT_C9/09_archived/AN-S-44@1-SPEC--example.md"
            ).exists()
        )
        self.assertEqual(old_bytes, old_draft.read_bytes())
        self.assertTrue(
            any(
                row.get("_exact_ref") == "AN-S-44@3"
                and row.get("status") == "ready"
                for row in rows()
            )
        )
