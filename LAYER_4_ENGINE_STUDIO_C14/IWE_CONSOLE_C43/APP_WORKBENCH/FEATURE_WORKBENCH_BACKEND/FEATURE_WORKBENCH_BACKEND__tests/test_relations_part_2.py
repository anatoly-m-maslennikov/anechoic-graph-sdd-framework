"""Runtime facts and hashes, independent of the repository's Atom contents."""

from contextlib import redirect_stderr
from io import StringIO
import unittest

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import materialize, materialize_with_registry
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical


from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.test_relations import atom, declarations

class RelationTests(unittest.TestCase):
    def test_hash_is_deterministic_and_excludes_only_hash_field(self):
        rows, _ = materialize([atom("CA-R-5")], [])
        import hashlib
        data = {key: value for key, value in rows[0].items() if key != "hash"}
        self.assertEqual(hashlib.sha256(canonical(data).encode()).hexdigest(), rows[0]["hash"])
        self.assertEqual(rows, materialize([atom("CA-R-5")], [])[0])

    def test_duplicate_references_keep_both_carriers_and_first_graph_facts(self):
        task = atom("CA-P-2", relation={"is_contained_by": ["CA-P-1"]})
        other = dict(task, source_path="another-draft.md")
        errors = StringIO()
        with redirect_stderr(errors):
            rows, _ = materialize(declarations() + [atom("CA-P-1"), task, other], [])
        self.assertEqual(1, len(next(row for row in rows if row["ref"] == "CA-P-1")["relation_edges_json"]))
        self.assertEqual([task["source_path"], other["source_path"]],
                         [row["source_path"] for row in rows if row["ref"] == "CA-P-2"])
        self.assertTrue(next(row for row in rows if row["source_path"] == other["source_path"])["_graph_excluded"])

    def test_unassigned_draft_references_are_not_duplicates(self):
        first = dict(atom("draft-1"), id=None, ref=None, status_group="Draft")
        second = dict(atom("draft-2"), id=None, ref=None, status_group="Draft")
        rows, _ = materialize([first, second], [])
        self.assertEqual(2, len(rows))

    def test_reuses_unchanged_rows_and_rebuilds_inverse_neighbours(self):
        epic = atom("CA-P-1")
        task = atom("CA-P-2", relation={"is_contained_by": ["CA-P-1"]})
        unrelated = atom("CA-P-3")
        rows, _scopes, _registered, _inverse, cache = materialize_with_registry(
            declarations() + [epic, task, unrelated], [],
        )
        original = {row["ref"]: row for row in rows}
        changed_task = atom("CA-P-2")
        next_rows, _scopes, _registered, _inverse, next_cache = materialize_with_registry(
            declarations() + [epic, changed_task, unrelated], [], cache,
        )
        current = {row["ref"]: row for row in next_rows}
        self.assertIs(original["CA-P-3"], current["CA-P-3"])
        self.assertIsNot(original["CA-P-1"], current["CA-P-1"])
        self.assertEqual([], current["CA-P-1"]["relation_edges_json"])
        self.assertIsNot(original["CA-P-2"], current["CA-P-2"])
        self.assertIn("CA-P-2.md", next_cache)
        self.assertIn("CA-P-3.md", next_cache)

    def test_cache_preserves_duplicate_rows(self):
        first = atom("CA-P-1")
        second = atom("CA-P-2")
        _rows, _scopes, _registered, _inverse, cache = materialize_with_registry([first, second], [])
        duplicate = dict(second, source_path="duplicate.md")
        _rows, _scopes, _registered, _inverse, next_cache = materialize_with_registry(
            [first, second, duplicate], [], cache,
        )
        self.assertEqual({"CA-P-1.md", "CA-P-2.md", "duplicate.md"}, set(next_cache))

    def test_registry_is_calculated_once_per_materialization(self):
        import KERNEL_MIXER_C59.relations as relations

        original = relations.compile_relation_registry
        calls = 0

        def counted(rows):
            nonlocal calls
            calls += 1
            return original(rows)

        relations.compile_relation_registry = counted
        try:
            materialize_with_registry(declarations() + [atom("CA-P-1")], [])
        finally:
            relations.compile_relation_registry = original
        self.assertEqual(1, calls)

    def test_reuses_direct_facts_for_unchanged_rows(self):
        import KERNEL_MIXER_C59.relations as relations

        metadata = declarations()
        epic = atom("CA-P-1")
        task = atom("CA-P-2", relation={"is_contained_by": ["CA-P-1"]})
        unrelated = atom("CA-P-3")
        original = relations._atom_facts
        calls = 0

        def counted(*args):
            nonlocal calls
            calls += 1
            return original(*args)

        relations._atom_facts = counted
        try:
            _rows, _scopes, _registered, _inverse, cache = materialize_with_registry(
                metadata + [epic, task, unrelated], [],
            )
            initial_calls = calls
            materialize_with_registry(metadata + [epic, atom("CA-P-2"), unrelated], [], cache)
        finally:
            relations._atom_facts = original
        self.assertEqual(5, initial_calls)
        self.assertEqual(6, calls)

    def test_relation_target_change_rebuilds_old_and_new_inverse_neighbours(self):
        old = atom("CA-P-1")
        new = atom("CA-P-3")
        task = atom("CA-P-2", relation={"is_contained_by": ["CA-P-1"]})
        rows, _scopes, _registered, _inverse, cache = materialize_with_registry(
            declarations() + [old, task, new], [],
        )
        changed = atom("CA-P-2", relation={"is_contained_by": ["CA-P-3"]})
        rows, _scopes, _registered, _inverse, _cache = materialize_with_registry(
            declarations() + [old, changed, new], [], cache,
        )
        by_ref = {row["ref"]: row for row in rows}
        self.assertEqual([], by_ref["CA-P-1"]["relation_edges_json"])
        self.assertEqual("CONTAINS", by_ref["CA-P-3"]["relation_edges_json"][0]["relation_type"])

    def test_scope_alias_or_registry_change_reparses_facts(self):
        import KERNEL_MIXER_C59.relations as relations

        source = atom("CA-P-1", relation={"is_contained_by": {"scope_unit": "CA-SU-1"}})
        first_scope = {"name": "FIRST", "scope_unit_id": "CA-SU-1", "parent_name": None,
                       "declared_label": None, "ordered": False, "order_number": None,
                       "declaration_source_path": "first.md", "declaration_version": 1,
                       "relation_edges_json": [], "hash": None}
        second_scope = dict(first_scope, name="SECOND")
        original = relations._atom_facts
        calls = 0

        def counted(*args):
            nonlocal calls
            calls += 1
            return original(*args)

        relations._atom_facts = counted
        try:
            _rows, _scopes, _registered, _inverse, cache = materialize_with_registry(
                declarations() + [source], [first_scope],
            )
            rows, _scopes, _registered, _inverse, _cache = materialize_with_registry(
                declarations() + [source], [second_scope], cache,
            )
        finally:
            relations._atom_facts = original
        self.assertEqual(6, calls)
        edge = next(row for row in rows if row["ref"] == "CA-P-1")["relation_edges_json"][0]
        self.assertEqual("SECOND", edge["target_ref"])

