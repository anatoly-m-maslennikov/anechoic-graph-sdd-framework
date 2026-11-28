import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_header__pub import (
    canonical_native_header,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native._native_draft_revision_fixture import (
    DRAFT_4856,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.revisions._native_revision_cases_b import (
    NativeRevisionCasesB,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.revisions._native_revision_cases_c import (
    NativeRevisionCasesC,
)


class FirstSpecRevisionCases(NativeRevisionCasesB, NativeRevisionCasesC):
    def test_first_unpinned_spec_publishes_its_version_and_cleans_up(self):
        for atom_id, lens, version in [
            ("AN-S-8", "SWD", 1),
            ("AN-S-9", "SPEC", 3),
        ]:
            self._check_unpinned_revision(atom_id, lens, version)

    def _check_unpinned_revision(self, atom_id, lens, version):
        draft, ref, suffix = self._write_unpinned_draft(atom_id, lens, version)
        params = {
            "target": {"ref_id": ref, "version": version},
            "targetStatus": "ready",
        }
        result = promote_draft(
            self.selection,
            params,
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"], result)
        current = self.control / "UNIT_C9" / "02_ready" / f"{atom_id}-{suffix}"
        self.assertEqual(
            (current, version),
            (
                self.root / result["artifact"]["path"],
                result["artifact"]["version"],
            ),
        )
        self.assertFalse(draft.exists())
        self.assertEqual(
            ["create", "remove"],
            [
                e["operation"]
                for e in result["effects"]
                if e.get("evidence") != "directory"
            ],
        )
        self.assertFalse(capture_native(self.selection).errors)

    def _write_unpinned_draft(self, atom_id, lens, version):
        suffix = lens + "--example.md"
        ref = f"{atom_id}@{version}-draft"
        draft = self.spec(f"UNIT_C9/01_draft/{ref}-{suffix}", atom_id, lens)
        header, body = draft.read_text().split("---\n", 2)[1:]
        data = yaml.safe_load(header)
        data["state"].update(status="draft", version=version)
        data["context"]["tier"] = 3
        draft.write_text(
            "---\n"
            + yaml.safe_dump(canonical_native_header(data), sort_keys=False)
            + "---\n"
            + body
        )
        return draft, ref, suffix

    def test_first_typed_spec_accepts_valid_and_rejects_invalid_scope(self):
        source = DRAFT_4856
        name = "AN-S-4856@1-draft-SPEC-MANIFEST_PROPERTY--declare-artifact-kind-classification.md"
        path = self.control / "UNIT_C9/01_draft" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        params = {
            "target": {"ref_id": "AN-S-4856@1-draft", "version": 1},
            "targetStatus": "ready",
        }
        invalid = source.replace(
            "MODEL//ANECHOIC <+ Graph/Classification >| Artifact Kind",
            "invalid scope",
        )
        path.write_text(invalid)
        with self.assertRaises(InputError):
            promote_draft(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertEqual(invalid, path.read_text())
        self.assertFalse((path.parent.parent / "02_ready").exists())
        path.write_text(source)
        result = promote_draft(
            self.selection,
            params,
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"], result)
        ready = self.root / result["artifact"]["path"]
        self.assertEqual(
            "AN-S-4856-SPEC-MANIFEST_PROPERTY--declare-artifact-kind-classification.md",
            ready.name,
        )
        self.assertEqual(
            "ready",
            yaml.safe_load(ready.read_text().split("---", 2)[1])["state"][
                "status"
            ],
        )
        self.assertFalse(path.exists())

    def test_first_spec_cleanup_failure_can_retry_without_rewriting(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
            effects_module as effects,
        )

        draft = self.spec(
            "UNIT_C9/01_draft/AN-S-8@1-draft-DES--example.md", "AN-S-8"
        )
        draft.write_text(
            draft.read_text().replace("status: active", "status: draft")
        )
        params = {
            "target": {"ref_id": "AN-S-8@1-draft", "version": 1},
            "targetStatus": "ready",
        }
        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion__shared.effects.remove",
            return_value=effects.Result(errors=[{"code": "injected"}]),
        ):
            result = promote_draft(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertEqual("failed", result["outcome"])
        self.assertNotIn("artifact", result)
        self.assertTrue(draft.exists())
        result = promote_draft(
            self.selection,
            params,
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"])
        self.assertEqual(
            ["remove"], [e["operation"] for e in result["effects"]]
        )
        self.assertFalse(draft.exists())

    def test_first_spec_preserves_other_drafts(self):
        old = self.spec(
            "UNIT_C9/01_draft/AN-S-8@1-draft-DES--example.md", "AN-S-8"
        )
        old.write_text(
            old.read_text().replace("status: active", "status: draft")
        )
        draft = self.spec(
            "UNIT_C9/01_draft/AN-S-8@2-draft-DES--example.md", "AN-S-8"
        )
        draft.write_text(
            draft.read_text()
            .replace("status: active", "status: draft")
            .replace("version: 1", "version: 2")
        )
        original = old.read_bytes()
        result = promote_draft(
            self.selection,
            {
                "target": {"ref_id": "AN-S-8@2-draft", "version": 2},
                "targetStatus": "ready",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"])
        self.assertEqual(2, result["artifact"]["version"])
        self.assertEqual(original, old.read_bytes())
        self.assertFalse(draft.exists())
