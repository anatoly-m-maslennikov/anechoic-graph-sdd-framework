"""Recursive contract-evidence graph case."""

from importlib import import_module

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.contracts__shared"
)
build_subject_projection_data = _graph.build_subject_projection_data
carrier, body = _support.carrier, _support.body


class ContractEvidenceCases:
    def test_content_recursion_is_general_and_ordering_is_rmed_only(self):
        roles, projection = self.recursion_projection()
        entries = projection["declarations"]["properties"]["Atom.Content"]
        self.assertFalse(entries[0]["diagnostics"])
        for name in (*roles, "Analysis"):
            entity = next(
                row
                for row in projection["entities"]
                if row["identity"].endswith(f":={name})")
            )
            props = {
                item["identity"]: item
                for item in entity["inherited_properties"]
            }
            self.assertEqual(
                "markdown",
                props["Atom.Content.Extra.Nested"]["effective_value_format"],
            )
            contracts = props["Atom.Content"]["contracts"]
            self.assertTrue(
                any(
                    c.get("selection") == "recursive_dependents"
                    for c in contracts
                )
            )
            pairs = [
                (
                    c["source_selector"].rsplit(".", 1)[1],
                    c["target_selector"].rsplit(".", 1)[1],
                )
                for c in contracts
                if c.get("relation") == "IS_ORDERED_RIGHT_BEFORE"
            ]
            self.assertEqual(
                [
                    ("Summary", "Claim"),
                    ("Claim", "Semantics"),
                    ("Semantics", "Details"),
                ]
                if name in roles
                else [],
                pairs,
            )

    def recursion_projection(self):
        roles = ("Requirement", "Method", "Evaluation", "Delivery")
        atom = carrier("CA-R-1", "Atom", body())
        role_rows = [
            carrier(
                f"CA-R-{index}",
                f"Atom/(.Header.Context.Role:={name})",
                body(
                    "### Formal Claim",
                    "```python",
                    "from anechoic.formal_claims import declare_entity",
                    "from anechoic.model import Atom",
                    f"class {name}(Atom):",
                    "    pass",
                    f"declare_entity(entity_class={name}, "
                    f"entity_name='{name}', "
                    "qualification_property_path='Atom.Header.Context.Role')",
                    "```",
                ),
            )
            for index, name in enumerate((*roles, "Analysis"), start=2)
        ]
        native = self.recursion_native()
        extra = carrier("CA-R-8", "Atom.Content.Extra.Nested", body())
        projection = build_subject_projection_data(
            [
                atom,
                *role_rows,
                carrier("CA-R-7", "Atom.Content", native),
                extra,
            ]
        )
        return roles, projection

    def recursion_native(self):
        return body(
            "### Formal Claim",
            "```python",
            "from anechoic.formal_claims import Cardinality, declare_entity",
            (
                "from anechoic.model import Requirement, "
                "Method, Evaluation, Delivery"
            ),
            (
                "declare_entity(entity_name='Content', re"
                "lation_name='IS_PROPERTY_OF', base_path="
                "'Atom',"
            ),
            "  property_occurrence_cardinality=1, value_cardinality=0,",
            (
                "  dependent_property_cardinality=Cardina"
                "lity(minimum=0, maximum=None), dependent"
                "_property_name_format=str,"
            ),
            (
                "  recursive_dependent_property_cardinali"
                "ty=Cardinality(minimum=0, maximum=None),"
            ),
            (
                "  recursive_dependent_property_name_form"
                "at=str, recursive_dependent_property_val"
                "ue_format='markdown',"
            ),
            (
                "  ordered_dependent_property_roles=(Requ"
                "irement, Method, Evaluation, Delivery),"
            ),
            (
                "  ordered_dependent_property_pairs=(('Su"
                "mmary', 'Claim'), ('Claim', 'Semantics')"
                ", ('Semantics', 'Details')))"
            ),
            "```",
        )
