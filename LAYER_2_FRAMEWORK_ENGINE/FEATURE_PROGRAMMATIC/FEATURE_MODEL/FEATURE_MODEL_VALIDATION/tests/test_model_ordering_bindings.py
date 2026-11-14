"""Bind actual native Property Declarations to scoped sibling order."""

from pathlib import Path
import sys
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(PROGRAMMATIC), str(PROGRAMMATIC / "FEATURE_TOOLS")]

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_ordering_bindings import (
    bind_ordering_declarations, derive_declared_sibling_links, validate_declared_sibling_order,
)
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_property_order import order_properties


def declaration(base, name, pairs, *, imports="", scopes=""):
    code = (
        "from caprmedio.formal_claims import declare_entity\n"
        + imports
        + f"declare_entity(entity_name={name!r}, relation_name='IS_PROPERTY_OF', "
        + f"base_path={base!r}, ordered_dependent_property_pairs={pairs!r}{scopes})\n"
    )
    return parse_native_model_claim(code)


class ModelOrderingBindingsTests(unittest.TestCase):
    def test_binds_header_and_role_scoped_content_separately(self):
        rows = [
            ("CAPRMEDIO_MODEL <+ Atom.Header", declaration(
                "Atom", "Header", (("Identity", "Context"), ("Context", "State")))),
            ("CAPRMEDIO_MODEL <+ Atom.Content", declaration(
                "Atom", "Content", (("Summary", "Claim"), ("Claim", "Details")),
                imports="from caprmedio.model import Requirement, Method\n",
                scopes=", ordered_dependent_property_roles=(Requirement, Method)")),
        ]
        bindings = bind_ordering_declarations(rows)
        header = bindings[("Atom.Header", ())]
        self.assertEqual(order_properties(["State", "Identity"], header), ["Identity", "State"])
        self.assertIn(("Atom.Content", ("Method", "Requirement")), bindings)

    def test_validates_only_the_resolved_bearer_and_role(self):
        rows = [
            ("CAPRMEDIO_MODEL <+ Atom.Header.Context", declaration(
                "Atom.Header", "Context", (("Form", "Label"), ("Label", "Topics")),
                imports="from caprmedio.model import Method\n",
                scopes=", ordered_dependent_property_roles=(Method,)")),
        ]
        bindings = bind_ordering_declarations(rows)
        context = {"bearer": "Atom.Header.Context", "role": "Method"}
        validate_declared_sibling_order(bindings, present_properties=["Form", "Topics"], **context)
        self.assertEqual(
            derive_declared_sibling_links(bindings, present_properties=["Topics", "Extra", "Form"], **context),
            (("Topics", "Form"),),
        )
        with self.assertRaisesRegex(ValueError, "out of their declared order"):
            validate_declared_sibling_order(bindings, present_properties=["Topics", "Form"], **context)
        validate_declared_sibling_order(
            bindings, bearer="Atom.Header.Identity", role="Method", present_properties=["Topics", "Form"],
        )

    def test_keeps_qualified_bearer_and_overlapping_role_scopes(self):
        base = "Atom/(.Header.Context.Role := Plan).Content"
        row = ("CAPRMEDIO_MODEL <+ " + base + ".Claim", declaration(
            base, "Claim", (("Prose Claim", "Formal Claim"),),
            imports="from caprmedio.model import Plan, Method, Requirement\n",
            scopes=", applies_to_entity_classes=(Plan, Method), "
                   "ordered_dependent_property_roles=(Method, Requirement)"))
        bindings = bind_ordering_declarations([row])
        key, = bindings
        self.assertIn("Role", key[0])
        self.assertEqual(key[1], ("Method",))

    def test_rejects_mismatch_duplicate_and_disconnected_order(self):
        item = declaration("Atom", "Header", (("Identity", "Context"),))
        row = ("CAPRMEDIO_MODEL <+ Atom.Header", item)
        with self.assertRaisesRegex(ValueError, "does not match"):
            bind_ordering_declarations([("CAPRMEDIO_MODEL <+ Atom.Content", item)])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            bind_ordering_declarations([row, row])
        disconnected = declaration("Atom", "Header", (("A", "B"), ("C", "D")))
        with self.assertRaisesRegex(ValueError, "disconnected"):
            bind_ordering_declarations([("CAPRMEDIO_MODEL <+ Atom.Header", disconnected)])


if __name__ == "__main__":
    unittest.main()
