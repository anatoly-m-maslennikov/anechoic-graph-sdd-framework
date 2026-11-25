"""Static Atom Status Group filtering for population dependency records."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import (
    compiler_model_statements,
    lint_python_model_claim,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    STATUS_GROUPS as CLAIM,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    NativeModelClaimError,
    parse_native_model_claim,
)

ADDRESSES = {
    "Atom",
    "Atom.Content",
    "Atom.Content.Summary",
    "Atom.Header.Identity.ID",
    "Atom.Header.State.Status",
}


class StatusGroupTests(unittest.TestCase):
    def test_filtered_dependency_and_rendering(self):
        decl = parse_native_model_claim(CLAIM)
        self.assertEqual(
            (),
            lint_python_model_claim(
                CLAIM,
                declared_addresses=ADDRESSES,
                relation_names={"IS_PROPERTY_OF"},
            ),
        )
        self.assertEqual(
            (
                "Atom.Content.Summary{::1} ::{::1}",
                "Atom.Content.Summary.*[]{::0}",
            ),
            compiler_model_statements(decl),
        )

    def test_invalid_filters_and_missing_paths(self):
        for bad in [
            CLAIM.replace(
                '"Current", "Backlog", "Archived"', '"Current", "NoSuchGroup"'
            ),
            CLAIM.replace(
                '"Current", "Backlog", "Archived"', '"Draft", "Draft"'
            ),
            CLAIM.replace('"Current", "Backlog", "Archived"', '["bad"]'),
            CLAIM.replace(
                'population_entity_path="Atom"',
                'population_entity_path="Other"',
            ),
            CLAIM.replace(
                '"status_groups": ("Current", "Backlog", "Archived")',
                '"status_groups": ()',
            ),
        ]:
            with (
                self.subTest(bad=bad),
                self.assertRaises(NativeModelClaimError),
            ):
                parse_native_model_claim(bad)
        for missing in ADDRESSES:
            with self.subTest(missing=missing):
                self.assertTrue(
                    lint_python_model_claim(
                        CLAIM,
                        declared_addresses=ADDRESSES - {missing},
                        relation_names={"IS_PROPERTY_OF"},
                    )
                )


if __name__ == "__main__":
    unittest.main()
