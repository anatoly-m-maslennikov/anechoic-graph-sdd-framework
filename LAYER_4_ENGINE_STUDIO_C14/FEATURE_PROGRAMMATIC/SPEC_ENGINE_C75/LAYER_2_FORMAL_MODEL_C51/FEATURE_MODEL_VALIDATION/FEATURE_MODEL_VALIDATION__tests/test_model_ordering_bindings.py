"""Bind actual native Property Declarations to scoped sibling order."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import parse_native_model_claim  # fmt: skip
from ..FEATURE_MODEL_VALIDATION__shared import (
    derive_declared_sibling_links,
    validate_declared_sibling_order,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import (
        bind_ordering_declarations,
        order_properties,
    )  # fmt: skip


def declaration(base, name, pairs, *, imports="", scopes=""):
    code = (
        "from anechoic.formal_claims import declare_entity\n"
        + imports
        + (
            "declare_entity(entity_name="
            f"{name!r}"
            ", relation_name='IS_PROPERTY_OF', "
        )
        + (
            "base_path="
            f"{base!r}"
            ", ordered_dependent_property_pairs="
            f"{pairs!r}"
            f"{scopes}"
            ")\n"
        )
    )
    return parse_native_model_claim(code)


class ModelOrderingBindingsTests(unittest.TestCase):
    def test_binds_header_and_role_scoped_content_separately(self):
        rows = [
            (
                "ANECHOIC_MODEL <+ Atom.Header",
                declaration(
                    "Atom",
                    "Header",
                    (("Identity", "Context"), ("Context", "State")),
                ),
            ),
            (
                "ANECHOIC_MODEL <+ Atom.Content",
                declaration(
                    "Atom",
                    "Content",
                    (("Summary", "Claim"), ("Claim", "Details")),
                    imports="from anechoic.model import Requirement, Method\n",
                    scopes=(
                        ", ordered_dependent_property_roles=(Requirement, "
                        "Method)"
                    ),
                ),
            ),
        ]
        bindings = bind_ordering_declarations(rows)
        header = bindings[("Atom.Header", ())]
        self.assertEqual(
            order_properties(["State", "Identity"], header),
            ["Identity", "State"],
        )
        self.assertIn(("Atom.Content", ("Method", "Requirement")), bindings)

    def test_validates_only_the_resolved_bearer_and_role(self):
        rows = [
            (
                "ANECHOIC_MODEL <+ Atom.Header.Context",
                declaration(
                    "Atom.Header",
                    "Context",
                    (("Form", "Label"), ("Label", "Topics")),
                    imports="from anechoic.model import Method\n",
                    scopes=", ordered_dependent_property_roles=(Method,)",
                ),
            )
        ]
        bindings = bind_ordering_declarations(rows)
        context = {"bearer": "Atom.Header.Context", "role": "Method"}
        validate_declared_sibling_order(
            bindings, present_properties=["Form", "Topics"], **context
        )
        self.assertEqual(
            derive_declared_sibling_links(
                bindings,
                present_properties=["Topics", "Extra", "Form"],
                **context,
            ),
            (("Topics", "Form"),),
        )
        with self.assertRaisesRegex(ValueError, "out of their declared order"):
            validate_declared_sibling_order(
                bindings, present_properties=["Topics", "Form"], **context
            )
        validate_declared_sibling_order(
            bindings,
            bearer="Atom.Header.Identity",
            role="Method",
            present_properties=["Topics", "Form"],
        )

    def test_keeps_qualified_bearer_and_overlapping_role_scopes(self):
        base = "Atom/(.Header.Context.Role := Plan).Content"
        row = (
            "ANECHOIC_MODEL <+ " + base + ".Claim",
            declaration(
                base,
                "Claim",
                (("Prose Claim", "Formal Claim"),),
                imports=(
                    "from anechoic.model import Plan, Method, Requirement\n"
                ),
                scopes=", applies_to_entity_classes=(Plan, Method), "
                "ordered_dependent_property_roles=(Method, Requirement)",
            ),
        )
        bindings = bind_ordering_declarations([row])
        (key,) = bindings
        self.assertIn("Role", key[0])
        self.assertEqual(key[1], ("Method",))

    def test_rejects_mismatch_duplicate_and_disconnected_order(self):
        item = declaration("Atom", "Header", (("Identity", "Context"),))
        row = ("ANECHOIC_MODEL <+ Atom.Header", item)
        with self.assertRaisesRegex(ValueError, "does not match"):
            bind_ordering_declarations(
                [("ANECHOIC_MODEL <+ Atom.Content", item)]
            )
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            bind_ordering_declarations([row, row])
        disconnected = declaration("Atom", "Header", (("A", "B"), ("C", "D")))
        with self.assertRaisesRegex(ValueError, "disconnected"):
            bind_ordering_declarations(
                [("ANECHOIC_MODEL <+ Atom.Header", disconnected)]
            )


if __name__ == "__main__":
    unittest.main()
