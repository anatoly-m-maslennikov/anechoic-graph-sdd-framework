"""Additional Model projection tests."""

from . import test_model_projection as source


class ModelProjectionCases1:
    def metadata_declarations(self):
        declarations = [
            source.entity("Node", "Node"),
            source.entity("Node//Example", "Example"),
        ]
        arguments = declarations[1][1]["arguments"]
        arguments.update(
            axes={"Form": "Example"},
            ssot_carrier_path="Carrier//Text",
            model_relation_constraints={"LINKS": {"targets_per_source": 0}},
            instance_relation_constraints={
                "CONTAINS": {"targets_per_source": 1}
            },
        )
        expected_rules = {
            key: arguments[key]
            for key in (
                "ssot_carrier_path",
                "model_relation_constraints",
                "instance_relation_constraints",
            )
        }
        return declarations, expected_rules

    def test_declared_node_metadata_and_upgrade(self):
        declarations, expected_rules = self.metadata_declarations()
        with source.TemporaryDirectory(
            prefix="ane-model-upgrade-", dir="/tmp"
        ) as directory:
            database = source.Path(directory).resolve() / "model.duckdb"
            with source._server(database) as client:
                source.admit(client, declarations)
                metadata = self.assert_metadata(client, expected_rules)
            with source.duckdb.connect(str(database)) as connection:
                connection.execute("DROP VIEW model_primary_entities")
                connection.execute(
                    "ALTER TABLE mrt_model_primary_entities RENAME COLUMN axes TO classifications"
                )
                connection.execute(
                    "ALTER TABLE mrt_model_primary_entities DROP COLUMN node_rules"
                )
                connection.execute(
                    "CREATE VIEW model_primary_entities AS SELECT * FROM mrt_model_primary_entities"
                )
            with source._server(database) as client:
                upgraded = source.rows(
                    client,
                    "SELECT entity_name, axes, node_rules FROM model_primary_entities ORDER BY entity_name",
                )
                self.assertEqual(metadata, upgraded)
                self.assertEqual(
                    [[row[1], row[1]] for row in metadata],
                    source.rows(
                        client,
                        "SELECT axes, classifications FROM model_primary_entities ORDER BY entity_name",
                    ),
                )
                self.assert_metadata_schema(client)

    def assert_metadata_schema(self, client):
        schema = client.get("/schema", params=source.BINDING).json()["result"][
            "tables"
        ]
        public = {
            column["name"] for column in schema["model_primary_entities"]
        }
        canonical = {
            column["name"] for column in schema["mrt_model_primary_entities"]
        }
        self.assertTrue({"axes", "classifications"} <= public)
        self.assertIn("axes", canonical)
        self.assertNotIn("classifications", canonical)

    def assert_metadata(self, client, expected_rules):
        metadata = source.rows(
            client,
            "SELECT entity_name, axes, node_rules FROM model_primary_entities ORDER BY entity_name",
        )
        self.assertEqual(
            ["Example", {"Form": "Example"}, expected_rules],
            [
                metadata[0][0],
                source.json.loads(metadata[0][1]),
                source.json.loads(metadata[0][2]),
            ],
        )
        self.assertEqual(
            ["Node", {}, {}],
            [
                metadata[1][0],
                source.json.loads(metadata[1][1]),
                source.json.loads(metadata[1][2]),
            ],
        )
        self.assertEqual(
            [[row[1], row[1]] for row in metadata],
            source.rows(
                client,
                "SELECT axes, classifications FROM model_primary_entities ORDER BY entity_name",
            ),
        )
        return metadata

    def test_authored_parts_and_link_upgrade(self):
        declarations = [
            source.entity("Node", "Node"),
            source.entity("Node//Owner", "Owner"),
            source.entity("Node//Target", "Target"),
            source.entity("Node//Owner//Child", "Child"),
        ]
        owner = declarations[1][0]
        parts = {
            owner: [["Child", "Node//Owner//Child"], ["=>IO", "Node//Target"]]
        }
        alternatives = {owner: [["Child", "=>IO"]]}
        with source.TemporaryDirectory(
            prefix="ane-model-parts-", dir="/tmp"
        ) as directory:
            database = source.Path(directory).resolve() / "model.duckdb"
            with source._server(database) as client:
                expected = self.assert_authored_parts(
                    client, declarations, parts, alternatives, owner
                )
            with source.duckdb.connect(str(database)) as connection:
                connection.execute(
                    "ALTER TABLE mrt_model_tree DROP COLUMN reference_path"
                )
            with source._server(database) as client:
                self.assertEqual(
                    expected,
                    source.rows(
                        client,
                        "SELECT entity_path, concern_path, parent_path, parent_operator, reference_path FROM model_tree ORDER BY entity_path",
                    ),
                )

    def assert_authored_parts(
        self, client, declarations, parts, alternatives, owner
    ):
        source.admit(
            client,
            declarations,
            node_parts=parts,
            node_alternatives=alternatives,
            node_aliases={declarations[2][0]: ["PORT"]},
        )
        expected = source.rows(
            client,
            "SELECT entity_path, concern_path, parent_path, parent_operator, reference_path FROM model_tree ORDER BY entity_path",
        )
        self.assertIn(
            [
                "Node//Owner//=>IO",
                "Node//Owner//=>IO",
                "Node//Owner",
                "//",
                "Node//Target",
            ],
            expected,
        )
        self.assertEqual(5, len(expected))
        self.assertEqual(
            [[4]],
            source.rows(client, "SELECT count(*) FROM model_primary_entities"),
        )
        self.assert_part_rules(client, parts, alternatives, owner)
        return expected

    def assert_part_rules(self, client, parts, alternatives, owner):
        rules = source.json.loads(
            source.rows(
                client,
                "SELECT node_rules FROM model_primary_entities WHERE entity_name = 'Owner'",
            )[0][0]
        )
        self.assertEqual(
            {
                "node_parts": parts[owner],
                "node_alternatives": alternatives[owner],
            },
            rules,
        )
        target_rules = source.json.loads(
            source.rows(
                client,
                "SELECT node_rules FROM model_primary_entities WHERE entity_name = 'Target'",
            )[0][0]
        )
        self.assertEqual({"node_aliases": ["PORT"]}, target_rules)
