"""Check declared sibling ordering with optional Properties."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import order_properties  # fmt: skip

from ..FEATURE_MODEL_VALIDATION__shared import validate_declared_sibling_order


class PropertyOrderTests(unittest.TestCase):
    def test_skips_absent_properties_and_leaves_unordered_fields_last(self):
        pairs = (("Form", "Label"), ("Label", "Topics"))
        self.assertEqual(
            order_properties(["Custom", "Topics", "Form"], pairs),
            ["Form", "Topics", "Custom"],
        )
        self.assertEqual(
            order_properties(["Topics", "Label", "Form"], pairs),
            ["Form", "Label", "Topics"],
        )
        self.assertEqual(order_properties(["B", "A"], ()), ["B", "A"])
        self.assertEqual(
            order_properties(["Custom", "Label"], pairs), ["Label", "Custom"]
        )

    def test_rejects_cycles_branches_and_disconnected_chains(self):
        for pairs in (
            (("A", "B"), ("B", "A")),
            (("A", "B"), ("A", "C")),
            (("A", "B"), ("C", "B")),
            (("A", "B"), ("C", "D")),
            (("A", "B"), ("C", "D"), ("D", "C")),
        ):
            with self.subTest(pairs=pairs), self.assertRaises(ValueError):
                order_properties(["A"], pairs)

    def test_rejects_invalid_property_names_and_pairs(self):
        for names, pairs in ((["A", "A"], ()), ([""], ()), (["A"], (("A",),))):
            with (
                self.subTest(names=names, pairs=pairs),
                self.assertRaises(ValueError),
            ):
                order_properties(names, pairs)

    def test_validates_observed_order_with_optional_property_absent(self):
        pairs = (("Form", "Label"), ("Label", "Topics"))
        bearer = "Atom.Header.Context"
        bindings = {(bearer, ()): pairs}
        validate_declared_sibling_order(
            bindings,
            bearer=bearer,
            role="Method",
            present_properties=["Form", "Topics", "Other"],
        )
        with self.assertRaisesRegex(ValueError, "out of their declared order"):
            validate_declared_sibling_order(
                bindings,
                bearer=bearer,
                role="Method",
                present_properties=["Topics", "Form", "Other"],
            )
        with self.assertRaisesRegex(ValueError, "out of their declared order"):
            validate_declared_sibling_order(
                bindings,
                bearer=bearer,
                role="Method",
                present_properties=["Other", "Form", "Topics"],
            )
