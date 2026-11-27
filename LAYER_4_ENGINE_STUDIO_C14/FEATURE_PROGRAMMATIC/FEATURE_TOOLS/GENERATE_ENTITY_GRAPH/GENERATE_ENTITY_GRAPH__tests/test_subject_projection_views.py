"""Focused checks for the first four source-bound primary views."""

from pathlib import Path
import sys
import unittest


TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import build_subject_projection_data  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import subject_projection_views as views  # noqa: E402


def carrier(atom_id, subject, body, *, role="Requirement", form="Declaration"):
    return {
        "source": {"atom_id": atom_id, "version": 1, "path": f"sources/{atom_id}.md"},
        "subjects": {"active": subject, "passive": []},
        "body": body,
        "read_view": {"content_role": role, "type": form},
    }


def claim(*lines):
    return "## Claim\n\n" + "\n".join(lines) + "\n"


def native_property(name, base, *arguments):
    return claim("```python", "from anechoic.formal_claims import Cardinality, declare_entity",
                 f"declare_entity(entity_name={name!r}, relation_name='IS_PROPERTY_OF', base_path={base!r},",
                 *(f"    {argument}," for argument in arguments), ")", "```")


def carriers():
    return [
        carrier(
            "CA-R-NODE", "Node",
            claim("```python", "from anechoic.formal_claims import declare_entity, Cardinality", "declare_entity(entity_name='Status', relation_name='IS_PROPERTY_OF', base_path='Node', property_occurrence_cardinality=1, value_format='string', value_cardinality=Cardinality(minimum=1, maximum=None))", "```"),
        ),
        carrier("CA-R-CHILD", "Node/Child", claim("Child declaration.")),
        carrier(
            "CA-R-STATUS", "Node.Status",
            claim("```python", "from anechoic.formal_claims import declare_entity, Cardinality", "declare_entity(entity_name='Status', relation_name='IS_PROPERTY_OF', base_path='Node', property_occurrence_cardinality=1, value_format='string', value_cardinality=Cardinality(minimum=1, maximum=None))", "```"),
        ),
        carrier(
            "CA-R-CHILD-STATUS", "Node/Child.Status",
            claim("```python", "from anechoic.formal_claims import declare_entity, Cardinality", "declare_entity(entity_name='Status', relation_name='IS_PROPERTY_OF', base_path='Node/Child', property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), value_format='integer', value_cardinality=2)", "```"),
        ),
        carrier(
            "CA-M-POISON", "Node.Poison",
            claim("### Formal Claim", "", "```python",
                  "from anechoic.formal_claims import declare_entity",
                  "declare_entity(entity_name='Poison', relation_name='IS_PROPERTY_OF', base_path='Node')", "```"),
            role="Method", form="Policy",
        ),
    ]


def projection(*, namespace=False):
    rows = carriers()
    if namespace:
        rows.append(carrier("CA-R-NS", "ANECHOIC <+ MODEL", claim("Namespace declaration.")))
    data = build_subject_projection_data(rows)
    if namespace:
        data.setdefault("namespaces", []).append({
            "subject": "ANECHOIC <+ MODEL",
            "source": {"atom_id": "CA-R-NS", "version": 1},
        })
    return data


class SubjectProjectionViewTests(unittest.TestCase):
    def test_authority_mode_children_inherit_native_value_format(self):
        prefix = "Project.Settings.Authority Modes"
        children = ("Default Scope Unit Authority Mode", "Project Authority Mode")
        python_claim = claim(
            "```python", "from anechoic.formal_claims import declare_entity",
            "declare_entity(entity_name='Authority Modes', relation_name='IS_PROPERTY_OF',",
            "    base_path='Project.Settings', dependent_property_cardinality=2,",
            "    allowed_dependent_property_names=('Default Scope Unit Authority Mode', 'Project Authority Mode'),",
            "    dependent_property_value_format=str)", "```",
        )
        rows = [carrier("CA-R-1", "Project", claim("Project.")),
                carrier("CA-R-2632", prefix, python_claim)]
        rows.extend(carrier(f"CA-R-{index}", f"{prefix}.{name}",
                            native_property(name, prefix, "value_cardinality=1"))
                    for index, name in enumerate(children, 2633))
        data = build_subject_projection_data(rows)
        properties = next(row for row in data["entities"] if row["identity"] == "Project")["direct_properties"]
        for name in children:
            prop = next(row for row in properties if row["identity"] == f"{prefix}.{name}")
            self.assertEqual("string", prop["effective_value_format"])
            self.assertEqual({"CA-R-2632"},
                             {source["atom_id"] for source in prop["effective_value_format_sources"]})
        self.assertFalse(any(row.get("code") == "conflicting_property_value_formats" for row in data["diagnostics"]))
        document = views.render_primary_projection(data, 4)
        self.assertIn("dependent_property_value_format=str", document)

    def test_unrelated_native_str_keeps_its_format(self):
        data = build_subject_projection_data([
            carrier("CA-R-1", "Node", claim("Node.")),
            carrier("CA-R-2", "Node.Name", claim(
                "```python", "from anechoic.formal_claims import declare_entity",
                "declare_entity(entity_name='Name', relation_name='IS_PROPERTY_OF',",
                "    base_path='Node', value_format=str, value_cardinality=1)", "```")),
        ])
        props = next(row for row in data["entities"] if row["identity"] == "Node")["direct_properties"]
        self.assertEqual("str", next(row for row in props if row["identity"] == "Node.Name")["effective_value_format"])

    def test_qualified_leaf_and_empty_structural_domain_keep_inherited_format(self):
        data = build_subject_projection_data([
            carrier("CA-R-1", "Node", claim("Node.")),
            carrier("CA-R-2", "Node.Section", native_property("Section", "Node", "recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None)", "recursive_dependent_property_value_format='markdown'")),
            carrier("CA-R-3", "Node.Section.Group", native_property("Group", "Node.Section", "property_occurrence_cardinality=1", "value_cardinality=0")),
            carrier("CA-R-4", "Node.Section.Group.Summary", claim("```python", "property_rule(address='Node/(.Header.Role in RMED).Section.Group.Summary', value_format=None, values='0..1')", "```")),
        ])
        properties = next(row for row in data["entities"] if row["identity"] == "Node")["direct_properties"]
        group = next(row for row in properties if row["identity"] == "Node.Section.Group")
        summary = next(row for row in properties if row["identity"] == "Node.Section.Group.Summary")
        self.assertEqual("markdown", group["effective_value_format"])
        self.assertEqual("markdown", summary["effective_value_format"])
        self.assertEqual("Node/(.Header.Role in RMED).Section.Group.Summary", summary["contracts"][0]["property_selector"])
        self.assertEqual({"minimum": 0, "maximum": 1}, summary["contracts"][0]["value_cardinality"])
        self.assertFalse(any(row.get("code") == "conflicting_property_value_formats" for row in data["diagnostics"]))

    def test_recursive_format_inheritance_keeps_local_count_and_source(self):
        rows = [
            carrier("CA-R-1", "Node", claim("Node.")),
            carrier("CA-R-2", "Node.Section", native_property("Section", "Node", "recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None)", "recursive_dependent_property_value_format='markdown'")),
            carrier("CA-R-3", "Node.Section.Summary", native_property("Summary", "Node.Section", "value_cardinality=Cardinality(minimum=0, maximum=1)")),
            carrier("CA-R-4", "Node.Section.Nested.Detail", native_property("Detail", "Node.Section.Nested", "value_cardinality=Cardinality(minimum=0, maximum=1)")),
            carrier("CA-M-5", "Node.Section", native_property("Section", "Node", "recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None)", "recursive_dependent_property_value_format='int'"), role="Method", form="Policy"),
        ]
        data = build_subject_projection_data(rows)
        properties = next(row for row in data["entities"] if row["identity"] == "Node")["direct_properties"]
        summary = next(row for row in properties if row["identity"] == "Node.Section.Summary")
        self.assertEqual({"minimum": 0, "maximum": 1}, summary["contracts"][0]["value_cardinality"])
        self.assertIsNone(summary["contracts"][0]["value_format"])
        self.assertEqual(["CA-R-2"], [row["atom_id"] for row in summary["effective_value_format_sources"]])
        document = views.render_primary_projection(data, 3)
        self.assertEqual(2, document.count("effective value format: `markdown` — CA-R-2@1"))
        self.assertIn("value cardinality: `0..1`", document)
        self.assertNotIn("integer", document)
        self.assertFalse(any(row.get("code") == "conflicting_property_value_formats" for row in data["diagnostics"]))

    def test_conflicting_local_and_recursive_formats_are_diagnostic(self):
        data = build_subject_projection_data([
            carrier("CA-R-1", "Node", claim("Node.")),
            carrier("CA-R-2", "Node.Section", native_property("Section", "Node", "recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None)", "recursive_dependent_property_value_format='markdown'")),
            carrier("CA-R-3", "Node.Section.Summary", native_property("Summary", "Node.Section", "value_format=int", "value_cardinality=Cardinality(minimum=0, maximum=1)")),
        ])
        document = views.render_primary_projection(data, 3)
        self.assertNotIn("effective value format:", document)
        self.assertIn("Conflicting applicable value formats for Node.Section.Summary", document)
        self.assertIn("CA-R-2@1, CA-R-3@1", document)

    def test_level_three_shows_effective_occurrence_and_value_counts(self):
        data = build_subject_projection_data([
            carrier("CA-R-1", "Node", claim("Node.")),
            carrier("CA-R-2", "Node.Name", claim("```python", "from anechoic.formal_claims import declare_entity, Cardinality", "declare_entity(entity_name='Name', relation_name='IS_PROPERTY_OF', base_path='Node', property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), value_format='string', value_cardinality=Cardinality(minimum=0, maximum=1))", "```")),
        ])
        document = views.render_primary_projection(data, 3)
        self.assertIn("occurrence cardinality: `0..1`", document)
        self.assertIn("effective occurrence cardinality: `0..1`", document)
        self.assertIn("value cardinality: `0..1`", document)

    def test_explicit_new_namespace_roots_render_without_invented_parent(self):
        data = projection()
        data["namespaces"] = [
            {"subject": "ANECHOIC_MODEL", "source": {"atom_id": "CA-R-1", "version": 1}},
            {"subject": "ANECHOIC_STRUCTURE <+ Project", "source": {"atom_id": "CA-R-2", "version": 1}},
        ]
        document = views.render_primary_projection(data, 1)
        self.assertIn("\nANECHOIC_MODEL\n", document)
        self.assertIn("\nANECHOIC_STRUCTURE\n  <+ Project", document)
        self.assertNotIn("\nANECHOIC\n", document)

    def test_level_one_keeps_primary_tree_and_source_backed_namespace(self):
        document = views.render_primary_projection(projection(namespace=True), 1)
        self.assertIn("NARROWER_THAN: `/`", document)
        self.assertIn("Node", document)
        self.assertIn("\t/ Child", document)
        self.assertIn("## Namespace context", document)
        self.assertIn("<+ MODEL [CA-R-NS@1]", document)
        self.assertNotIn("Node.Status", document)

    def test_level_two_lists_direct_properties_only(self):
        document = views.render_primary_projection(projection(), 2)
        self.assertIn("## Direct properties", document)
        self.assertIn("property: `Node/Child.Status`", document)
        self.assertNotIn("[inherited]", document)
        child_section = document.split("### `Node/Child`", 1)[1]
        self.assertNotIn("property: `Node.Status`", child_section)

    def test_namespace_context_is_not_invented_without_source_evidence(self):
        document = views.render_primary_projection(projection(), 1)
        self.assertNotIn("## Namespace context", document)

    def test_level_three_keeps_inherited_origin_and_all_constraint_channels(self):
        document = views.render_primary_projection(projection(), 3)
        self.assertIn("## Effective properties", document)
        self.assertIn("property: `Node.Status` (relative `Status`) [inherited]", document)
        self.assertIn("origin: `Node`", document)
        self.assertIn("property_occurrence_cardinality=Cardinality(minimum=0, maximum=1)", document)
        self.assertIn("nesting: `property`", document)
        self.assertIn("occurrence cardinality: `0..1`", document)
        self.assertIn("value format: `integer`", document)
        self.assertIn("value cardinality: `2`", document)
        self.assertIn("CA-R-CHILD-STATUS@1", document)
        self.assertIn("CA-R-STATUS@1", document)

    def test_level_four_copies_formal_claim_blocks_verbatim_without_prose(self):
        document = views.render_primary_projection(projection(), 4)
        self.assertIn("## Primary Declaration Formal Claims", document)
        self.assertIn("value_cardinality=Cardinality(minimum=1, maximum=None)", document)
        self.assertIn("value_format='integer', value_cardinality=2)\n```", document)
        self.assertIn("ancestor Declaration `Node`", document)
        self.assertIn("Property Declaration Formal Claim", document)
        self.assertNotIn("Child declaration.", document)
        self.assertNotIn("Semantics", document)
        self.assertNotIn("Details", document)

    def test_non_declaration_source_is_not_rendered(self):
        document = views.render_primary_projection(projection(), 4)
        self.assertNotIn("Poison", document)
        self.assertNotIn("CA-M-POISON", document)

    def test_invalid_level_is_rejected(self):
        with self.assertRaises(ValueError):
            views.render_primary_projection(projection(), 5)


if __name__ == "__main__":
    unittest.main()
