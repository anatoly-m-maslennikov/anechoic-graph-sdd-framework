"""Static direct-container uniqueness; no Python Claim is executed."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.\
    FEATURE_FORMAL_MODEL_ENGINE__shared \
    import (
    compiler_model_statements,
    lint_python_model_claim,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared \
    import (
    BASE,
    SEQ,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared \
    import (
    SEQUENCE_CLAIM as CLAIM,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared \
    import (
    SEQUENCE_PLAN as PLAN,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared \
    import (
    SEQUENCE_PROP as PROP,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared \
    import (
    NativeModelClaimError,
    parse_native_model_claim,
)  # fmt: skip

CATALOG = {
    "Atom",
    "Atom.Header.Context.Role",
    "Atom.Header.Context.Container.atom",
    "Atom.Header.Context.Container.scope_unit",
    "Atom.Header.State.Status",
    PLAN,
    BASE,
    PROP,
}


class PlanSequenceTests(unittest.TestCase):
    def lint(self, claim=CLAIM, addresses=CATALOG):
        return lint_python_model_claim(
            claim,
            declared_addresses=addresses,
            relation_names={"IS_PROPERTY_OF"},
        )

    def test_two_direct_containers_and_optional_positive_int(self):
        d = parse_native_model_claim(CLAIM)
        self.assertEqual((), self.lint())
        stmts = compiler_model_statements(d)
        self.assertEqual(
            (PROP + " :: [int]{::0..1}", PROP + ".*[]{::0}", PROP + " >= 1"),
            stmts,
        )

    def test_malformed_and_unresolved_inputs(self):
        for bad in (
            CLAIM.replace('"status":"Active"', '"status":"Draft"', 1),
            CLAIM.replace(
                '"single_value_paths": ("Header.Context.Container.atom", "'
                + SEQ
                + '")',
                '"single_value_paths": ("' + SEQ + '",)',
            ),
            CLAIM.replace(
                '"Header.Context.Container.atom", "' + SEQ + '"',
                '"../atom", "' + SEQ + '"',
                1,
            ),
            CLAIM.replace(
                'population_entity_path="' + PLAN + '"',
                'population_entity_path="Other"',
            ),
        ):
            with (
                self.subTest(bad=bad),
                self.assertRaises(NativeModelClaimError),
            ):
                parse_native_model_claim(bad)
        for missing in (
            "Atom.Header.Context.Container.atom",
            "Atom.Header.Context.Container.scope_unit",
            "Atom.Header.State.Status",
            PROP,
        ):
            with self.subTest(missing=missing):
                self.assertTrue(self.lint(addresses=CATALOG - {missing}))


if __name__ == "__main__":
    unittest.main()
