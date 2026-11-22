"""Runtime facts and hashes, independent of the repository's Atom contents."""

from contextlib import redirect_stderr
from io import StringIO
import unittest

from KERNEL_MIXER_C59.relations import (
    compile_relation_registry, materialize, relation_registry,
)


def atom(ref, *, relation=None, form="Rule", body="## Claim\nOne claim.\n"):
    return {"source_path": ref + ".md", "status_group": "Current", "id": ref, "ref": ref,
            "version": 1, "status": "Active", "current_scope_unit": None,
            "claim_target_scope_unit": None, "role": "Requirement", "form": form,
            "tier": 1, "updated_at": None, "header_json": {"relations": relation or {}},
            "content_markdown": body, "content_properties_json": [],
            "relation_edges_json": [], "hash": None}


def relation_declaration(ref, name, binding=""):
    body = f'## Claim\n\n### Formal Claim\n\n```python\nsubject_path(address="Relation//{name}")\n{binding}\n```\n'
    row = atom(ref, form="Declaration", body=body)
    row["header_json"]["subjects"] = {
        "active": "ANECHOIC_MODEL <+ CFEL <+ Relation//" + name,
    }
    return row


def inverse_call(left, right, *, reverse=False):
    return f'relation(source="Relation//{left}", name="HAS_INVERSE", target="Relation//{right}", reverse={reverse})'


def declarations():
    return [
        relation_declaration("CA-R-1", "IS_CONTAINED_BY", inverse_call("IS_CONTAINED_BY", "CONTAINS")),
        relation_declaration("CA-R-2", "CONTAINS"),
    ]


class RelationTests(unittest.TestCase):
    def test_project_root_reference_has_derived_contains(self):
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.incremental_relations import materialize_delta

        root = {"name": "demo", "scope_unit_id": "DEMO-SU-00", "parent_name": None,
                "declared_label": None, "ordered": False, "order_number": None,
                "declaration_source_path": "project.md", "declaration_version": 1,
                "relation_edges_json": [], "hash": None}
        source = atom("CA-R-3")
        source["header_json"]["context"] = {"container": {"scope_unit": "DEMO-SU-00"}}
        sources = declarations() + [source]
        rows, scopes = materialize(sources, [root])
        edge = next(row for row in rows if row["ref"] == "CA-R-3")["relation_edges_json"][0]
        self.assertEqual(("Scope Unit", "demo"), (edge["target_kind"], edge["target_ref"]))
        self.assertEqual("CA-R-3", scopes[0]["relation_edges_json"][0]["target_ref"])
        self.assertTrue(scopes[0]["relation_edges_json"][0]["derived"])

        _, _, _, _, state, _ = materialize_delta(declarations(), [root])
        _, scopes, _, _, state, delta = materialize_delta(
            sources, [root], state, {source["source_path"]: source},
        )
        self.assertIsNotNone(delta)
        self.assertEqual("CA-R-3", scopes[0]["relation_edges_json"][0]["target_ref"])
        _, scopes, _, _, _, _ = materialize_delta(
            declarations(), [root], state, {source["source_path"]: None},
        )
        self.assertEqual([], scopes[0]["relation_edges_json"])

    def test_nested_header_container_atom_generates_both_directions(self):
        parent = atom("CA-P-1")
        child = atom("CA-P-2")
        child["header_json"]["context"] = {"container": {"atom": "CA-P-1"}}
        rows, _ = materialize(declarations() + [parent, child], [])
        by_ref = {row["ref"]: row for row in rows}
        direct = by_ref["CA-P-2"]["relation_edges_json"][0]
        inverse = by_ref["CA-P-1"]["relation_edges_json"][0]
        self.assertEqual(("IS_CONTAINED_BY", "CA-P-1", False),
                         (direct["relation_type"], direct["target_ref"], direct["derived"]))
        self.assertEqual(("CONTAINS", "CA-P-2", True),
                         (inverse["relation_type"], inverse["target_ref"], inverse["derived"]))
        self.assertEqual({}, child["header_json"]["relations"])
        self.assertEqual(1, parent["version"])

    def test_inverse_lives_on_counterpart_and_changes_its_hash(self):
        epic = atom("CA-P-1")
        task = atom("CA-P-2", relation={"is_contained_by": ["CA-P-1"]})
        rows, _ = materialize(declarations() + [epic, task], [])
        by_ref = {row["ref"]: row for row in rows}
        self.assertEqual("IS_CONTAINED_BY", by_ref["CA-P-2"]["relation_edges_json"][0]["relation_type"])
        self.assertEqual({"source_kind": "Atom", "source_ref": "CA-P-1",
                          "target_kind": "Atom", "target_ref": "CA-P-2",
                          "relation_type": "CONTAINS", "derived": True},
                         by_ref["CA-P-1"]["relation_edges_json"][0])
        before = by_ref["CA-P-1"]["hash"]
        changed, _ = materialize(declarations() + [epic, atom("CA-P-2")], [])
        after = next(row for row in changed if row["ref"] == "CA-P-1")
        self.assertNotEqual(before, after["hash"])
        self.assertEqual([], after["relation_edges_json"])
        self.assertIsNone(epic["hash"])
        self.assertEqual(1, epic["version"])

    def test_scope_rows_own_outgoing_inverse_facts(self):
        row = atom("CA-R-3")
        row["current_scope_unit"] = "ENGINE"
        scope = {"name": "ENGINE", "scope_unit_id": "CA-SU-1", "parent_name": None,
                 "declared_label": None, "ordered": False, "order_number": None,
                 "declaration_source_path": "scope.md", "declaration_version": 1,
                 "relation_edges_json": [], "hash": None}
        _, scopes = materialize(declarations() + [row], [scope])
        edge = scopes[0]["relation_edges_json"][0]
        self.assertEqual(("Scope Unit", "ENGINE", "Atom", "CA-R-3"),
                         tuple(edge[x] for x in ("source_kind", "source_ref", "target_kind", "target_ref")))
        self.assertEqual("CONTAINS", edge["relation_type"])
        self.assertTrue(edge["derived"])

    def test_scope_unit_id_relations_use_the_declared_scope_name(self):
        by_mapping = atom("CA-R-31", relation={"is_contained_by": {"scope_unit": "CA-SU-14"}})
        by_id = atom("CA-R-32", relation={"is_contained_by": "CA-SU-14"})
        unknown = atom("CA-R-33", relation={"is_contained_by": {"scope_unit": "CA-SU-999"}})
        parent = {"name": "CORE", "scope_unit_id": "CA-SU-9", "parent_name": None,
                  "declared_label": None, "ordered": False, "order_number": None,
                  "declaration_source_path": "core.md", "declaration_version": 1,
                  "relation_edges_json": [], "hash": None}
        scope = {"name": "FRAMEWORK_ENGINE", "scope_unit_id": "CA-SU-14", "parent_name": "CORE",
                 "declared_label": None, "ordered": False, "order_number": None,
                 "declaration_source_path": "engine.md", "declaration_version": 1,
                 "relation_edges_json": [], "hash": None}

        rows, scopes = materialize(declarations() + [by_mapping, by_id, unknown], [parent, scope])

        by_ref = {row["ref"]: row for row in rows}
        by_scope = {row["name"]: row for row in scopes}
        for ref in ("CA-R-31", "CA-R-32"):
            self.assertIn({"source_kind": "Atom", "source_ref": ref,
                           "target_kind": "Scope Unit", "target_ref": "FRAMEWORK_ENGINE",
                           "relation_type": "IS_CONTAINED_BY", "derived": False},
                          by_ref[ref]["relation_edges_json"])
        self.assertIn({"source_kind": "Atom", "source_ref": "CA-R-33",
                       "target_kind": "Scope Unit", "target_ref": "CA-SU-999",
                       "relation_type": "IS_CONTAINED_BY", "derived": False},
                      by_ref["CA-R-33"]["relation_edges_json"])
        self.assertIn({"source_kind": "Scope Unit", "source_ref": "FRAMEWORK_ENGINE",
                       "target_kind": "Scope Unit", "target_ref": "CORE",
                       "relation_type": "IS_CONTAINED_BY", "derived": False},
                      by_scope["FRAMEWORK_ENGINE"]["relation_edges_json"])
        self.assertIn({"source_kind": "Scope Unit", "source_ref": "FRAMEWORK_ENGINE",
                       "target_kind": "Atom", "target_ref": "CA-R-31",
                       "relation_type": "CONTAINS", "derived": True},
                      by_scope["FRAMEWORK_ENGINE"]["relation_edges_json"])
        self.assertEqual({"scope_unit": "CA-SU-14"}, by_mapping["header_json"]["relations"]["is_contained_by"])

    def test_only_current_literal_relation_metadata_establishes_inverses(self):
        rows = declarations()
        rows[0]["status_group"] = "Draft"
        registered, inverses = relation_registry(rows)
        self.assertNotIn("IS_CONTAINED_BY", registered)
        self.assertEqual({}, inverses)
        rows[0]["status_group"] = "Current"
        rows[0]["content_markdown"] += "\n" + inverse_call("A", "B") + "\n"
        registered, inverses = relation_registry(rows)
        self.assertEqual({"IS_CONTAINED_BY": "CONTAINS"}, inverses)
        self.assertNotIn("A", registered)

    def test_relation_declaration_registers_direct_fact_but_draft_does_not(self):
        declaration = relation_declaration("CA-R-1", "IS_WORK_REPORT_FOR")
        declaration["form"] = "Relation Declaration"
        report = atom("CA-R-REPORT", relation={"IS_WORK_REPORT_FOR": ["CA-P-TASK"]})
        task = atom("CA-P-TASK")

        rows, _ = materialize([declaration, report, task], [])
        self.assertIn(
            {
                "source_kind": "Atom", "source_ref": "CA-R-REPORT",
                "target_kind": "Atom", "target_ref": "CA-P-TASK",
                "relation_type": "IS_WORK_REPORT_FOR", "derived": False,
            },
            next(row for row in rows if row["ref"] == "CA-R-REPORT")["relation_edges_json"],
        )

        draft = dict(declaration, status_group="Draft")
        self.assertNotIn("IS_WORK_REPORT_FOR", relation_registry([draft])[0])
        rows, _ = materialize([draft, report, task], [])
        self.assertEqual([], next(row for row in rows if row["ref"] == "CA-R-REPORT")["relation_edges_json"])

    def test_inverse_alias_without_own_declaration_normalizes_once(self):
        declaration = relation_declaration(
            "CA-R-1", "CONTAINS",
            'relation(source="Relation//IS_CONTAINED_BY", name="IS_INVERSE_ALIAS_FOR", target="Relation//CONTAINS")',
        )
        parent = atom("CA-P-1", relation={"CONTAINS": ["CA-P-2"]})
        child = atom("CA-P-2", relation={"IS_CONTAINED_BY": ["CA-P-1"]})
        registry = compile_relation_registry([declaration, parent, child])

        self.assertEqual({"CONTAINS"}, set(registry.names))
        self.assertEqual({"IS_CONTAINED_BY": "CONTAINS"}, registry.aliases)
        rows, _ = materialize([declaration, parent, child], [])
        edges = next(row for row in rows if row["ref"] == "CA-P-1")["relation_edges_json"]
        self.assertEqual(
            [{"source_kind": "Atom", "source_ref": "CA-P-1", "target_kind": "Atom",
              "target_ref": "CA-P-2", "relation_type": "CONTAINS", "derived": False}],
            edges,
        )
        self.assertEqual({"IS_CONTAINED_BY": ["CA-P-1"]}, child["header_json"]["relations"])

    def test_instance_scoped_literal_metadata_is_warned_and_omitted(self):
        instance_scoped = relation_declaration(
            "CA-R-1", "DIRECT",
            f'# instances\n{inverse_call("DIRECT", "INVERSE")}\n'
            'relation(source="Relation//LEGACY", name="IS_INVERSE_ALIAS_FOR", target="Relation//DIRECT")\n',
        )
        inverse = relation_declaration("CA-R-2", "INVERSE")
        errors = StringIO()
        with redirect_stderr(errors):
            registry = compile_relation_registry([instance_scoped, inverse])
        self.assertEqual({"DIRECT", "INVERSE"}, set(registry.names))
        self.assertEqual({}, registry.inverse)
        self.assertEqual({}, registry.aliases)
        self.assertIn("unsupported Python relation metadata", errors.getvalue())

    def test_ambiguous_literal_inverses_warn_and_keep_direct_facts(self):
        metadata = [
            relation_declaration("A", "A", inverse_call("A", "B")),
            relation_declaration("B", "B"),
            relation_declaration("C", "C", inverse_call("C", "B")),
            relation_declaration("D", "D", inverse_call("D", "D")),
            relation_declaration("E", "E", inverse_call("E", "F")),
            relation_declaration("F", "F", inverse_call("F", "G")),
            relation_declaration("G", "G"),
            relation_declaration("J", "J", inverse_call("J", "K")),
            relation_declaration("K", "K", inverse_call("K", "J", reverse=True)),
        ]
        errors = StringIO()
        with redirect_stderr(errors):
            registered, inverses = relation_registry(metadata)
        self.assertEqual({"J": "K"}, inverses)
        self.assertTrue({"A", "B", "C", "D", "E", "F", "G", "J", "K"} <= registered)
        self.assertIn("multiple direct owners A, C", errors.getvalue())
        self.assertIn("self-pair", errors.getvalue())
        self.assertIn("derived Relation F is declared direct", errors.getvalue())

        source = atom("CA-P-1", relation={"A": ["CA-P-2"], "J": ["CA-P-3"]})
        with redirect_stderr(StringIO()):
            rows, _ = materialize(metadata + [source, atom("CA-P-2"), atom("CA-P-3")], [])
        by_ref = {row["ref"]: row for row in rows}
        self.assertIn({"source_kind": "Atom", "source_ref": "CA-P-1",
                       "target_kind": "Atom", "target_ref": "CA-P-2",
                       "relation_type": "A", "derived": False},
                      by_ref["CA-P-1"]["relation_edges_json"])
        self.assertIn({"source_kind": "Atom", "source_ref": "CA-P-1",
                       "target_kind": "Atom", "target_ref": "CA-P-3",
                       "relation_type": "J", "derived": False},
                      by_ref["CA-P-1"]["relation_edges_json"])
        self.assertEqual([], by_ref["CA-P-2"]["relation_edges_json"])
        self.assertIn({"source_kind": "Atom", "source_ref": "CA-P-3",
                       "target_kind": "Atom", "target_ref": "CA-P-1",
                       "relation_type": "K", "derived": True},
                      by_ref["CA-P-3"]["relation_edges_json"])

    def test_ambiguous_normalized_header_relation_warns_and_skips_links(self):
        source = atom("CA-P-4", relation={"BlOcKs": ["CA-P-5"]})
        errors = StringIO()
        with redirect_stderr(errors):
            rows, _ = materialize([
                relation_declaration("UPPER", "BLOCKS"),
                relation_declaration("LOWER", "blocks"),
                source,
                atom("CA-P-5"),
            ], [])
        self.assertEqual([], next(row for row in rows if row["ref"] == "CA-P-4")["relation_edges_json"])
        self.assertIn("CA-P-4.md: ambiguous registered Relation BlOcKs", errors.getvalue())
        self.assertIn("candidates: BLOCKS, blocks; link skipped", errors.getvalue())

    def test_unregistered_relations_and_prose_do_not_create_facts(self):
        row = atom("CA-R-4", relation={"unknown_relation": ["CA-R-5"]},
                   body="CA-R-4 CONTAINS CA-R-5\n")
        rows, _ = materialize(declarations() + [row], [])
        self.assertEqual([], rows[-1]["relation_edges_json"])

