"""Runtime facts and hashes, independent of the repository's Atom contents."""

from contextlib import redirect_stderr  # noqa: F401
from io import StringIO  # noqa: F401
import unittest

from .relation_registry_cases import RelationRegistryCases

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    compile_relation_registry,  # noqa: F401
    materialize,
    relation_registry,  # noqa: F401
)


def atom(ref, *, relation=None, form="Rule", body="## Claim\nOne claim.\n"):
    return {
        "source_path": ref + ".md",
        "status_group": "Current",
        "id": ref,
        "ref": ref,
        "version": 1,
        "status": "Active",
        "current_scope_unit": None,
        "claim_target_scope_unit": None,
        "role": "Requirement",
        "form": form,
        "tier": 1,
        "updated_at": None,
        "header_json": {"relations": relation or {}},
        "content_markdown": body,
        "content_properties_json": [],
        "relation_edges_json": [],
        "hash": None,
    }


def relation_declaration(ref, name, binding=""):
    body = (
        "## Claim\n\n### Formal Claim\n\n```python\n"
        'subject_path(address="Relation//'
        f"{name}"
        '")\n'
        f"{binding}"
        "\n```\n"
    )
    row = atom(ref, form="Declaration", body=body)
    row["header_json"]["subjects"] = {
        "active": "ANECHOIC_MODEL <+ CFEL <+ Relation//" + name,
    }
    return row


def inverse_call(left, right, *, reverse=False):
    return (
        'relation(source="Relation//'
        f"{left}"
        '", name="HAS_INVERSE", target="Relation//'
        f"{right}"
        '", reverse='
        f"{reverse}"
        ")"
    )


def declarations():
    return [
        relation_declaration(
            "CA-R-1",
            "IS_CONTAINED_BY",
            inverse_call("IS_CONTAINED_BY", "CONTAINS"),
        ),
        relation_declaration("CA-R-2", "CONTAINS"),
    ]


def project_root_relation():
    root = {
        "name": "demo",
        "scope_unit_id": "DEMO-SU-00",
        "parent_name": None,
        "declared_label": None,
        "ordered": False,
        "order_number": None,
        "declaration_source_path": "project.md",
        "declaration_version": 1,
        "relation_edges_json": [],
        "hash": None,
    }
    source = atom("CA-R-3")
    source["header_json"]["context"] = {
        "container": {"scope_unit": "DEMO-SU-00"}
    }
    return root, source


class RelationTests(RelationRegistryCases, unittest.TestCase):
    def test_project_root_reference_has_derived_contains(self):
        root, source = project_root_relation()
        sources = declarations() + [source]
        rows, scopes = materialize(sources, [root])
        edge = next(row for row in rows if row["ref"] == "CA-R-3")[
            "relation_edges_json"
        ][0]
        self.assertEqual(
            ("Scope Unit", "demo"), (edge["target_kind"], edge["target_ref"])
        )
        self.assertEqual(
            "CA-R-3", scopes[0]["relation_edges_json"][0]["target_ref"]
        )
        self.assertTrue(scopes[0]["relation_edges_json"][0]["derived"])

    def test_nested_header_container_atom_generates_both_directions(self):
        parent = atom("CA-P-1")
        child = atom("CA-P-2")
        child["header_json"]["context"] = {"container": {"atom": "CA-P-1"}}
        rows, _ = materialize(declarations() + [parent, child], [])
        by_ref = {row["ref"]: row for row in rows}
        direct = by_ref["CA-P-2"]["relation_edges_json"][0]
        inverse = by_ref["CA-P-1"]["relation_edges_json"][0]
        self.assertEqual(
            ("IS_CONTAINED_BY", "CA-P-1", False),
            (direct["relation_type"], direct["target_ref"], direct["derived"]),
        )
        self.assertEqual(
            ("CONTAINS", "CA-P-2", True),
            (
                inverse["relation_type"],
                inverse["target_ref"],
                inverse["derived"],
            ),
        )
        self.assertEqual({}, child["header_json"]["relations"])
        self.assertEqual(1, parent["version"])

    def test_inverse_lives_on_counterpart_and_changes_its_hash(self):
        epic = atom("CA-P-1")
        task = atom("CA-P-2", relation={"is_contained_by": ["CA-P-1"]})
        rows, _ = materialize(declarations() + [epic, task], [])
        by_ref = {row["ref"]: row for row in rows}
        self.assertEqual(
            "IS_CONTAINED_BY",
            by_ref["CA-P-2"]["relation_edges_json"][0]["relation_type"],
        )
        self.assertEqual(
            {
                "source_kind": "Atom",
                "source_ref": "CA-P-1",
                "target_kind": "Atom",
                "target_ref": "CA-P-2",
                "relation_type": "CONTAINS",
                "derived": True,
            },
            by_ref["CA-P-1"]["relation_edges_json"][0],
        )
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
        scope = {
            "name": "ENGINE",
            "scope_unit_id": "CA-SU-1",
            "parent_name": None,
            "declared_label": None,
            "ordered": False,
            "order_number": None,
            "declaration_source_path": "scope.md",
            "declaration_version": 1,
            "relation_edges_json": [],
            "hash": None,
        }
        _, scopes = materialize(declarations() + [row], [scope])
        edge = scopes[0]["relation_edges_json"][0]
        self.assertEqual(
            ("Scope Unit", "ENGINE", "Atom", "CA-R-3"),
            tuple(
                edge[x]
                for x in (
                    "source_kind",
                    "source_ref",
                    "target_kind",
                    "target_ref",
                )
            ),
        )
        self.assertEqual("CONTAINS", edge["relation_type"])
        self.assertTrue(edge["derived"])

    def test_scope_unit_id_relations_use_the_declared_scope_name(self):
        by_mapping = atom(
            "CA-R-31", relation={"is_contained_by": {"scope_unit": "CA-SU-14"}}
        )
        by_id = atom("CA-R-32", relation={"is_contained_by": "CA-SU-14"})
        unknown = atom(
            "CA-R-33",
            relation={"is_contained_by": {"scope_unit": "CA-SU-999"}},
        )
        parent = {
            "name": "CORE",
            "scope_unit_id": "CA-SU-9",
            "parent_name": None,
            "declared_label": None,
            "ordered": False,
            "order_number": None,
            "declaration_source_path": "core.md",
            "declaration_version": 1,
            "relation_edges_json": [],
            "hash": None,
        }
        scope = {
            "name": "FRAMEWORK_ENGINE",
            "scope_unit_id": "CA-SU-14",
            "parent_name": "CORE",
            "declared_label": None,
            "ordered": False,
            "order_number": None,
            "declaration_source_path": "engine.md",
            "declaration_version": 1,
            "relation_edges_json": [],
            "hash": None,
        }

        rows, scopes = materialize(
            declarations() + [by_mapping, by_id, unknown], [parent, scope]
        )

        by_ref = {row["ref"]: row for row in rows}
        by_scope = {row["name"]: row for row in scopes}
        self._assert_atom_scope_edges(by_ref)
        self._assert_scope_edges(by_scope, by_mapping)

    def _assert_atom_scope_edges(self, by_ref):
        for ref in ("CA-R-31", "CA-R-32"):
            self.assertIn(
                {
                    "source_kind": "Atom",
                    "source_ref": ref,
                    "target_kind": "Scope Unit",
                    "target_ref": "FRAMEWORK_ENGINE",
                    "relation_type": "IS_CONTAINED_BY",
                    "derived": False,
                },
                by_ref[ref]["relation_edges_json"],
            )
        self.assertIn(
            {
                "source_kind": "Atom",
                "source_ref": "CA-R-33",
                "target_kind": "Scope Unit",
                "target_ref": "CA-SU-999",
                "relation_type": "IS_CONTAINED_BY",
                "derived": False,
            },
            by_ref["CA-R-33"]["relation_edges_json"],
        )

    def _assert_scope_edges(self, by_scope, by_mapping):
        self.assertIn(
            {
                "source_kind": "Scope Unit",
                "source_ref": "FRAMEWORK_ENGINE",
                "target_kind": "Scope Unit",
                "target_ref": "CORE",
                "relation_type": "IS_CONTAINED_BY",
                "derived": False,
            },
            by_scope["FRAMEWORK_ENGINE"]["relation_edges_json"],
        )
        self.assertIn(
            {
                "source_kind": "Scope Unit",
                "source_ref": "FRAMEWORK_ENGINE",
                "target_kind": "Atom",
                "target_ref": "CA-R-31",
                "relation_type": "CONTAINS",
                "derived": True,
            },
            by_scope["FRAMEWORK_ENGINE"]["relation_edges_json"],
        )
        self.assertEqual(
            {"scope_unit": "CA-SU-14"},
            by_mapping["header_json"]["relations"]["is_contained_by"],
        )
