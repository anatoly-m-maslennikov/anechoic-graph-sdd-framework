from pathlib import Path
import sys
import unittest

from ._graph_native_parity_fixtures import STEP_CLAIM, WORKSPACE_CLAIM

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    GENERATE_ENTITY_GRAPH__shared import (
    compose_contract_graph,
    render_contract_graph,
    extract_claim_constraints,
    build_subject_projection_data,
)  # fmt: skip


def carrier(name, subject, code, label="python", form="Declaration"):
    return {
        "source": {"atom_id": name, "version": 1, "path": name + ".md"},
        "subjects": {"active": subject, "passive": []},
        "read_view": {"content_role": "Requirement", "type": form},
        "body": (
            f"## Claim\n\n### Formal Claim\n\n```{label}\n{code}\n```\n"
            "\n## Semantics\n\nA relation.\n"
        ),
    }


class GraphParity(unittest.TestCase):
    def test_native_special_contracts_project_fields_and_classification(self):
        code = WORKSPACE_CLAIM
        classification = (
            "from anechoic.formal_claims import "
            "declare_entity\n"
            'declare_entity(entity_name="Node", '
            'allowed_axis_values={"Container": ("yes", '
            '"no")})'
        )
        fields, errors = extract_claim_constraints(
            carrier("CA-R-1", "Workspace", code, "python")
        )
        allowed, more_errors = extract_claim_constraints(
            carrier("CA-R-2", "Node", classification, "python")
        )
        self.assertEqual(errors + more_errors, [])
        self.assertEqual(
            [row["kind"] for row in fields],
            ["property_constraint", "relation_cardinality"],
        )
        self.assertEqual(fields[0]["value_format"], "string")
        self.assertEqual(
            fields[1]["target_cardinality"], {"minimum": 1, "maximum": None}
        )
        self.assertEqual([row["value"] for row in allowed], ["yes", "no"])

    def test_typed_step_check_and_relation_permissions_project_together(self):
        step = carrier(
            "CA-R-2465",
            "Atom/(.Header.Context.Role:=Operations)/Step",
            (STEP_CLAIM),
            "python",
        )
        clauses, diagnostics = extract_claim_constraints(step)
        self.assertEqual([], diagnostics)
        (check,) = [
            clause for clause in clauses if clause["kind"] == "instance_check"
        ]
        self.assertEqual("step_has_one_execution_form", check["callback"])
        self.assertEqual(step["source"], check["source"])
        (node,) = compose_contract_graph([step])["entities"]
        self.assertIn(check, node["own"][0]["instance_clauses"])
        projection = build_subject_projection_data([step])
        entity = next(
            row
            for row in projection["entities"]
            if row["identity"] == node["target"]
        )
        rules = entity["relation_rule_origins"]["declared_here"]
        self.assertEqual(
            {"RUNS": ("Action", "Workflow"), "CONTAINS": ("Step",)},
            {
                rule["relation"]: rule["contract"]["target_entity_paths"]
                for rule in rules
            },
        )

    def test_relation_axes_are_separate_explicit_conditions(self):
        declaration = carrier(
            "CA-R-1",
            "Relation//LINKS",
            (
                "from anechoic.formal_claims import "
                "declare_relation\n"
                'declare_relation(relation_name="LINKS", '
                'inverse_alias="LINKED_BY",\n'
                '    source_endpoint={"level": "model_entities"},'
                ' target_endpoint={"level": "model_entities"},\n'
                '    axes={"Direction": "Forward"}, '
                'inverse_axes={"Direction": "Reverse"})'
            ),
            "python",
            "Relation Declaration",
        )
        clauses, diagnostics = extract_claim_constraints(declaration)
        self.assertEqual([], diagnostics)
        conditions = [
            row for row in clauses if row["kind"] == "axis_condition"
        ]
        self.assertEqual(
            [
                (
                    row["subject_selector"],
                    row["axis"],
                    row["operator"],
                    row["value"],
                )
                for row in conditions
            ],
            [
                ("Relation//LINKS", "Direction", "==", "Forward"),
                ("Relation//LINKED_BY", "Direction", "==", "Reverse"),
            ],
        )

    def test_instance_property_native(self):
        native = carrier(
            "CA-R-2524",
            "Project",
            (
                "from anechoic.formal_claims import "
                "declare_entity\n"
                "from anechoic.model import ScopeUnit\n"
                "class Project(ScopeUnit):\n"
                "    pass\n"
                "declare_entity(entity_class=Project, "
                'entity_name="Project", '
                'instance_property_constraints={"order.number": {'
                '"value_cardinality": 0}})'
            ),
            "python",
        )
        graph = compose_contract_graph([native])
        clause = next(
            c
            for c in graph["entities"][0]["own"][0]["instance_clauses"]
            if c["kind"] == "property_constraint"
        )
        self.assertEqual(clause["selection"], "values")
        self.assertEqual(
            clause["value_cardinality"], {"minimum": 0, "maximum": 0}
        )
        self.assertEqual(clause["group"], "instances")
        self.assertTrue(clause["property_selector"].endswith(".order.number"))
        rendered = render_contract_graph(graph)
        self.assertIn("Instance constraints:", rendered)
        self.assertIn("order.number` values", rendered)
        self.assertIn("values count=0", rendered)

    def test_model_inverse_alias_keeps_derived_reverse_view(self):
        c = carrier(
            "CA-R-2965",
            "CFEL <+ Relation//AFTER",
            (
                "from anechoic.formal_claims import "
                "declare_relation, Cardinality\n"
                'declare_relation(relation_name="AFTER", '
                'source_endpoint={"level": "model_entities", '
                '"entity_paths": ("Host",)}, target_endpoint={'
                '"level": "model_entities", "entity_paths": ('
                '"Target",)}, inverse_alias="BEFORE", '
                "targets_per_source=Cardinality(minimum=0, "
                "maximum=1), sources_per_target=Cardinality("
                "minimum=0, maximum=2))"
            ),
            "python",
            "Relation Declaration",
        )
        clauses, diag = extract_claim_constraints(c)
        self.assertFalse(diag)
        inverse = next(
            x for x in clauses if x.get("relation") == "IS_INVERSE_ALIAS_FOR"
        )
        self.assertEqual(
            (inverse["source_selector"], inverse["target_selector"]),
            ("Relation//BEFORE", "Relation//AFTER"),
        )
        self.assertIsNone(inverse["source_cardinality"])
        self.assertIsNone(inverse["target_cardinality"])
        self.assertEqual(inverse["written_direction"], "forward")
        self.assertFalse(
            any(x.get("relation") == "HAS_INVERSE" for x in clauses)
        )
        self._check_inverse_alias_graph(c)

    def _check_inverse_alias_graph(self, c):
        graph = compose_contract_graph([c])
        self.assertEqual([r["target"] for r in graph["relations"]], ["AFTER"])
        alias = graph["relations"][0]["derived_aliases"][0]
        self.assertEqual(
            (alias["name"], alias["classification"], alias["direct_relation"]),
            ("BEFORE", "Derived", "AFTER"),
        )
        endpoint = alias["endpoints"][0]
        self.assertEqual(endpoint["host"]["entity_paths"], ("Target",))
        self.assertEqual(endpoint["target"]["entity_paths"], ("Host",))
        self.assertEqual(
            endpoint["targets_per_source"], {"minimum": 0, "maximum": 2}
        )
        self.assertEqual(
            endpoint["sources_per_target"], {"minimum": 0, "maximum": 1}
        )
        rendered = render_contract_graph(graph)
        self.assertIn("Derived Relation `((BEFORE))`", rendered)
        self.assertIn("IS_INVERSE_ALIAS_FOR bindings", rendered)
        self.assertNotIn("HAS_INVERSE bindings", rendered)
        aliases = build_subject_projection_data([c])["relation_declarations"]
        self.assertTrue(
            any(
                r["name"] == "BEFORE"
                and r["derivation"] == "Derived"
                and r["direct_relations"] == ["AFTER"]
                for r in aliases
            )
        )

    def test_native_relation_keeps_endpoint_pairs_and_reverses_each_pair(self):
        declaration = carrier(
            "CA-R-2245",
            "CFEL <+ Relation//IS_EXECUTION_OF",
            (
                "from anechoic.formal_claims import "
                "declare_relation\n"
                "\n"
                "declare_relation(\n"
                '    relation_name="IS_EXECUTION_OF",\n'
                "    endpoint_pairs=(\n"
                '        {"source_endpoint": {"level": '
                '"instances", "entity_paths": ("Workflow Run",)},'
                "\n"
                '         "target_endpoint": {"level": '
                '"instances", "entity_paths": ("Workflow",)}},\n'
                '        {"source_endpoint": {"level": '
                '"instances", "entity_paths": ("Step Run",)},\n'
                '         "target_endpoint": {"level": '
                '"instances", "entity_paths": ("Step",)}},\n'
                "    ),\n"
                '    inverse_alias="HAS_EXECUTION",\n'
                "    targets_per_source=1,\n"
                ")\n"
            ),
            "python",
        )
        self._check_endpoint_pairs(declaration)

    def _check_endpoint_pairs(self, declaration):
        graph = compose_contract_graph([declaration])
        (relation,) = graph["relations"]
        pairs = relation["host_target"]
        self.assertEqual(
            [(("Workflow Run",), ("Workflow",)), (("Step Run",), ("Step",))],
            [
                (
                    p["source_endpoint"]["entity_paths"],
                    p["target_endpoint"]["entity_paths"],
                )
                for p in pairs
            ],
        )
        (inverse,) = relation["derived_aliases"]
        self.assertEqual("HAS_EXECUTION", inverse["name"])
        self.assertEqual(
            [(("Workflow",), ("Workflow Run",)), (("Step",), ("Step Run",))],
            [
                (p["host"]["entity_paths"], p["target"]["entity_paths"])
                for p in inverse["endpoints"]
            ],
        )
        self.assertTrue(
            all(
                p["sources_per_target"] == {"minimum": 1, "maximum": 1}
                for p in inverse["endpoints"]
            )
        )
        rendered = render_contract_graph(graph)
        _, _, contracts = rendered.partition("- Host / Target contracts:\n")
        pair_lines = contracts.split("\n- ", 1)[0].splitlines()
        self.assertEqual(2, len(pair_lines))
        self.assertIn("Workflow Run", pair_lines[0])
        self.assertIn("Step Run", pair_lines[1])
        self.assertTrue(
            all("targets per source=1" in line for line in pair_lines)
        )


if __name__ == "__main__":
    unittest.main()
