"""Additional Model projection tests."""

from . import test_model_projection as source


class ModelProjectionCases2:
    def test_tree_includes_axes_declared_for_their_bearer(self):
        axis = [
            "ANECHOIC_MODEL <+ Node >| Review",
            {
                "kind": "entity",
                "arguments": {
                    "entity_name": "Review",
                    "allowed_axis_values": {"Review": ["Pending", "Done"]},
                },
            },
        ]
        with source._server() as client:
            source.admit(client, [source.entity("Node", "Node"), axis])
            result = source.rows(
                client,
                "SELECT tree_line, parent_path, parent_operator, allowed_values "
                "FROM model_tree WHERE allowed_values IS NOT NULL",
            )
        self.assertEqual(1, len(result))
        line, parent, operator, values = result[0]
        self.assertEqual(
            ("    Review", "Node", " >| "), (line, parent, operator)
        )
        self.assertEqual(["Pending", "Done"], source.json.loads(values))

    def assert_relation_axes(self, client):
        axes = source.rows(
            client,
            "SELECT declaring_node, property_path, entity_name, attributes FROM mrt_model_properties WHERE entity_name IN ('Functional', 'Transitive') ORDER BY entity_name",
        )
        for row, axis in zip(axes, ("Functional", "Transitive"), strict=True):
            self.assertEqual(
                ["Graph/Relation", f"Graph/Relation >| {axis}", axis],
                row[:3],
            )
            self.assertEqual(
                {axis: ["yes", "no"]},
                source.json.loads(row[3])["allowed_axis_values"],
            )

    def relation_declarations(self):
        declarations = [
            source.entity("Graph/Relation", "Relation"),
            source.entity("Graph/Axis", "Axis"),
            source.entity("Graph/Structure/Component", "Component"),
            source.entity("Graph/Other/Component", "Component"),
            source.prop(
                "Structure/Component.Tier", "Tier", "Graph/Other/Component"
            ),
            [
                "ANECHOIC_MODEL <+ Relation//IS_CHILD_OF",
                {
                    "kind": "relation",
                    "arguments": {
                        "relation_name": "IS_CHILD_OF",
                        "inverse_alias": "IS_PARENT_FOR",
                    },
                },
            ],
        ]
        for axis in ("Functional", "Transitive"):
            declarations.append(
                [
                    f"ANECHOIC_MODEL <+ Graph/Relation >| {axis}",
                    {
                        "kind": "entity",
                        "arguments": {
                            "entity_name": "Relation",
                            "allowed_axis_values": {axis: ["yes", "no"]},
                        },
                    },
                ]
            )
        self.add_container_axis(declarations)
        return declarations

    def add_container_axis(self, declarations):
        declarations.append(
            [
                "ANECHOIC_MODEL <+ Graph/Axis >| Container",
                {
                    "kind": "entity",
                    "arguments": {
                        "entity_name": "Axis",
                        "allowed_axis_values": {"Container": ["yes", "no"]},
                    },
                },
            ]
        )

    def test_relations_and_scoped_axis(self):
        declarations = self.relation_declarations()
        with source._server() as client:
            source.admit(client, declarations)
            axis_rules = source.rows(
                client,
                "SELECT node_rules FROM model_primary_entities WHERE entity_name = 'Axis'",
            )
            self.assertEqual(
                {"Container": ["yes", "no"]},
                source.json.loads(axis_rules[0][0])["allowed_axis_values"],
            )
            self.assertEqual(
                [["Graph/Relation//IS_CHILD_OF", "Graph/Relation", "//"]],
                source.rows(
                    client,
                    "SELECT entity_path, parent_path, parent_operator FROM mrt_model_entities WHERE entity_name = 'IS_CHILD_OF'",
                ),
            )
            self.assertEqual(
                [[0]],
                source.rows(
                    client,
                    "SELECT count(*) FROM mrt_model_entities WHERE entity_name = 'IS_PARENT_FOR'",
                ),
            )
            self.assertEqual(
                [
                    [
                        "Graph/Structure/Component",
                        "Graph/Structure/Component.Tier",
                    ]
                ],
                source.rows(
                    client,
                    "SELECT declaring_node, property_path FROM mrt_model_properties WHERE entity_name = 'Tier'",
                ),
            )
            self.assert_relation_axes(client)
            self.assert_applies_relation(client)

    def assert_applies_relation(self, client):
        source.admit(
            client,
            [
                source.entity("Relation", "Relation"),
                [
                    "ANECHOIC_MODEL <+ Relation//APPLIES",
                    {
                        "kind": "relation",
                        "arguments": {"relation_name": "APPLIES"},
                    },
                ],
            ],
        )
        self.assertEqual(
            [["Relation//APPLIES", "Relation"]],
            source.rows(
                client,
                "SELECT entity_path, parent_path FROM mrt_model_entities WHERE entity_name = 'APPLIES'",
            ),
        )
