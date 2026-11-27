("Formal Status placement uses numbered directories and "
 "Current source selection.")  # fmt: skip

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(TOOLS := Path(__file__).resolve().parents[1]))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.\
    FEATURE_TOOLS__tests__shared import (  # noqa: E402
    compile_candidate_schema,
    load_candidate_schema,
)  # fmt: skip

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.\
    test_lifecycle_formal_placement import (
    role_source,
    native_body,
    status_rule,
)  # fmt: skip


def statement(status, template, *, plan=False):
    base = "container" if template.startswith("<container>") else "role"
    folder = template.rsplit("/", 1)[-1] if "/" in template else ""
    return status_rule(status.lower(), base, folder, "plan" if plan else None)


class NumberedStatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        role_source(self.root, "Plan", 3, "CA-R-482")

    def delivery(self, atom_id, subject, claim, *, directory=None):
        path = (directory or self.root) / f"{atom_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\natom_id: {atom_id}\nrole: Delivery\n"
            "form: File Layout\nstatus: Active\nversion: 1\n"
            f"topics:\n  main_subject: {json.dumps(subject)}\n---\n"
            + native_body(
                claim if isinstance(claim, (tuple, list)) else (claim,)
            )
        )

    def _write_initial_status_sources(self):
        self.delivery(
            "CA-D-1001", "ANECHOIC_MODEL <+ Carrier", {"kind": "role_root"}
        )
        prefix = (
            "ANECHOIC_MODEL <+ Atom.Header.State.Status >| Status Group := "
        )
        self.delivery(
            "CA-D-1002",
            prefix + "Draft",
            statement("Draft", "<owning scope unit>/<role folder>/000_draft"),
        )
        self.delivery(
            "CA-D-1003",
            prefix + "Archived",
            statement(
                "Archived", "<owning scope unit>/<role folder>/099_archived"
            ),
        )
        return prefix

    def _write_status_sources(self):
        prefix = self._write_initial_status_sources()
        self.delivery(
            "CA-D-1004",
            prefix + "Current",
            [
                statement("Active", "<container>"),
                statement("Done", "<container>/020_done"),
                statement("Resolved", "<container>/021_resolved"),
                statement("Canceled", "<container>/040_canceled"),
            ],
        )
        self.delivery(
            "CA-D-1005",
            "ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)."
            "Header.State.Status >| Status Group := Backlog",
            statement(
                "Backlog",
                "<owning scope unit>/<role folder>/001_backlog",
                plan=True,
            ),
        )
        self.delivery(
            "CA-D-1006",
            prefix + "Draft",
            statement("Draft", "<owning scope unit>/<role folder>/wrong"),
            directory=self.root / "000_draft",
        )
        self.delivery(
            "CA-D-1007",
            prefix + "Archived",
            statement("Archived", "<owning scope unit>/<role folder>/wrong"),
            directory=self.root / "099_archived",
        )

    def test_exact_numbered_status_rules_and_current_source_boundary(self):
        self._write_status_sources()
        asset = self.root.parent / (self.root.name + "-status.json")
        self.addCleanup(asset.unlink, missing_ok=True)
        asset.write_bytes(compile_candidate_schema(self.root))
        rules = load_candidate_schema(asset).placement
        for status, expected in {
            "Draft": ("role", "000_draft"),
            "Backlog": ("role", "001_backlog"),
            "Active": ("container", ""),
            "Done": ("container", "020_done"),
            "Resolved": ("container", "021_resolved"),
            "Canceled": ("container", "040_canceled"),
            "Archived": ("role", "099_archived"),
        }.items():
            with self.subTest(status=status):
                self.assertEqual(expected, rules.placement("Plan", status))
        with self.assertRaises(ValueError):
            rules.placement("Plan", "Unknown")
        self.assertEqual(
            {
                "CA-D-1001",
                "CA-D-1002",
                "CA-D-1003",
                "CA-D-1004",
                "CA-D-1005",
                "CA-R-482",
            },
            {pin["atom_id"] for pin in rules.sources},
        )


if __name__ == "__main__":
    unittest.main()
