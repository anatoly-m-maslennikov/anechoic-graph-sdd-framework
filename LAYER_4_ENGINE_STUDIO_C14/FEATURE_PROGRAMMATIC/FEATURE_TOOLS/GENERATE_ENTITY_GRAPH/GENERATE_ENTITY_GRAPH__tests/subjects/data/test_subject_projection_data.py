"""Subject projection data is declaration-only for detail evidence."""

from pathlib import Path
import sys
import unittest


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import (
        build_subject_projection_data,
        render_primary_projection,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    GENERATE_ENTITY_GRAPH__tests.subjects.data.projection_data_fixtures import (
        inherited_format_carriers,
        duplicate_property_carriers,
        inherited_contract_carriers,
        nondeclaration_carriers,
        namespace_carriers,
        INHERITED_EXPECTED,
    )  # fmt: skip

TOOL = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]


def carrier(atom_id, subject, body, *, role="Requirement", form="Declaration"):
    return {
        "source": {
            "atom_id": atom_id,
            "version": 1,
            "path": f"sources/{atom_id}.md",
        },
        "subjects": {"active": subject, "passive": []},
        "body": body,
        "read_view": {"content_role": role, "type": form},
    }


def claim(*lines):
    return "## Claim\n\n" + "\n".join(lines) + "\n"


class SubjectProjectionDataTests(unittest.TestCase):
    def test_encoded_roles_and_forms_keep_declaration_evidence(self):
        body = claim(
            "```python",
            (
                "property_rule(address='Node.Name', "
                "value_format='string', values='1')"
            ),
            "```",
        )
        canonical = [
            carrier("CA-R-1", "Node", claim("Node.")),
            carrier("CA-R-2", "Node.Name", body),
        ]
        encoded = [
            carrier(
                "CA-R-1",
                "Node",
                claim("Node."),
                role="requirement",
                form="declaration",
            ),
            carrier(
                "CA-R-2",
                "Node.Name",
                body,
                role="requirement",
                form="declaration",
            ),
        ]
        self.assertEqual(
            build_subject_projection_data(canonical),
            build_subject_projection_data(encoded),
        )

    def test_inherited_model_format_and_instance_constraints_stay_separate(
        self,
    ):
        data = build_subject_projection_data(
            inherited_format_carriers(carrier, claim)
        )
        child = next(
            row for row in data["entities"] if row["identity"] == "Node/Child"
        )
        prop = child["inherited_properties"][0]
        self.assertEqual(
            ["string"], [row["value_format"] for row in prop["contracts"]]
        )
        self.assertEqual(
            ["property_constraint"],
            [row["kind"] for row in prop["instance_constraints"]],
        )
        self.assertIn("# model", prop["formal_claims"][0]["block"])
        self.assertIn("# instances", prop["formal_claims"][0]["block"])
        self.assertFalse(
            any("$n" in row["identity"] for row in data["entities"])
        )
        inspector = render_primary_projection(data, 4)
        self.assertIn(
            INHERITED_EXPECTED,
            inspector,
        )

    def test_keeps_explicit_new_namespace_roots(self):
        data = build_subject_projection_data(
            [
                carrier("CA-R-1", "ANECHOIC_MODEL", claim("Model root.")),
                carrier("CA-R-2", "ANECHOIC_MODEL <+ Node", claim("Node.")),
                carrier(
                    "CA-R-3",
                    "ANECHOIC_STRUCTURE <+ Project",
                    claim("Project."),
                ),
            ]
        )
        self.assertEqual(
            [("ANECHOIC_MODEL", "CA-R-1"), ("ANECHOIC_STRUCTURE", "CA-R-3")],
            [
                (row["subject"], row["source"]["atom_id"])
                for row in data["namespaces"]
            ],
        )

    def _check_namespace_root_context(
        self,
    ):
        data = build_subject_projection_data(
            namespace_carriers(carrier, claim)
        )

        self.assertEqual(
            [
                ("ANECHOIC <+ MODEL", "CA-R-1"),
                ("ANECHOIC <+ STRUCTURE", "CA-R-3"),
            ],
            [
                (row["subject"], row["source"]["atom_id"])
                for row in data["namespaces"]
            ],
        )

    def test_does_not_invent_namespace_context_without_an_explicit_prefix(
        self,
    ):
        data = build_subject_projection_data(
            [
                carrier("CA-R-1", "Node", claim("Node declaration.")),
                carrier("CA-R-2", "Project", claim("Project declaration.")),
            ]
        )

        self.assertEqual([], data["namespaces"])

    def test_keeps_exact_component_declaration_for_a_retained_tree_entity_only(
        self,
    ):
        data = build_subject_projection_data(
            [
                carrier(
                    "CA-R-1",
                    "CFEL",
                    claim(
                        "```python",
                        (
                            "property_rule(address='CFEL', "
                            "value_format='string', values='1')"
                        ),
                        "```",
                    ),
                    form="Entity Definition",
                ),
                carrier(
                    "CA-R-2",
                    "CFEL <+ Operator",
                    claim(
                        "```python",
                        (
                            "property_rule(address='Operator', "
                            "value_format='string', values='1')"
                        ),
                        "```",
                    ),
                ),
            ]
        )

        entities = {row["identity"]: row for row in data["entities"]}
        self.assertEqual(
            ["CA-R-2@1"], entities["Operator"]["declaration_refs"]
        )
        self.assertEqual(
            ["CA-R-2"],
            [
                row["source"]["atom_id"]
                for row in entities["Operator"]["formal_claims"]
            ],
        )
        self.assertEqual([], entities["CFEL"]["formal_claims"])
        self.assertIn("Operator", data["declarations"]["primary_nodes"])

    def test_catalog_keeps_exact_instances_relations_and_components_only(self):
        data = build_subject_projection_data(
            [
                carrier("CA-R-1", "Node", claim("Node declaration.")),
                carrier(
                    "CA-R-2", "Node//Example", claim("Instance declaration.")
                ),
                carrier(
                    "CA-R-3",
                    "CFEL <+ Relation//RUN",
                    claim("Relation declaration."),
                ),
                carrier(
                    "CA-R-4", "CFEL <+ Format", claim("Component declaration.")
                ),
                carrier("CA-R-5", "Node//Poison", claim("Rule."), form="Rule"),
            ]
        )

        declarations = data["declarations"]
        self.assertEqual(["Node//Example"], list(declarations["instances"]))
        self.assertEqual(["RUN"], list(declarations["relations"]))
        self.assertEqual(["Format"], list(declarations["components"]))
        self.assertNotIn("Node//Poison", declarations["instances"])

    def _check_duplicate_properties(
        self,
    ):
        data = build_subject_projection_data(
            duplicate_property_carriers(carrier, claim)
        )

        property = next(
            row for row in data["entities"] if row["identity"] == "Node"
        )["direct_properties"][0]
        self.assertTrue(property["multiple_applicable"])
        self.assertEqual(
            ["CA-R-2@1", "CA-R-3@1"], property["declaration_refs"]
        )
        self.assertEqual(
            ["Draft", "Review"],
            [row["literal"] for row in property["contracts"]],
        )
        self.assertEqual(
            ["Node.Status"],
            [
                row["target"]
                for row in data["diagnostics"]
                if row.get("code") == "duplicate_exact_declaration"
            ],
        )

    def _check_inherited_constraints(
        self,
    ):
        data = build_subject_projection_data(
            inherited_contract_carriers(carrier, claim)
        )

        child = next(
            row for row in data["entities"] if row["identity"] == "Node/Child"
        )
        self.assertEqual(["Node"], child["ancestors"])
        self.assertEqual(
            "Node/Child.Status", child["direct_properties"][0]["identity"]
        )
        self.assertEqual(
            "Node.Status", child["inherited_properties"][0]["identity"]
        )
        self.assertTrue(child["direct_properties"][0]["multiple_applicable"])
        contract = child["direct_properties"][0]["contracts"][0]
        self.assertIsNone(contract["name_format"])
        self.assertEqual(
            {"minimum": 0, "maximum": 1}, contract["occurrence_cardinality"]
        )
        self.assertEqual("integer", contract["value_format"])
        self.assertEqual(
            {"minimum": 2, "maximum": 2}, contract["value_cardinality"]
        )
        self.assertEqual(
            "CA-R-3@1", child["inherited_properties"][0]["declaration_refs"][0]
        )

    def test_excludes_non_declaration_claims_before_formal_extraction(self):
        carriers = nondeclaration_carriers(carrier, claim)
        for carrier_row in carriers:
            carrier_row["raw"] = repr(carrier_row).encode()
        source_bytes = [carrier_row["raw"] for carrier_row in carriers]
        data = build_subject_projection_data(carriers)

        property = next(
            row for row in data["entities"] if row["identity"] == "Node"
        )["direct_properties"][0]
        self.assertEqual(
            ["Draft"], [row["literal"] for row in property["contracts"]]
        )
        self.assertEqual(
            ["CA-R-2"],
            [row["source"]["atom_id"] for row in property["formal_claims"]],
        )
        self.assertEqual(2, data["coverage"]["detail_declaration_sources"])
        self.assertEqual(
            source_bytes, [carrier_row["raw"] for carrier_row in carriers]
        )


setattr(
    SubjectProjectionDataTests,
    "test_keeps_one_explicit_root_namespace_context_and_"
    "uses_prefix_only_as_fallback",
    SubjectProjectionDataTests._check_namespace_root_context,
)
setattr(
    SubjectProjectionDataTests,
    "test_surfaces_duplicate_exact_property_declarations_without_merging_them",
    SubjectProjectionDataTests._check_duplicate_properties,
)
setattr(
    SubjectProjectionDataTests,
    "test_keeps_inherited_original_property_and_all_"
    "constraint_channels_without_merging",
    SubjectProjectionDataTests._check_inherited_constraints,
)

if __name__ == "__main__":
    unittest.main()
