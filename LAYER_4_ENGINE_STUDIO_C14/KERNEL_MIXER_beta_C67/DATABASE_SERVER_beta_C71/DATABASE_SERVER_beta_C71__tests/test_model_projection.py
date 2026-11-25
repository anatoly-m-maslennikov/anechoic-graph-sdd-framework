import json
import unittest
from hashlib import sha256

from .DATABASE_SERVER_beta_C71__tests__shared import BINDING, _generation, _query, _server


def entity(subject, name):
    return [f"ANECHOIC_MODEL <+ {subject}", {"kind": "entity", "arguments": {
        "entity_name": name, "entity_class": name.replace(" ", "")}}]


def prop(subject, name, bearer, **options):
    return [f"ANECHOIC_MODEL <+ {subject}", {"kind": "entity", "arguments": {
        "entity_kind": "Property", "entity_name": name, "base_path": bearer, **options}}]


def admit(client, declarations):
    payload = _generation()
    model = json.loads(payload["model"])
    model["bindings"]["declarations"] = declarations
    payload["model"] = json.dumps(model)
    payload["receipt"]["model_descriptor_sha256"] = sha256(payload["model"].encode()).hexdigest()
    response = client.put("/generation", json=payload)
    assert response.status_code == 200, response.text


def rows(client, sql):
    response = _query(client, sql)
    assert response.status_code == 200, response.text
    return response.json()["result"]["rows"]


class ModelProjectionTests(unittest.TestCase):
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

    def test_relations_and_scoped_classification(self):
        declarations = [entity("Graph/Relation", "Relation"), entity("Graph/Structure/Component", "Component"),
                        entity("Graph/Other/Component", "Component"),
                        prop("Structure/Component.Tier", "Tier", "Graph/Other/Component"),
                        ["ANECHOIC_MODEL <+ Relation//IS_CHILD_OF", {"kind": "relation", "arguments": {
                            "relation_name": "IS_CHILD_OF", "inverse_alias": "IS_PARENT_FOR"}}]]
        for axis in ("Functional", "Transitive"):
            declarations.append([f"ANECHOIC_MODEL <+ Graph/Relation >| {axis}",
                {"kind": "entity", "arguments": {"entity_name": "Relation",
                 "allowed_classification_values": {axis: ["yes", "no"]}}}])
        with _server() as client:
            admit(client, declarations)
            self.assertEqual([["Graph/Relation//IS_CHILD_OF", "Graph/Relation", "//"]], rows(client,
                "SELECT entity_path, parent_path, parent_operator FROM mrt_model_entities WHERE entity_name = 'IS_CHILD_OF'"))
            self.assertEqual([[0]], rows(client, "SELECT count(*) FROM mrt_model_entities WHERE entity_name = 'IS_PARENT_FOR'"))
            self.assertEqual([["Graph/Structure/Component", "Graph/Structure/Component.Tier"]], rows(client,
                "SELECT declaring_node, property_path FROM mrt_model_properties WHERE entity_name = 'Tier'"))
            axes = rows(client, "SELECT declaring_node, property_path, entity_name, attributes FROM mrt_model_properties WHERE entity_name IN ('Functional', 'Transitive') ORDER BY entity_name")
            for row, axis in zip(axes, ("Functional", "Transitive"), strict=True):
                self.assertEqual(["Graph/Relation", f"Graph/Relation >| {axis}", axis], row[:3])
                self.assertEqual({axis: ["yes", "no"]}, json.loads(row[3])["allowed_classification_values"])
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
