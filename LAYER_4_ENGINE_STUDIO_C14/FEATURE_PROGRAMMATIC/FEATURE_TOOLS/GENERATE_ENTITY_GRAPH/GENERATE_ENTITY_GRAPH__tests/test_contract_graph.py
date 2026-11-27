"""Source-bound graph native cases."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(TOOL.parent))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import render_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import extract_claim_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.contract_graph_test_support import carrier, body


class ContractGraphTests(unittest.TestCase):
    def test_ambiguous_native_inverse_does_not_create_a_derived_view(self):
        def direct(atom_id, name):
            return carrier(atom_id, "Relation//" + name, body(
                "### Formal Claim", "```python",
                "from anechoic.formal_claims import declare_relation",
                f"declare_relation(relation_name='{name}', source_endpoint={{'level':'instances'}},",
                "  target_endpoint={'level':'instances'}, inverse_alias='SHARED')",
                "```", semantics="Direct meaning."))
        graph = compose_contract_graph([direct("CA-R-1", "FIRST"), direct("CA-R-2", "SECOND")])
        self.assertTrue(all("derived_aliases" not in row for row in graph["relations"]))
        declared = carrier("CA-R-3", "Relation//SHARED", body("### Prose Claim", "Other meaning."))
        graph = compose_contract_graph([direct("CA-R-1", "FIRST"), declared])
        self.assertTrue(all("derived_aliases" not in row for row in graph["relations"]))

    def test_native_forms_with_same_local_class_name_keep_distinct_parents(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_narrowing_graph

        root = carrier("CA-R-1", "Atom", body())
        carriers = [root]
        for index, role in enumerate(("Method", "Evaluation"), 2):
            parent = f"Atom/(.Header.Context.Role := {role})"
            carriers.append(carrier(f"CA-R-{index}", parent, body(
                "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
                "from anechoic.model import Atom", f"class {role}(Atom):", "    pass",
                f"declare_entity(entity_class={role}, entity_name='{role}')", "```")))
            carriers.append(carrier(f"CA-R-{index + 10}", parent + "/(.Header.Context.Form := Decision)", body(
                "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
                f"from anechoic.model import {role}", f"class Decision({role}):", "    pass",
                "declare_entity(entity_class=Decision, entity_name='Decision')", "```")))
        tree, _ = compose_narrowing_graph(carriers)
        identities = {node["id"]: node["identity"] for node in tree["nodes"]}
        edges = {(identities[edge["relation_source"]], identities[edge["relation_target"]])
                 for edge in tree["edges"]}
        for role in ("Method", "Evaluation"):
            parent = f"Atom/(.Header.Context.Role:={role})"
            self.assertIn((parent + "/(.Header.Context.Form:=Decision)", parent), edges)

    def test_native_namespace_classification_keeps_source(self):
        row = carrier("CA-R-1", "ANECHOIC_MODEL", body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
            "from anechoic.model import Node", "class Model(Node):", "    pass",
            'declare_entity(entity_class=Model, entity_name="MODEL", axes={"Container": "yes"})',
            "```"))
        graph = compose_contract_graph([row])
        namespace, = graph["namespaces"]
        entry, = namespace["own"]
        condition, = [clause for clause in entry["clauses"] if clause["kind"] == "axis_condition"]
        self.assertEqual(("MODEL", "Container", "==", "yes"),
                         tuple(condition[key] for key in ("subject_selector", "axis", "operator", "value")))
        self.assertEqual(row["source"], condition["source"])
        self.assertIn("MODEL >| Container == yes", render_contract_graph(graph))

    def test_native_dependent_counts(self):
        address = "Atom.Header.Relations"
        native = body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
            "from anechoic.formal_claims import Cardinality",
            "declare_entity(entity_name='Relations', relation_name='IS_PROPERTY_OF', base_path='Atom.Header',",
            "  property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), value_cardinality=0,",
            "  dependent_property_cardinality=Cardinality(minimum=1, maximum=None), dependent_property_name_format=str,",
            "  dependent_property_value_format=str,",
            "  dependent_property_value_cardinality=Cardinality(minimum=1, maximum=None))", "```")

        def contracts(claim):
            atom = carrier("CA-R-1", address, claim)
            graph = compose_contract_graph([atom])
            entry, = next(row for row in graph["entities"] if row["target"] == address)["own"]
            self.assertFalse(entry["diagnostics"])

            def format_name(value):
                return "string" if value == "str" else value or None

            return {
                clause["selection"]: (format_name(clause.get("name_format")),
                                      clause.get("occurrence_cardinality"),
                                      format_name(clause.get("value_format")), clause.get("value_cardinality"))
                for clause in entry["clauses"] if clause["kind"] == "property_constraint"
            }

        self.assertEqual({
            "property": (None, {"minimum": 0, "maximum": 1}, None, {"minimum": 0, "maximum": 0}),
            "immediate_dependents": ("string", {"minimum": 1, "maximum": None}, None, None),
            "immediate_dependent_values": (None, None, "string", {"minimum": 1, "maximum": None}),
        }, contracts(native))

    def test_native_order_keeps_property_scope_and_source(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import build_subject_projection_data

        atom = carrier("CA-R-1", "Atom", body())
        claim = carrier("CA-R-2", "Atom.Content.Claim", body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
            "from anechoic.model import Requirement, Method, Evaluation, Delivery",
            "declare_entity(entity_name='Claim', relation_name='IS_PROPERTY_OF', base_path='Atom.Content',",
            "  dependent_property_cardinality=2, allowed_dependent_property_names=('Prose Claim', 'Formal Claim'),",
            "  ordered_dependent_property_pairs=(('Prose Claim', 'Formal Claim'),),",
            "  applies_to_entity_classes=(Requirement, Method, Evaluation, Delivery))", "```"))
        graph = compose_contract_graph([atom, claim])
        prop = next(node for node in graph["entities"] if node["target"] == "Atom.Content.Claim")
        order, = [clause for clause in prop["own"][0]["clauses"]
                  if clause.get("relation") == "IS_ORDERED_RIGHT_BEFORE"]
        self.assertEqual("relation_cardinality", order["kind"])
        self.assertEqual("Atom.Content.Claim", order["bearer"])
        self.assertEqual(("Atom.Content.Claim.Prose Claim", "Atom.Content.Claim.Formal Claim"),
                         (order["source_selector"], order["target_selector"]))
        self.assertEqual(("Requirement", "Method", "Evaluation", "Delivery"), order["applicable_entity_classes"])
        self.assertEqual("CA-R-2", order["source"]["atom_id"])
        role = carrier("CA-R-3", "Atom/(.Header.Context.Role:=Requirement)", body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
            "from anechoic.model import Atom", "class Requirement(Atom):", "    pass",
            "declare_entity(entity_class=Requirement, entity_name='Requirement', qualification_property_path='Atom.Header.Context.Role')", "```"))
        projection = build_subject_projection_data([atom, claim, role])
        base = next(row for row in projection["entities"] if row["identity"] == "Atom")
        self.assertNotIn("Atom.Content.Claim", [row["identity"] for row in base["direct_properties"]])
        entity = next(row for row in projection["entities"] if row["identity"] == "Atom/(.Header.Context.Role:=Requirement)")
        projected = next(row for row in entity["inherited_properties"] if row["identity"] == "Atom.Content.Claim")
        self.assertIn(order, projected["contracts"])

    def test_native_property_uses_explicit_bearer_and_preserves_written_subject(self):
        step = "Atom/(.Header.Context.Role:=Operations)/Step"
        topic = "ANECHOIC_MODEL <+ Step.Kind"
        declarations = [
            carrier("CA-R-1", step, body()),
            carrier("CA-R-2", "Other/Step", body()),
            carrier("CA-R-3", topic, body(
                "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
                f"declare_entity(entity_name='Kind', relation_name='IS_PROPERTY_OF', base_path={step!r})",
                "```")),
        ]
        graph = compose_contract_graph(declarations)
        node, = [row for row in graph["entities"] if row["target"] == f"{step}.Kind"]
        entry, = node["own"]
        self.assertEqual(topic, entry["subject"])
        self.assertEqual("CA-R-3", entry["source"]["atom_id"])
        self.assertEqual("native_property_base_path", entry["binding"])
        self.assertFalse(any(row["target"] in {"Step.Kind", "Other/Step.Kind"} for row in graph["entities"]))

    def test_native_nested_bearers_resolve_independently_of_source_order(self):
        def property_declaration(atom_id, subject, base, name):
            return carrier(atom_id, subject, body(
                "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
                f"declare_entity(entity_name={name!r}, relation_name='IS_PROPERTY_OF', base_path={base!r})",
                "```"))

        declarations = [
            carrier("CA-R-1", "Atom", body()),
            property_declaration("CA-R-2", "Short.Header", "Atom", "Header"),
            property_declaration("CA-R-3", "Header.Context", "Atom.Header", "Context"),
            property_declaration("CA-R-4", "Context.Role", "Atom.Header.Context", "Role"),
        ]
        for rows in (declarations, list(reversed(declarations))):
            graph = compose_contract_graph(rows)
            targets = {entry["source"]["atom_id"]: node["target"]
                       for node in graph["entities"] for entry in node["own"]}
            self.assertEqual("Atom.Header.Context.Role", targets["CA-R-4"])

    def test_native_python_class_inheritance_and_relation_metadata(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_narrowing_graph

        root = carrier("CA-R-1", "Atom", body())
        method = carrier("CA-R-2", "Atom/(.Header.Context.Role := Method)", body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
            "from anechoic.model import Atom", "class Method(Atom):", "    pass",
            "declare_entity(entity_class=Method, entity_name='Method', qualification_property_path='Atom.Header.Context.Role')",
            "```"))
        tree, _ = compose_narrowing_graph([root, method])
        identities = {node["id"]: node["identity"] for node in tree["nodes"]}
        self.assertIn(("Atom/(.Header.Context.Role:=Method)", "Atom"),
                      {(identities[edge["relation_source"]], identities[edge["relation_target"]])
                       for edge in tree["edges"]})
        relation = carrier("CA-R-3", "Relation//CARRIES", body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_relation",
            "declare_relation(relation_name='CARRIES', source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)}, target_endpoint={'level': 'instances'}, inverse_alias='IS_CARRIED_BY', written_alias='>>')",
            "```"))
        clauses, diagnostics = extract_claim_constraints(relation)
        self.assertEqual([], diagnostics)
        self.assertEqual(2, sum(row["kind"] == "relation_endpoint" for row in clauses))
        self.assertTrue(any(row.get("relation") == "HAS_INVERSE" for row in clauses))
        self.assertTrue(any(row.get("glyph") == ">>" for row in clauses))

    def test_native_direct_relation_preserves_the_legacy_inverse_view(self):
        direct = carrier("CA-R-1", "Relation//CARRIES", body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_relation",
            "declare_relation(relation_name='CARRIES', source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},",
            "                 target_endpoint={'level': 'instances', 'ephemeral': False},",
            "                 inverse_alias='IS_CARRIED_BY', targets_per_source=1)", "```",
            "### Prose Claim", "The Carrier represents the object."))
        inverse = carrier("CA-R-2", "Relation//IS_CARRIED_BY", body(
            "### Formal Claim", "```python", "relation(source='Relation//IS_CARRIED_BY', name='HAS_INVERSE', target='Relation//CARRIES', reverse=True)", "```"))
        graph = compose_contract_graph([direct, inverse])
        view = next(row["derived_view"] for row in graph["relations"] if row["target"] == "IS_CARRIED_BY")
        endpoint, = view["endpoints"]
        self.assertEqual({"level": "instances", "ephemeral": False}, endpoint["host"])
        self.assertEqual(("Carrier",), endpoint["target"]["entity_paths"])
        self.assertEqual({"minimum": 1, "maximum": 1}, endpoint["sources_per_target"])
        self.assertEqual([], graph["missing_relation_semantics"])
        self.assertEqual([], graph["inheritance_diagnostics"])
        direct_row = next(row for row in graph["relations"] if row["target"] == "CARRIES")
        self.assertNotIn("derived_aliases", direct_row)

    def test_native_inverse_without_separate_declaration_keeps_source_and_bounds(self):
        direct = carrier("CA-R-1", "Relation//CARRIES", body(
            "### Formal Claim", "```python",
            "from anechoic.formal_claims import Cardinality, declare_relation",
            "declare_relation(relation_name='CARRIES',",
            "  source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},",
            "  target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},",
            "  inverse_alias='IS_CARRIED_BY',",
            "  targets_per_source=Cardinality(minimum=2, maximum=3),",
            "  sources_per_target=Cardinality(minimum=1, maximum=5))",
            "```", semantics="The Carrier represents the object."))
        graph = compose_contract_graph([direct])
        self.assertEqual(["CARRIES"], [row["target"] for row in graph["relations"]])
        direct_row = graph["relations"][0]
        alias, = direct_row["derived_aliases"]
        self.assertEqual(("IS_CARRIED_BY", "Derived", "CARRIES"),
                         (alias["name"], alias["classification"], alias["direct_relation"]))
        self.assertEqual("CA-R-1", alias["source"]["atom_id"])
        endpoint, = alias["endpoints"]
        self.assertEqual(("Atom",), endpoint["host"]["entity_paths"])
        self.assertEqual(("Carrier",), endpoint["target"]["entity_paths"])
        self.assertEqual({"minimum": 1, "maximum": 5}, endpoint["targets_per_source"])
        self.assertEqual({"minimum": 2, "maximum": 3}, endpoint["sources_per_target"])
        self.assertEqual(2, len(direct_row["host_target"]))
        self.assertIn("Derived Relation `((IS_CARRIED_BY))`", render_contract_graph(graph))
