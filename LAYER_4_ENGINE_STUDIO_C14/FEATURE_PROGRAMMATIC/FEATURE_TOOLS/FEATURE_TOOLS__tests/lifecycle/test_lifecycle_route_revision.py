"""Generated native lifecycle paths; each case uses a fresh project."""

from pathlib import Path
import sys
import unittest


sys.path.insert(
    0,
    str(
        (ENGINE := (TOOLS := Path(__file__).resolve().parents[2]).parents[1])
        / "IWE_CONSOLE_C43"
    ),
)
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.\
    ATOM_LIFECYCLE__shared import (
    InputError,
    SourceChanged,
)  # fmt: skip
import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.drafts.\
    test_native_lifecycle_draft as fixtures  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)


class NonTicketRevisionMatrix(unittest.TestCase):
    write = fixtures.NativeDraftTests.write
    spec = fixtures.NativeRevisionCarrierTests.spec

    def test_generic_spec_and_project_config_revision(self):
        for family in ("SPEC", "PROJECT_CONFIG"):
            with self.subTest(family=family):
                self._check_revision(family)

    def _check_revision(self, family):
        fixtures.NativeRevisionCarrierTests.setUp(self)
        if family == "SPEC":
            path = self.spec(
                "UNIT_C9/__DES/__DOM/AN-S-4-DOM--example.md",
                "AN-S-4",
                "DES/DOM",
            )
            atom_id, status = "AN-S-4", "ready"
        else:
            path = self.write(
                "002_PROJECT_CONFIG/AN-P-4-ACTION--example.md",
                "AN-P-4",
                template="action",
            )
            atom_id, status = "AN-P-4", "active"

        def rows():
            return capture_native(self.selection).atoms

        original = path.read_bytes()
        revision = create_draft(
            self.selection,
            {"sourceCurrent": {"ref_id": atom_id, "version": 1}},
            current_rows=rows(),
        )
        self.assertEqual("completed", revision["outcome"])
        draft = revision["savedDraft"]
        self.assertEqual(original, path.read_bytes())
        result = promote_draft(
            self.selection,
            {
                "target": {"ref_id": draft["ref_id"], "version": 2},
                "targetStatus": status,
            },
            current_rows=rows(),
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(status, result["artifact"]["status"])
        self.assertIn(atom_id + "@1", [row["_exact_ref"] for row in rows()])
        self._assert_stale_unchanged(atom_id, rows)

    def _assert_stale_unchanged(self, atom_id, rows):
        before = {p: p.read_bytes() for p in self.control.rglob("*.md")}
        with self.assertRaises((InputError, SourceChanged)):
            create_draft(
                self.selection,
                {
                    "sourceCurrent": {
                        "ref_id": atom_id + "@1",
                        "version": 1,
                    }
                },
                current_rows=rows(),
            )
        self.assertEqual(
            before,
            {p: p.read_bytes() for p in self.control.rglob("*.md")},
        )
