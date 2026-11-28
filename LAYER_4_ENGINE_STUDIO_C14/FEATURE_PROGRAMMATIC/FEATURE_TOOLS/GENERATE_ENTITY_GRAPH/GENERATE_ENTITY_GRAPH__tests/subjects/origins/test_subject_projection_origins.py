"""Rule origin separates inheritance, local overrides and Relation \
classification."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[3]))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import (
        _rule_groups,
        build_subject_projection_data,
        render_primary_projection,
    )  # fmt: skip

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    GENERATE_ENTITY_GRAPH__tests.subjects.origins.projection_origin_fixtures import (
        local_override_carriers,
        inverse_relation_declaration,
        authored_relation_carriers,
        DIRECT_RELATION_CLAIM,
        INSTANCE_RELATION_CLAIM,
    )  # fmt: skip


def carrier(atom_id, subject, expression, *, form="Declaration"):
    return {
        "source": {"atom_id": atom_id, "version": 1, "path": atom_id + ".md"},
        "subjects": {"active": subject, "passive": []},
        "body": "## Claim\n\n### Formal Claim\n\n```python\n"
        + expression
        + "\n```\n",
        "read_view": {"content_role": "Requirement", "type": form},
    }


class RuleOriginTests(unittest.TestCase):
    def test_symbolic_relation_requires_an_unambiguous_declared_alias(self):
        node = carrier(
            "CA-R-1",
            "Node",
            "# model\ncomposition(container='Node', parts=('Node',))",
        )
        declared = carrier(
            "CA-R-2",
            "CFEL <+ Relation//LINKS",
            DIRECT_RELATION_CLAIM,
            form="Relation Declaration",
        )
        data = build_subject_projection_data([node, declared])
        entity = next(
            row for row in data["entities"] if row["identity"] == "Node"
        )
        (relation,) = entity["relation_rule_origins"]["declared_here"]
        self.assertEqual(
            ("LINKS", "Direct"), (relation["relation"], relation["derivation"])
        )
        competing = carrier(
            "CA-R-3",
            "CFEL <+ Relation//OTHER",
            (
                "from anechoic.formal_claims import "
                "declare_relation\n"
                "declare_relation(relation_name='OTHER', "
                "written_alias='<+', source_endpoint={"
                "'level': 'model_entities'}, "
                "target_endpoint={'level': "
                "'model_entities'})"
            ),
            form="Relation Declaration",
        )
        data = build_subject_projection_data([node, declared, competing])
        entity = next(
            row for row in data["entities"] if row["identity"] == "Node"
        )
        self.assertEqual([], entity["relation_rule_origins"]["declared_here"])

    def test_unbounded_structural_fact_is_not_an_inherited_relation_rule(self):
        data = build_subject_projection_data(
            [
                carrier(
                    "CA-R-1",
                    "Node",
                    (
                        "relation(source='Node', name='NARROWER_THAN', "
                        "target='Root')\n"
                        "relation(source='Node', name='NARROWER_THAN', "
                        "target='Node', source_count='0+')"
                    ),
                ),
                carrier(
                    "CA-R-2",
                    "Node/Child",
                    (
                        "relation(source='Node/Child', "
                        "name='NARROWER_THAN', target='Node')"
                    ),
                ),
            ]
        )
        child = next(
            row for row in data["entities"] if row["identity"] == "Node/Child"
        )
        self.assertEqual([], child["relation_rule_origins"]["overridden_here"])
        (rule,) = child["relation_rule_origins"]["inherited"]
        self.assertEqual(
            "Node {::0+}((NARROWER_THAN)) Node", rule["expression"]
        )

    def test_unrelated_ancestors_keep_both_inherited_rules(self):
        rules = [
            {
                "relative_name": "Status",
                "origin_entity": origin,
                "declaration_refs": [origin + "@1"],
                "source_refs": [],
            }
            for origin in ("ParentA", "ParentB", "Grandparent")
        ]
        ancestors = {
            "Child": ["ParentA", "ParentB", "Grandparent"],
            "ParentA": ["Grandparent"],
        }
        groups = _rule_groups(
            "Child", rules, ancestors, lambda row: row["relative_name"]
        )
        self.assertEqual(
            {"ParentA", "ParentB"},
            {row["origin_entity"] for row in groups["inherited"]},
        )
        parent_a = next(
            row
            for row in groups["inherited"]
            if row["origin_entity"] == "ParentA"
        )
        self.assertEqual(
            ["Grandparent"],
            [row["origin_entity"] for row in parent_a["replaces"]],
        )
        self.assertEqual([], groups["overridden_here"])

    def test_local_overrides_keep_source_and_level_separate(self):
        data = build_subject_projection_data(local_override_carriers(carrier))
        child = next(
            row for row in data["entities"] if row["identity"] == "Node/Child"
        )
        prop = child["property_rule_origins"]["overridden_here"][0]
        self.assertEqual(
            ("Node/Child.Status", "Node"),
            (prop["identity"], prop["replaces"][0]["origin_entity"]),
        )
        self.assertEqual(["CA-R-3@1"], prop["replaces"][0]["declaration_refs"])
        self.assertEqual([], child["property_rule_origins"]["inherited"])
        (overridden,) = child["relation_rule_origins"]["overridden_here"]
        self.assertEqual(
            ("LINKS", "model", "Direct"),
            (
                overridden["relation"],
                overridden["level"],
                overridden["derivation"],
            ),
        )
        self.assertEqual(
            ["CA-R-1@1"], overridden["replaces"][0]["declaration_refs"]
        )
        (inherited,) = child["relation_rule_origins"]["inherited"]
        self.assertEqual(
            ("LINKS", "instances", "Node"),
            (
                inherited["relation"],
                inherited["level"],
                inherited["origin_entity"],
            ),
        )
        self.assertEqual([], child["relation_rule_origins"]["declared_here"])
        self._check_override_rendering(data)

    def _check_override_rendering(self, data):
        rendered = render_primary_projection(data, 4)
        self.assertIn("#### Overridden here", rendered)
        self.assertIn("Relation `LINKS` (Direct, model, forward)", rendered)
        self.assertIn("Replaces rule from `Node` — CA-R-3@1", rendered)
        self.assertIn(
            (
                "property: `Node.Status` (relative "
                "`Status`) [inherited] [overridden]"
            ),
            rendered,
        )
        self.assertIn(
            "contract: `Node.Status:: [string]{::1}` — CA-R-3@1", rendered
        )
        self.assertIn("Rule: `Node {::0+}((LINKS)) Node`", rendered)

    def test_only_authored_relations_get_permissions_and_classification(self):
        data = build_subject_projection_data(
            authored_relation_carriers(carrier)
        )
        node = next(
            row for row in data["entities"] if row["identity"] == "Node"
        )
        rules = node["relation_rule_origins"]["declared_here"]
        self.assertEqual(2, len(rules))
        self.assertEqual(
            {
                ("LINKS", "model", "forward", "Direct"),
                ("BELONGS", "model", "reverse", "Derived"),
            },
            {
                (r["relation"], r["level"], r["direction"], r["derivation"])
                for r in rules
            },
        )

    def test_native_relation_constraints_have_instance_scope(self):
        python = INSTANCE_RELATION_CLAIM
        native = carrier("CA-R-2", "Node/Child", "")
        native["body"] = (
            "## Claim\n\n### Formal Claim\n\n```python\n" + python + "\n```\n"
        )
        data = build_subject_projection_data(
            [
                carrier(
                    "CA-R-1",
                    "Node",
                    (
                        "relation(source='Node', "
                        "name='NARROWER_THAN', target='Root')"
                    ),
                ),
                native,
            ]
        )
        child = next(
            row for row in data["entities"] if row["identity"] == "Node/Child"
        )
        (rule,) = child["relation_rule_origins"]["declared_here"]
        self.assertEqual(
            ("IS_CONTAINED_BY", "instances", "forward"),
            (rule["relation"], rule["level"], rule["direction"]),
        )
        self.assertEqual(("Node",), rule["contract"]["target_entity_paths"])
        self.assertIsNone(rule["derivation"])
        self.assertIn(
            (
                "Contract: `{'target_entity_paths': ('Node',), "
                "'targets_per_source': 0}`"
            ),
            render_primary_projection(data, 4),
        )

    def test_native_inverse_alias_classifies_only_an_authored_rule(self):
        declaration = inverse_relation_declaration(carrier)
        data = build_subject_projection_data(
            [
                carrier(
                    "CA-R-1",
                    "Node",
                    (
                        "# model\n"
                        "relation(source='Node', "
                        "name='LINKED_BY', target='Node')"
                    ),
                ),
                carrier(
                    "CA-R-3",
                    "Node/Other",
                    (
                        "# model\n"
                        "relation(source='Node/Other', "
                        "name='LINKS', target='Node')"
                    ),
                ),
                declaration,
            ]
        )
        self._check_native_inverse_alias(data)

    def _check_native_inverse_alias(self, data):
        node = next(
            row for row in data["entities"] if row["identity"] == "Node"
        )
        (rule,) = node["relation_rule_origins"]["declared_here"]
        self.assertEqual(
            ("LINKED_BY", "Derived"), (rule["relation"], rule["derivation"])
        )
        self.assertNotIn(
            "LINKS",
            [
                row["relation"]
                for row in node["relation_rule_origins"]["declared_here"]
            ],
        )
        alias = next(
            row
            for row in data["relation_declarations"]
            if row["name"] == "LINKED_BY"
        )
        self.assertEqual(
            ("Derived", ["LINKS"], ["CA-R-2@1"]),
            (
                alias["derivation"],
                alias["direct_relations"],
                alias["declaration_refs"],
            ),
        )
        output = render_primary_projection(data, 4)
        self.assertIn("### Derived", output)
        self.assertIn("`LINKED_BY` — CA-R-2@1; inverse of `LINKS`", output)


if __name__ == "__main__":
    unittest.main()
