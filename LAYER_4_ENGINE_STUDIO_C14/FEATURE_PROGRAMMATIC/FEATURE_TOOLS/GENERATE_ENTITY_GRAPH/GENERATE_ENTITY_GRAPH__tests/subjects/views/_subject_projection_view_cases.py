"""Subject projection value-format cases."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    GENERATE_ENTITY_GRAPH__shared import (
        build_subject_projection_data, subject_projection_views as views,
    )  # fmt: skip

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.subjects.views._subject_projection_view_fixtures import (
    carrier,
    claim,
    native_property,
)


class SubjectProjectionViewCases:
    def test_authority_mode_children_inherit_native_value_format(self):
        prefix = "Project.Settings.Authority Modes"
        children = (
            "Default Scope Unit Authority Mode",
            "Project Authority Mode",
        )
        data = self._authority_fixture(prefix, children)
        properties = next(
            row for row in data["entities"] if row["identity"] == "Project"
        )["direct_properties"]
        for name in children:
            prop = next(
                row
                for row in properties
                if row["identity"] == f"{prefix}.{name}"
            )
            self.assertEqual("string", prop["effective_value_format"])
            self.assertEqual(
                {"CA-R-2632"},
                {
                    source["atom_id"]
                    for source in prop["effective_value_format_sources"]
                },
            )
        self.assertFalse(
            any(
                row.get("code") == "conflicting_property_value_formats"
                for row in data["diagnostics"]
            )
        )
        document = views.render_primary_projection(data, 4)
        self.assertIn("dependent_property_value_format=str", document)

    def _authority_fixture(self, prefix, children):
        python_claim = claim(
            "```python",
            "from anechoic.formal_claims import declare_entity",
            "declare_entity(entity_name='Auth"
            "ority Modes', relation_name='IS_"
            "PROPERTY_OF',",
            "    base_path='Project.Settings'"
            ", dependent_property_cardinality"
            "=2,",
            "    allowed_dependent_property_n"
            "ames=('Default Scope Unit Author"
            "ity Mode', 'Project Authority Mo"
            "de'),",
            "    dependent_property_value_format=str)",
            "```",
        )
        rows = [
            carrier("CA-R-1", "Project", claim("Project.")),
            carrier("CA-R-2632", prefix, python_claim),
        ]
        rows.extend(
            carrier(
                f"CA-R-{index}",
                f"{prefix}.{name}",
                native_property(name, prefix, "value_cardinality=1"),
            )
            for index, name in enumerate(children, 2633)
        )
        return build_subject_projection_data(rows)

    def test_unrelated_native_str_keeps_its_format(self):
        data = build_subject_projection_data(
            [
                carrier("CA-R-1", "Node", claim("Node.")),
                carrier(
                    "CA-R-2",
                    "Node.Name",
                    claim(
                        "```python",
                        "from anechoic.formal_claims import declare_entity",
                        "declare_entity(entity_name='Name"
                        "', relation_name='IS_PROPERTY_OF"
                        "',",
                        "    base_path='Node', value_form"
                        "at=str, value_cardinality=1)",
                        "```",
                    ),
                ),
            ]
        )
        props = next(
            row for row in data["entities"] if row["identity"] == "Node"
        )["direct_properties"]
        self.assertEqual(
            "str",
            next(row for row in props if row["identity"] == "Node.Name")[
                "effective_value_format"
            ],
        )

    def test_qualified_leaf_and_empty_structural_domain_keep_inherited_format(
        self,
    ):
        data = self._qualified_fixture()
        properties = next(
            row for row in data["entities"] if row["identity"] == "Node"
        )["direct_properties"]
        group = next(
            row
            for row in properties
            if row["identity"] == "Node.Section.Group"
        )
        summary = next(
            row
            for row in properties
            if row["identity"] == "Node.Section.Group.Summary"
        )
        self.assertEqual("markdown", group["effective_value_format"])
        self.assertEqual("markdown", summary["effective_value_format"])
        self.assertEqual(
            "Node/(.Header.Role in RMED).Section.Group.Summary",
            summary["contracts"][0]["property_selector"],
        )
        self.assertEqual(
            {"minimum": 0, "maximum": 1},
            summary["contracts"][0]["value_cardinality"],
        )
        self.assertFalse(
            any(
                row.get("code") == "conflicting_property_value_formats"
                for row in data["diagnostics"]
            )
        )

    def _qualified_fixture(self):
        return build_subject_projection_data(
            [
                carrier("CA-R-1", "Node", claim("Node.")),
                carrier(
                    "CA-R-2",
                    "Node.Section",
                    native_property(
                        "Section",
                        "Node",
                        "recursive_dependent_property_car"
                        "dinality=Cardinality(minimum=0, "
                        "maximum=None)",
                        "recursive_dependent_property_value_format='markdown'",
                    ),
                ),
                carrier(
                    "CA-R-3",
                    "Node.Section.Group",
                    native_property(
                        "Group",
                        "Node.Section",
                        "property_occurrence_cardinality=1",
                        "value_cardinality=0",
                    ),
                ),
                carrier(
                    "CA-R-4",
                    "Node.Section.Group.Summary",
                    claim(
                        "```python",
                        "property_rule(address='Node/(.He"
                        "ader.Role in RMED).Section.Group"
                        ".Summary', value_format=None, va"
                        "lues='0..1')",
                        "```",
                    ),
                ),
            ]
        )

    def test_recursive_format_inheritance_keeps_local_count_and_source(self):
        rows = self._recursive_fixture()
        data = build_subject_projection_data(rows)
        properties = next(
            row for row in data["entities"] if row["identity"] == "Node"
        )["direct_properties"]
        summary = next(
            row
            for row in properties
            if row["identity"] == "Node.Section.Summary"
        )
        self.assertEqual(
            {"minimum": 0, "maximum": 1},
            summary["contracts"][0]["value_cardinality"],
        )
        self.assertIsNone(summary["contracts"][0]["value_format"])
        self.assertEqual(
            ["CA-R-2"],
            [
                row["atom_id"]
                for row in summary["effective_value_format_sources"]
            ],
        )
        document = views.render_primary_projection(data, 3)
        self.assertEqual(
            2, document.count("effective value format: `markdown` — CA-R-2@1")
        )
        self.assertIn("value cardinality: `0..1`", document)
        self.assertNotIn("integer", document)
        self.assertFalse(
            any(
                row.get("code") == "conflicting_property_value_formats"
                for row in data["diagnostics"]
            )
        )

    def _recursive_fixture(self):
        return [
            carrier("CA-R-1", "Node", claim("Node.")),
            carrier(
                "CA-R-2",
                "Node.Section",
                native_property(
                    "Section",
                    "Node",
                    "recursive_dependent_property_car"
                    "dinality=Cardinality(minimum=0, "
                    "maximum=None)",
                    "recursive_dependent_property_value_format='markdown'",
                ),
            ),
            carrier(
                "CA-R-3",
                "Node.Section.Summary",
                native_property(
                    "Summary",
                    "Node.Section",
                    "value_cardinality=Cardinality(minimum=0, maximum=1)",
                ),
            ),
        ] + self._recursive_fixture_tail()

    def _recursive_fixture_tail(self):
        return [
            carrier(
                "CA-R-4",
                "Node.Section.Nested.Detail",
                native_property(
                    "Detail",
                    "Node.Section.Nested",
                    "value_cardinality=Cardinality(minimum=0, maximum=1)",
                ),
            ),
            carrier(
                "CA-M-5",
                "Node.Section",
                native_property(
                    "Section",
                    "Node",
                    "recursive_dependent_property_car"
                    "dinality=Cardinality(minimum=0, "
                    "maximum=None)",
                    "recursive_dependent_property_value_format='int'",
                ),
                role="Method",
                form="Policy",
            ),
        ]
