"""Read relation declarations in the pinned Claim syntax."""

from pathlib import Path
import sys
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(PROGRAMMATIC), str(PROGRAMMATIC / "FEATURE_TOOLS")]

from FEATURE_FORMAL_MODEL_ENGINE.project_claim_lint import _relation_declaration_context


class ProjectClaimLintTests(unittest.TestCase):
    def test_direct_and_legacy_relation_declaration_subjects(self):
        view = {"content_role": "Requirement", "type": "Relation Declaration"}
        for branch in ("", "CFEL <+ "):
            subject = f"ANECHOIC_MODEL <+ {branch}Relation//SPECIALIZES"
            with self.subTest(subject=subject):
                self.assertEqual(
                    _relation_declaration_context(dict(view, subjects={"active": subject})), "SPECIALIZES",
                )


if __name__ == "__main__":
    unittest.main()
