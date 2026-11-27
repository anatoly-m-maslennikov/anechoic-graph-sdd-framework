import json
import unittest
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _generation, _query, _server


def entity(subject, name):
    return [f"ANECHOIC_MODEL <+ {subject}", {"kind": "entity", "arguments": {
        "entity_name": name, "entity_class": name.replace(" ", "")}}]


def prop(subject, name, bearer, **options):
    return [f"ANECHOIC_MODEL <+ {subject}", {"kind": "entity", "arguments": {
        "entity_kind": "Property", "entity_name": name, "base_path": bearer, **options}}]


def admit(client, declarations, node_locations=None, node_parts=None, node_alternatives=None, node_aliases=None):
    payload = _generation()
    model = json.loads(payload["model"])
    model["bindings"]["declarations"] = declarations
    if node_locations:
        model["node_locations"] = node_locations
    if node_parts is not None:
        model["node_parts"] = node_parts
    if node_alternatives is not None:
        model["node_alternatives"] = node_alternatives
    if node_aliases is not None:
        model["node_aliases"] = node_aliases
    payload["model"] = json.dumps(model)
    payload["receipt"]["model_descriptor_sha256"] = sha256(payload["model"].encode()).hexdigest()
    response = client.put("/generation", json=payload)
    assert response.status_code == 200, response.text


def rows(client, sql):
    response = _query(client, sql)
    assert response.status_code == 200, response.text
    return response.json()["result"]["rows"]


class ModelProjectionTests(unittest.TestCase):
    def test_primary_projections_from_the_accepted_generation(self):
        declarations = [entity("Atom", "Atom"), entity("Atom//Spec", "Spec"),
                        entity("Atom//Spec//Axiom", "Axiom"),
                        prop("Atom.Header.Context.Template", "Template", "Atom.Header.Context",
                             value_cardinality=1, field_options={"default": "example"}),
                        prop("Atom//Spec//Axiom.Header.Context.Template", "Template", "Atom.Header.Context",
                             applies_to_entity_classes=["Atom//Spec//Axiom"], allowed_values=["axiom"],
                             field_options={"default": "axiom"})]
        for declaration, base in zip(declarations[1:3], ("Atom", "Spec"), strict=True):
            declaration[1]["classes"] = [{"name": declaration[1]["arguments"]["entity_class"], "bases": [base]}]
        with TemporaryDirectory(prefix="ane-model-projection-", dir="/tmp") as directory:
            database = Path(directory).resolve() / "model.duckdb"
            with _server(database) as client:
                admit(client, declarations, {declarations[2][0]:
                    ("Atom//Spec", "//", "(Header.Context.Template := axiom)")})
            with duckdb.connect(str(database)) as connection:
                connection.execute("DROP TABLE mrt_model_tree")
                connection.execute("DROP TABLE mrt_model_primary_entities")
            with _server(database) as client:
                self.assertEqual([["Atom//Spec//(Header.Context.Template := axiom)", "Atom//Spec", "//"]],
                    rows(client, "SELECT concern_path, parent_path, parent_operator FROM model_tree WHERE entity_name = 'Axiom'"))
                properties = {name: json.loads(fields) for name, fields in
                              rows(client, "SELECT entity_name, properties FROM model_primary_entities")}
                self.assertEqual("axiom", properties["Axiom"][0]["fixed_value"])
                self.assertFalse(properties["Axiom"][0]["inherited"])
                self.assertEqual("example", properties["Spec"][0]["default_value"])
                self.assertTrue(properties["Spec"][0]["inherited"])
                self.assertNotIn("fixed_value", properties["Spec"][0])
                admit(client, [])
                for table in ("mrt_model_tree", "mrt_model_primary_entities"):
                    self.assertEqual([[0]], rows(client, f"SELECT count(*) FROM {table}"))

    def test_declared_node_metadata_and_upgrade(self):
        declarations = [entity("Node", "Node"), entity("Node//Example", "Example")]
        arguments = declarations[1][1]["arguments"]
        arguments.update(axes={"Form": "Example"}, ssot_carrier_path="Carrier//Text",
                         model_relation_constraints={"LINKS": {"targets_per_source": 0}},
                         instance_relation_constraints={"CONTAINS": {"targets_per_source": 1}})
        expected_rules = {key: arguments[key] for key in (
            "ssot_carrier_path", "model_relation_constraints", "instance_relation_constraints")}
        with TemporaryDirectory(prefix="ane-model-upgrade-", dir="/tmp") as directory:
            database = Path(directory).resolve() / "model.duckdb"
            with _server(database) as client:
                admit(client, declarations)
                metadata = rows(client, "SELECT entity_name, axes, node_rules FROM model_primary_entities ORDER BY entity_name")
                self.assertEqual(["Example", {"Form": "Example"}, expected_rules],
                                 [metadata[0][0], json.loads(metadata[0][1]), json.loads(metadata[0][2])])
                self.assertEqual(["Node", {}, {}],
                                 [metadata[1][0], json.loads(metadata[1][1]), json.loads(metadata[1][2])])
                self.assertEqual([[row[1], row[1]] for row in metadata], rows(
                    client, "SELECT axes, classifications FROM model_primary_entities ORDER BY entity_name"))
            with duckdb.connect(str(database)) as connection:
                connection.execute("DROP VIEW model_primary_entities")
                connection.execute("ALTER TABLE mrt_model_primary_entities RENAME COLUMN axes TO classifications")
                connection.execute("ALTER TABLE mrt_model_primary_entities DROP COLUMN node_rules")
                connection.execute("CREATE VIEW model_primary_entities AS SELECT * FROM mrt_model_primary_entities")
            with _server(database) as client:
                upgraded = rows(client, "SELECT entity_name, axes, node_rules FROM model_primary_entities ORDER BY entity_name")
                self.assertEqual(metadata, upgraded)
                self.assertEqual([[row[1], row[1]] for row in metadata], rows(
                    client, "SELECT axes, classifications FROM model_primary_entities ORDER BY entity_name"))
                schema = client.get('/schema', params=BINDING).json()['result']['tables']
                public = {column['name'] for column in schema['model_primary_entities']}
                canonical = {column['name'] for column in schema['mrt_model_primary_entities']}
                self.assertTrue({'axes', 'classifications'} <= public)
                self.assertIn('axes', canonical)
                self.assertNotIn('classifications', canonical)

    def test_authored_parts_and_link_upgrade(self):
        declarations = [entity("Node", "Node"), entity("Node//Owner", "Owner"),
                        entity("Node//Target", "Target"), entity("Node//Owner//Child", "Child")]
        owner = declarations[1][0]
        parts = {owner: [["Child", "Node//Owner//Child"], ["=>IO", "Node//Target"]]}
        alternatives = {owner: [["Child", "=>IO"]]}
        with TemporaryDirectory(prefix="ane-model-parts-", dir="/tmp") as directory:
            database = Path(directory).resolve() / "model.duckdb"
            with _server(database) as client:
                admit(client, declarations, node_parts=parts, node_alternatives=alternatives,
                      node_aliases={declarations[2][0]: ["PORT"]})
                expected = rows(client, "SELECT entity_path, concern_path, parent_path, parent_operator, reference_path FROM model_tree ORDER BY entity_path")
                self.assertIn(["Node//Owner//=>IO", "Node//Owner//=>IO", "Node//Owner", "//", "Node//Target"], expected)
                self.assertEqual(5, len(expected))
                self.assertEqual([[4]], rows(client, "SELECT count(*) FROM model_primary_entities"))
                rules = json.loads(rows(client, "SELECT node_rules FROM model_primary_entities WHERE entity_name = 'Owner'")[0][0])
                self.assertEqual({"node_parts": parts[owner], "node_alternatives": alternatives[owner]}, rules)
                target_rules = json.loads(rows(client, "SELECT node_rules FROM model_primary_entities WHERE entity_name = 'Target'")[0][0])
                self.assertEqual({"node_aliases": ["PORT"]}, target_rules)
            with duckdb.connect(str(database)) as connection:
                connection.execute("ALTER TABLE mrt_model_tree DROP COLUMN reference_path")
            with _server(database) as client:
                self.assertEqual(expected, rows(client, "SELECT entity_path, concern_path, parent_path, parent_operator, reference_path FROM model_tree ORDER BY entity_path"))

    def test_hierarchy_refinements_and_replacement(self):
        declarations = [entity("Node", "Node"), entity("Node//Artifact", "Artifact"),
                        entity("Node//Artifact//Atom", "Atom"), entity("Atom/Spec", "Spec"),
                        prop("Node//Artifact//Atom.ID", "ID", "Node//Artifact//Atom"),
                        prop("Atom/Spec.ID", "ID", "Node//Artifact//Atom",
                             applies_to_entity_classes=["Atom/Spec"], allowed_values=["A"])]
        with _server() as client:
            admit(client, declarations)
            self.assertEqual([["Node//Artifact//Atom", "/"]], rows(client,
                "SELECT parent_path, parent_operator FROM mrt_model_entities WHERE entity_name = 'Spec'"))
            properties = rows(client, "SELECT declaring_node, property_path, refinements, attributes FROM mrt_model_properties ORDER BY subject")
            self.assertEqual(2, len(properties))
            refined = next(row for row in properties if json.loads(row[2]))
            self.assertEqual(["Atom/Spec", "Atom/Spec.ID"], refined[:2])
            self.assertEqual(["Atom/Spec"], json.loads(refined[2]))
            self.assertEqual(["A"], json.loads(refined[3])["allowed_values"])
            admit(client, [])
            self.assertEqual([[0]], rows(client, "SELECT count(*) FROM mrt_model_entities"))

    def test_relations_and_scoped_axis(self):
        declarations = [entity("Graph/Relation", "Relation"), entity("Graph/Axis", "Axis"),
                        entity("Graph/Structure/Component", "Component"),
                        entity("Graph/Other/Component", "Component"),
                        prop("Structure/Component.Tier", "Tier", "Graph/Other/Component"),
                        ["ANECHOIC_MODEL <+ Relation//IS_CHILD_OF", {"kind": "relation", "arguments": {
                            "relation_name": "IS_CHILD_OF", "inverse_alias": "IS_PARENT_FOR"}}]]
        for axis in ("Functional", "Transitive"):
            declarations.append([f"ANECHOIC_MODEL <+ Graph/Relation >| {axis}",
                {"kind": "entity", "arguments": {"entity_name": "Relation",
                 "allowed_axis_values": {axis: ["yes", "no"]}}}])
        declarations.append(["ANECHOIC_MODEL <+ Graph/Axis >| Container",
            {"kind": "entity", "arguments": {"entity_name": "Axis",
             "allowed_axis_values": {"Container": ["yes", "no"]}}}])
        with _server() as client:
            admit(client, declarations)
            axis_rules = rows(client, "SELECT node_rules FROM model_primary_entities WHERE entity_name = 'Axis'")
            self.assertEqual({"Container": ["yes", "no"]}, json.loads(axis_rules[0][0])["allowed_axis_values"])
            self.assertEqual([["Graph/Relation//IS_CHILD_OF", "Graph/Relation", "//"]], rows(client,
                "SELECT entity_path, parent_path, parent_operator FROM mrt_model_entities WHERE entity_name = 'IS_CHILD_OF'"))
            self.assertEqual([[0]], rows(client, "SELECT count(*) FROM mrt_model_entities WHERE entity_name = 'IS_PARENT_FOR'"))
            self.assertEqual([["Graph/Structure/Component", "Graph/Structure/Component.Tier"]], rows(client,
                "SELECT declaring_node, property_path FROM mrt_model_properties WHERE entity_name = 'Tier'"))
            axes = rows(client, "SELECT declaring_node, property_path, entity_name, attributes FROM mrt_model_properties WHERE entity_name IN ('Functional', 'Transitive') ORDER BY entity_name")
            for row, axis in zip(axes, ("Functional", "Transitive"), strict=True):
                self.assertEqual(["Graph/Relation", f"Graph/Relation >| {axis}", axis], row[:3])
                self.assertEqual({axis: ["yes", "no"]}, json.loads(row[3])["allowed_axis_values"])
            admit(client, [entity("Relation", "Relation"), ["ANECHOIC_MODEL <+ Relation//APPLIES",
                {"kind": "relation", "arguments": {"relation_name": "APPLIES"}}]])
            self.assertEqual([["Relation//APPLIES", "Relation"]], rows(client,
                "SELECT entity_path, parent_path FROM mrt_model_entities WHERE entity_name = 'APPLIES'"))

    def test_diagnostics_do_not_change_projection(self):
        diagnostic = {"attempt_id": "try-2", "accepted_generation": "untrusted", "severity": "error",
                      "code": "invalid", "message": "broken", "atom_ref": "AN-S-1@1", "source_path": "x.md", "subject": None}
        with _server() as client:
            admit(client, [entity("Node", "Node")])
            payload = {**BINDING, "source": "build", "issues": [], "model_diagnostics": [diagnostic]}
            self.assertEqual(200, client.put("/ingestion/issues", json=payload).status_code)
            self.assertEqual([["try-2", "b" * 64, "AN-S-1@1", "x.md"]], rows(client,
                "SELECT attempt_id, accepted_generation, atom_ref, source_path FROM mrt_diag_model_manifests"))
            self.assertEqual([["Node"]], rows(client, "SELECT entity_name FROM mrt_model_entities"))
            payload["model_diagnostics"] = []
            self.assertEqual(200, client.put("/ingestion/issues", json=payload).status_code)
            self.assertEqual([[0]], rows(client, "SELECT count(*) FROM mrt_diag_model_manifests"))
