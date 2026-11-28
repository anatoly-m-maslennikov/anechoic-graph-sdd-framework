import json
import unittest
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)


from .model_projection_cases_1 import ModelProjectionCases1
from .model_projection_cases_2 import ModelProjectionCases2


def entity(subject, name):
    return [
        f"ANECHOIC_MODEL <+ {subject}",
        {
            "kind": "entity",
            "arguments": {
                "entity_name": name,
                "entity_class": name.replace(" ", ""),
            },
        },
    ]


def prop(subject, name, bearer, **options):
    return [
        f"ANECHOIC_MODEL <+ {subject}",
        {
            "kind": "entity",
            "arguments": {
                "entity_kind": "Property",
                "entity_name": name,
                "base_path": bearer,
                **options,
            },
        },
    ]


def admit(
    client,
    declarations,
    node_locations=None,
    node_parts=None,
    node_alternatives=None,
    node_aliases=None,
):
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
    payload["receipt"]["model_descriptor_sha256"] = sha256(
        payload["model"].encode()
    ).hexdigest()
    response = client.put("/generation", json=payload)
    assert response.status_code == 200, response.text


def rows(client, sql):
    response = _query(client, sql)
    assert response.status_code == 200, response.text
    return response.json()["result"]["rows"]


class ModelProjectionTests(
    ModelProjectionCases1, ModelProjectionCases2, unittest.TestCase
):
    def test_tree_labels_use_indentation_and_retain_structured_details(self):
        root = entity("Node", "Node")
        subtype = entity("Node//A", "A")
        branch = entity("Node/B", "B")
        child = entity("Node//A/Child", "Child")
        axes = {"Persistence": "Artifact"}
        subtype[1]["arguments"]["axes"] = axes
        with _server() as client:
            admit(
                client,
                [root, subtype, branch, child],
                node_parts={branch[0]: [["=>A", "Node//A"]]},
            )
            rendered = rows(
                client,
                "SELECT tree_order, tree_line, axes, parent_operator, "
                "reference_path "
                "FROM model_tree ORDER BY tree_order",
            )
        self.assertEqual([1, 2, 3, 4, 5], [row[0] for row in rendered])
        self.assertEqual(
            [
                "Node",
                "    A",
                "        Child",
                "    B",
                "        A",
            ],
            [row[1] for row in rendered],
        )
        self.assertEqual(axes, json.loads(rendered[1][2]))
        self.assertEqual(
            [None, "//", "/", "/", "//"], [r[3] for r in rendered]
        )
        self.assertEqual("Node//A", rendered[-1][4])

    def primary_declarations(self):
        declarations = [
            entity("Atom", "Atom"),
            entity("Atom//Spec", "Spec"),
            entity("Atom//Spec//Axiom", "Axiom"),
            prop(
                "Atom.Header.Context.Template",
                "Template",
                "Atom.Header.Context",
                value_cardinality=1,
                field_options={"default": "example"},
            ),
            prop(
                "Atom//Spec//Axiom.Header.Context.Template",
                "Template",
                "Atom.Header.Context",
                applies_to_entity_classes=["Atom//Spec//Axiom"],
                allowed_values=["axiom"],
                field_options={"default": "axiom"},
            ),
        ]
        for declaration, base in zip(
            declarations[1:3], ("Atom", "Spec"), strict=True
        ):
            declaration[1]["classes"] = [
                {
                    "name": declaration[1]["arguments"]["entity_class"],
                    "bases": [base],
                }
            ]
        return declarations

    def test_primary_projections_from_the_accepted_generation(self):
        declarations = self.primary_declarations()
        with TemporaryDirectory(
            prefix="ane-model-projection-", dir="/tmp"
        ) as directory:
            database = Path(directory).resolve() / "model.duckdb"
            with _server(database) as client:
                admit(
                    client,
                    declarations,
                    {
                        declarations[2][0]: (
                            "Atom//Spec",
                            "//",
                            "(Header.Context.Template := axiom)",
                        )
                    },
                )
            with duckdb.connect(str(database)) as connection:
                connection.execute("DROP TABLE mrt_model_tree")
                connection.execute("DROP TABLE mrt_model_primary_entities")
            with _server(database) as client:
                self.assert_primary_projection(client)

    def assert_primary_projection(self, client):
        self.assertEqual(
            [
                [
                    "Atom//Spec//(Header.Context.Template := axiom)",
                    "Atom//Spec",
                    "//",
                ]
            ],
            rows(
                client,
                (
                    "SELECT concern_path, parent_path, parent_operator FROM "
                    "model_tree WHERE entity_name = 'Axiom'"
                ),
            ),
        )
        properties = {
            name: json.loads(fields)
            for name, fields in rows(
                client,
                "SELECT entity_name, properties FROM model_primary_entities",
            )
        }
        self.assertEqual("axiom", properties["Axiom"][0]["fixed_value"])
        self.assertFalse(properties["Axiom"][0]["inherited"])
        self.assertEqual("example", properties["Spec"][0]["default_value"])
        self.assertTrue(properties["Spec"][0]["inherited"])
        self.assertNotIn("fixed_value", properties["Spec"][0])
        admit(client, [])
        for table in ("mrt_model_tree", "mrt_model_primary_entities"):
            self.assertEqual(
                [[0]], rows(client, f"SELECT count(*) FROM {table}")
            )

    def test_hierarchy_refinements_and_replacement(self):
        declarations = [
            entity("Node", "Node"),
            entity("Node//Artifact", "Artifact"),
            entity("Node//Artifact//Atom", "Atom"),
            entity("Atom/Spec", "Spec"),
            prop("Node//Artifact//Atom.ID", "ID", "Node//Artifact//Atom"),
            prop(
                "Atom/Spec.ID",
                "ID",
                "Node//Artifact//Atom",
                applies_to_entity_classes=["Atom/Spec"],
                allowed_values=["A"],
            ),
        ]
        with _server() as client:
            admit(client, declarations)
            self.assertEqual(
                [["Node//Artifact//Atom", "/"]],
                rows(
                    client,
                    (
                        "SELECT parent_path, parent_operator FROM "
                        "mrt_model_entities WHERE entity_name = 'Spec'"
                    ),
                ),
            )
            properties = rows(
                client,
                (
                    "SELECT declaring_node, property_path, refinements, "
                    "attributes FROM mrt_model_properties ORDER BY subject"
                ),
            )
            self.assertEqual(2, len(properties))
            refined = next(row for row in properties if json.loads(row[2]))
            self.assertEqual(["Atom/Spec", "Atom/Spec.ID"], refined[:2])
            self.assertEqual(["Atom/Spec"], json.loads(refined[2]))
            self.assertEqual(["A"], json.loads(refined[3])["allowed_values"])
            admit(client, [])
            self.assertEqual(
                [[0]], rows(client, "SELECT count(*) FROM mrt_model_entities")
            )

    def test_diagnostics_do_not_change_projection(self):
        diagnostic = {
            "attempt_id": "try-2",
            "accepted_generation": "untrusted",
            "severity": "error",
            "code": "invalid",
            "message": "broken",
            "atom_ref": "AN-S-1@1",
            "source_path": "x.md",
            "subject": None,
        }
        with _server() as client:
            admit(client, [entity("Node", "Node")])
            payload = {
                **BINDING,
                "source": "build",
                "issues": [],
                "model_diagnostics": [diagnostic],
            }
            self.assertEqual(
                200, client.put("/ingestion/issues", json=payload).status_code
            )
            self.assertEqual(
                [["try-2", "b" * 64, "AN-S-1@1", "x.md"]],
                rows(
                    client,
                    (
                        "SELECT attempt_id, accepted_generation, atom_ref, "
                        "source_path FROM mrt_diag_model_manifests"
                    ),
                ),
            )
            self.assertEqual(
                [["Node"]],
                rows(client, "SELECT entity_name FROM mrt_model_entities"),
            )
            payload["model_diagnostics"] = []
            self.assertEqual(
                200, client.put("/ingestion/issues", json=payload).status_code
            )
            self.assertEqual(
                [[0]],
                rows(client, "SELECT count(*) FROM mrt_diag_model_manifests"),
            )
