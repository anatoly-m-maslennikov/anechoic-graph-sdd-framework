from __future__ import annotations

import random
import unittest


from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.incremental_relations import materialize_delta  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.test_relations import atom, declarations  # noqa: E402




class _GuardedBucket(frozenset):
    reads = 0

    def __iter__(self):
        type(self).reads += 1
        return super().__iter__()


class IncrementalRelationTests(unittest.TestCase):
    def test_ordinary_delta_refreshes_only_the_changed_fact_support(self):
        import IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.incremental_relation_state as incremental

        leaves = [
            atom(
                f"CA-P-{number}",
                relation={"IS_CONTAINED_BY": [f"CA-P-MISSING-{number}"]},
            )
            for number in range(1000)
        ]
        _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(
            declarations() + leaves, [],
        )

        endpoint = ("Atom", "CA-P-999")
        guarded = _GuardedBucket(state.facts_by_endpoint[endpoint])
        state.facts_by_endpoint[endpoint] = guarded
        guarded_support = _GuardedBucket(state.support[endpoint])
        state.support[endpoint] = guarded_support
        original = incremental._support_for_fact
        calls = []

        def counted(fact, *args):
            calls.append(fact)
            return original(fact, *args)

        incremental._support_for_fact = counted
        try:
            changed = dict(leaves[0], version=2)
            original_compiler = incremental.compile_registry
            incremental.compile_registry = lambda _atoms: self.fail("ordinary delta compiled all sources")
            try:
                _rows, _scopes, _registered, _inverse, next_state, _delta = materialize_delta(
                    declarations() + [changed, *leaves[1:]], [], state,
                    {changed["source_path"]: changed},
                )
            finally:
                incremental.compile_registry = original_compiler
        finally:
            incremental._support_for_fact = original
        self.assertEqual(
            [("Atom", "CA-P-0", "IS_CONTAINED_BY", "Atom", "CA-P-MISSING-0")], calls
        )
        self.assertEqual(0, _GuardedBucket.reads)
        self.assertIs(guarded, next_state.facts_by_endpoint[endpoint])
        self.assertIs(guarded_support, next_state.support[endpoint])

    def test_endpoint_presence_changes_match_full_materialization(self):
        child = atom("CA-P-1", relation={"IS_CONTAINED_BY": ["CA-P-2"]})
        parent = atom("CA-P-2")
        unrelated = atom("CA-P-3")
        initial = declarations() + [child, unrelated]
        _, _, _, _, state, _ = materialize_delta(initial, [])
        for sources, changes in (
            (initial + [parent], {parent["source_path"]: parent}),
            (initial, {parent["source_path"]: None}),
        ):
            rows, scopes, _, _, state, delta = materialize_delta(sources, [], state, changes)
            expected, expected_scopes, *_ = materialize_delta(sources, [])
            self.assertIsNotNone(delta)
            self.assertEqual(expected, rows)
            self.assertEqual(expected_scopes, scopes)

    def test_duplicate_reference_changes_use_full_membership_boundary(self):
        first = atom("CA-R-X")
        second = dict(atom("CA-R-X"), source_path="second.md")
        _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta([first, second], [])
        self.assertEqual(frozenset({"second.md"}), state.excluded_paths)

        still_duplicate = dict(first, content_markdown="## Claim\nChanged.\n")
        rows, _scopes, _registered, _inverse, state, delta = materialize_delta(
            [still_duplicate, second], [], state, {"CA-R-X.md": still_duplicate},
        )
        self.assertIsNone(delta)
        self.assertEqual(["CA-R-X", "CA-R-X"], [row["ref"] for row in rows])

        third = dict(atom("CA-R-X"), source_path="third.md")
        rows, _scopes, _registered, _inverse, state, delta = materialize_delta(
            [still_duplicate, second, third], [], state, {"third.md": third},
        )
        self.assertIsNone(delta)
        self.assertEqual(["CA-R-X", "CA-R-X", "CA-R-X"], [row["ref"] for row in rows])

        renamed = dict(still_duplicate, id="CA-R-Y", ref="CA-R-Y")
        rows, _scopes, _registered, _inverse, _state, delta = materialize_delta(
            [renamed, second], [], state, {"CA-R-X.md": renamed},
        )
        self.assertIsNone(delta)
        self.assertEqual({"CA-R-X", "CA-R-Y"}, {row["ref"] for row in rows})

    def test_draft_without_reference_is_materialized_by_an_ordinary_delta(self):
        draft = dict(atom("draft"), id=None, ref=None, status_group="Draft")
        rows, _scopes, _registered, _inverse, state, _delta = materialize_delta([draft], [])
        self.assertEqual(1, len(rows))
        changed = dict(draft, content_markdown="## Claim\nChanged draft.\n")
        rows, _scopes, _registered, _inverse, _state, delta = materialize_delta(
            [changed], [], state, {"draft.md": changed},
        )
        self.assertIn("draft.md", delta.old_atoms)
        self.assertIn("draft.md", delta.new_atoms)
        self.assertEqual("Changed draft.", rows[0]["content_markdown"].splitlines()[-1])

    def test_unrelated_outgoing_sets_keep_their_identity(self):
        first = atom("CA-P-1")
        second = atom("CA-P-2", relation={"is_contained_by": ["CA-P-1"]})
        third = atom("CA-P-3")
        fourth = atom("CA-P-4", relation={"is_contained_by": ["CA-P-3"]})
        _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(
            declarations() + [first, second, third, fourth], [],
        )
        untouched = state.outgoing[("Atom", "CA-P-3")]
        changed = atom("CA-P-2")
        _rows, _scopes, _registered, _inverse, next_state, _delta = materialize_delta(
            declarations() + [first, changed, third, fourth], [], state, {"CA-P-2.md": changed},
        )
        self.assertIs(untouched, next_state.outgoing[("Atom", "CA-P-3")])

    def test_rename_with_same_reference_stays_incremental(self):
        source = atom("CA-P-1")
        _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta([source], [])
        moved = dict(source, source_path="moved.md")
        rows, _scopes, _registered, _inverse, state, delta = materialize_delta(
            [moved], [], state, {"CA-P-1.md": None, "moved.md": moved},
        )
        self.assertIsNotNone(delta)
        self.assertIn("CA-P-1.md", delta.old_atoms)
        self.assertIn("moved.md", delta.new_atoms)
        self.assertEqual(["moved.md"], list(state.atom_order))
        self.assertEqual(["moved.md"], [row["source_path"] for row in rows])

    def test_same_reference_rename_keeps_edges_in_both_change_orders(self):
        target = atom("CA-P-1")
        source = atom("CA-P-2", relation={"is_contained_by": ["CA-P-1"]})
        initial = declarations() + [target, source]
        moved = dict(source, source_path="moved.md")
        expected, _scopes, _types, _inverse, _state, _delta = materialize_delta(
            declarations() + [target, moved], [],
        )

        entries = [("CA-P-2.md", None), ("moved.md", moved)]
        for seed in range(8):
            shuffled = list(entries)
            random.Random(seed).shuffle(shuffled)
            changes = dict(shuffled)
            _rows, _scopes, _types, _inverse, state, _delta = materialize_delta(initial, [])
            rows, _scopes, _types, _inverse, _state, delta = materialize_delta(
                declarations() + [target, moved], [], state, changes,
            )
            self.assertIsNotNone(delta)
            self.assertEqual(expected, rows)
            by_ref = {row["ref"]: row for row in rows}
            self.assertEqual("IS_CONTAINED_BY", by_ref["CA-P-2"]["relation_edges_json"][0]["relation_type"])
            self.assertEqual("CONTAINS", by_ref["CA-P-1"]["relation_edges_json"][0]["relation_type"])

    def test_new_duplicate_forces_full_but_ignored_delete_does_not(self):
        first = atom("CA-P-1")
        _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta([first], [])
        second = dict(atom("CA-P-2"), source_path="second.md")
        third = dict(atom("CA-P-2"), source_path="third.md")
        rows, _scopes, _registered, _inverse, state, delta = materialize_delta(
            [first, second, third], [], state, {"second.md": second, "third.md": third},
        )
        self.assertIsNone(delta)
        self.assertEqual(["CA-P-1", "CA-P-2", "CA-P-2"], [row["ref"] for row in rows])

        changed = dict(first, content_markdown="## Claim\nChanged.\n")
        rows, _scopes, _registered, _inverse, _state, delta = materialize_delta(
            [changed, second, third], [], state, {"ignored.md": None, "CA-P-1.md": changed},
        )
        self.assertIsNotNone(delta)
        self.assertEqual("Changed.", rows[0]["content_markdown"].splitlines()[-1])

