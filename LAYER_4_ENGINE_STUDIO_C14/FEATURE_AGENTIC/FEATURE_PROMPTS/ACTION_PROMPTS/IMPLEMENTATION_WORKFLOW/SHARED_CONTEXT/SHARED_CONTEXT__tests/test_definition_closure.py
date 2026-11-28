"""Check workflow definition closure rules."""

import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parents[1]


class SharedDefinitionClosure(unittest.TestCase):
    def test_preparation_and_repair_keep_review_and_check_closure(self):
        prepare = (HERE / "CA-O-231.prompt.md").read_text()
        repair = (HERE / "CA-O-099.prompt.md").read_text()
        self.assertIn("`review_ready`", prepare)
        self.assertIn("R/M/D obligations", prepare)
        self.assertIn("same candidate", prepare)
        self.assertIn("mark affected previous review/check evidence", repair)
        self.assertIn("remaining budget", repair)

    def test_final_checks_require_current_preliminary_clearance(self):
        checks = (HERE / "verification/CA-O-094.prompt.md").read_text()
        self.assertIn(
            "For final checks require actual `preliminary_clear`", checks
        )
        self.assertIn("this exact", checks)
        self.assertIn(
            "candidate and relevant source/test/input bindings", checks
        )
        self.assertIn("If it is missing or stale", checks)
        self.assertIn("return `blocked`, never `passed`", checks)
        self.assertIn("baseline checks", checks)
        self.assertIn("do not require preliminary clearance", checks)

    def test_summary_replacements_use_distinct_current_source_identities(self):
        frontier = json.loads(
            (HERE / "definition_frontier.projection.json").read_text()
        )
        ids = {row["atom_id"] for row in frontier["sources"]}
        self.assertTrue(
            {"CA-O-231", "CA-O-232", "CA-O-233", "CA-O-234", "CA-E-652"} <= ids
        )
        self.assertFalse(
            {"CA-O-091", "CA-O-092", "CA-O-093", "CA-O-095", "CA-E-519"} & ids
        )


if __name__ == "__main__":
    unittest.main()
