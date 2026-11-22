"""Read relation declarations in the pinned Claim syntax."""

from pathlib import Path
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[2]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_class_subject__pub import canonical_model_address


class ProjectClaimLintTests(unittest.TestCase):
    def test_direct_and_legacy_relation_declaration_subjects(self):
        for branch in ("", "CFEL <+ "):
            subject = f"ANECHOIC_MODEL <+ {branch}Relation//SPECIALIZES"
            with self.subTest(subject=subject):
                self.assertEqual(
                    canonical_model_address(subject), f"{branch}Relation//SPECIALIZES",
                )


if __name__ == "__main__":
    unittest.main()
