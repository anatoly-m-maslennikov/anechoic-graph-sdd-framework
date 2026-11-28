"""Unfiltered uniqueness is distinct from Active Plan uniqueness."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.\
    FEATURE_FORMAL_MODEL_ENGINE__shared \
    import (
    lint_python_model_claim,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared \
    import (
    EVENT_CLAIM as CLAIM,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared \
    import (
    EVENT_CLASS,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim,
)


class EventIDTests(unittest.TestCase):
    def test_unfiltered_rule_and_catalog(self):
        rule = parse_native_model_claim(CLAIM)["arguments"][
            "population_unique_constraints"
        ][0]
        self.assertEqual({"keys": ("ID",)}, rule)
        self.assertEqual(
            (),
            lint_python_model_claim(
                CLAIM,
                declared_addresses=["Event Record", "Event Record.ID"],
                relation_names=["IS_PROPERTY_OF"],
            ),
        )
        self.assertTrue(
            lint_python_model_claim(
                CLAIM,
                declared_addresses=["Event Record"],
                relation_names=["IS_PROPERTY_OF"],
            )
        )
        for invalid in (
            CLAIM.replace(
                '{"keys": ("ID",)}', '{"keys": ("ID",), "status": "Active"}'
            ),
            CLAIM.replace('{"keys": ("ID",)}', '{"keys": ()}'),
        ):
            with self.assertRaises(ValueError):
                parse_native_model_claim(invalid)

    def test_class_population_uniqueness_uses_declared_class(self):
        claim = EVENT_CLASS
        addresses = {
            "Atom",
            "Atom.Header.Identity.ID",
            "Atom.Header.State.Version",
        }
        parse_native_model_claim(claim)
        self.assertEqual(
            (),
            lint_python_model_claim(
                claim, declared_addresses=addresses, relation_names=()
            ),
        )
        self.assertIn(
            "unknown population Property",
            lint_python_model_claim(
                claim,
                declared_addresses=addresses - {"Atom.Header.State.Version"},
                relation_names=(),
            )[0],
        )
        invalid = claim.replace(
            "entity_class=Atom,",
            'entity_class=Atom, population_entity_path="Other",',
        )
        with self.assertRaises(ValueError):
            parse_native_model_claim(invalid)


if __name__ == "__main__":
    unittest.main()
