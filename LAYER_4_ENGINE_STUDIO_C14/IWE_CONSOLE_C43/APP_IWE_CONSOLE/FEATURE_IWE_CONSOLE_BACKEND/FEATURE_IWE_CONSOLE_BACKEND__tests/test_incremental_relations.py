from __future__ import annotations

import unittest
from unittest.mock import patch


from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import materialize_delta
from KERNEL_MIXER_C59.graph_store import graph_delta_state, graph_state  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import compile_registry  # noqa: E402
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__tests.test_relations import atom, declarations, project_root_relation  # noqa: E402


class _RelationReadProbe(dict):
    reads = 0

    def get(self, name, default=None):
        if name == "relations":
            self.reads += 1
        return super().get(name, default)


class IncrementalRelationTests(unittest.TestCase):
    def test_root_contains_delta_follows_carrier_addition_and_removal(self):
        root, source = project_root_relation()
        _, _, _, _, state, _ = materialize_delta(declarations(), [root])
        _, scopes, _, _, state, delta = materialize_delta(
            declarations() + [source], [root], state, {source["source_path"]: source},
        )
        self.assertIsNotNone(delta)
        self.assertEqual("CA-R-3", scopes[0]["relation_edges_json"][0]["target_ref"])
        _, scopes, _, _, _, _ = materialize_delta(
            declarations(), [root], state, {source["source_path"]: None},
        )
        self.assertEqual([], scopes[0]["relation_edges_json"])

    def test_all_carriers_are_retained_without_polluting_the_current_graph(self):
        first_parent, second_parent = atom("CA-P-1"), atom("CA-P-3")
        current = atom("CA-P-2", relation={"IS_CONTAINED_BY": ["CA-P-1"]})
        duplicate = dict(atom("CA-P-2", relation={"IS_CONTAINED_BY": ["CA-P-3"]}),
                         source_path="duplicate.md")
        archived = dict(atom("CA-P-2@1", relation={"IS_CONTAINED_BY": ["CA-P-3"]}),
                        status_group="Archived", source_path="archived.md")
        sources = declarations() + [first_parent, second_parent, current, duplicate, archived]
        rows, scopes, names, _, state, _ = materialize_delta(sources, [])
        self.assertEqual(len(sources), len(rows))
        self.assertEqual({"duplicate.md", "archived.md"},
                         {row["source_path"] for row in rows if row.get("_graph_excluded")})
        for row in rows:
            if row.get("_graph_excluded"):
                self.assertEqual([], row["relation_edges_json"])
                self.assertEqual(1, len(row["_carrier_relation_edges_json"]))
        graph = graph_state(rows, scopes, names)
        self.assertEqual({("Atom", "CA-P-2", "Atom", "CA-P-1", "IS_CONTAINED_BY", False)},
                         set(graph.edges["IS_CONTAINED_BY"]))

        sources.remove(current)
        rows, scopes, names, _, _, delta = materialize_delta(sources, [], state, {current["source_path"]: None})
        self.assertIsNone(delta)
        graph = graph_state(rows, scopes, names)
        self.assertEqual({("Atom", "CA-P-2", "Atom", "CA-P-3", "IS_CONTAINED_BY", False)},
                         set(graph.edges["IS_CONTAINED_BY"]))

    def test_archived_carrier_delta_does_not_change_graph(self):
        source = atom("CA-P-1")
        initial = declarations() + [source]
        rows, scopes, names, _, state, _ = materialize_delta(initial, [])
        previous = graph_state(rows, scopes, names)
        archived = dict(atom("CA-P-1@1", relation={"IS_CONTAINED_BY": ["CA-P-2"]}),
                        status_group="Archived", source_path="archived.md")
        rows, scopes, names, _, state, delta = materialize_delta(initial + [archived], [], state,
                                                                  {"archived.md": archived})
        self.assertIsNotNone(delta)
        self.assertIn("archived.md", delta.new_atoms)
        actual, *_ = graph_delta_state(previous, delta, names)
        self.assertEqual(previous, actual)
        _, _, names, _, _, delta = materialize_delta(initial, [], state, {"archived.md": None})
        self.assertIsNotNone(delta)
        self.assertIn("archived.md", delta.old_atoms)

    def test_static_registry_survives_changes_and_full_rebuild_without_compilation(self):
        metadata = declarations()
        registry = compile_registry(metadata).registry
        source = atom("CA-P-100")
        changed = atom("CA-P-100", relation={"IS_CONTAINED_BY": ["CA-P-200"]})
        module = "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.incremental_relation_state"
        with patch(f"{module}.compile_registry", side_effect=AssertionError("compiled")), \
             patch(f"{module}.registry_contribution", side_effect=AssertionError("compiled contribution")):
            _, _, _, _, state, _ = materialize_delta(metadata + [source], [], registry=registry)
            _, _, _, _, state, delta = materialize_delta(metadata + [changed], [], state, {source["source_path"]: changed})
            self.assertIsNotNone(delta)
            _, _, names, inverse, state, delta = materialize_delta(metadata + [changed], [], state, None)
            self.assertIsNone(delta)
            self.assertEqual(registry.names, names)
            self.assertEqual(registry.inverse, inverse)
            self.assertTrue(state.static_registry)

    def test_unique_deleted_sources_leave_no_relation_cache_keys(self):
        sources = declarations() + [atom("CA-P-100")]
        _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(sources, [])
        baseline = dict(state.outgoing)
        for number in range(200, 220):
            row = atom(f"CA-P-{number}", relation={"IS_CONTAINED_BY": ["CA-P-100"]})
            _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(
                sources + [row], [], state, {row["source_path"]: row},
            )
            rows, _scopes, _registered, _inverse, state, delta = materialize_delta(
                sources, [], state, {row["source_path"]: None},
            )
            self.assertEqual(baseline, state.outgoing)
            self.assertIn("CA-P-100.md", delta.new_atoms)
            self.assertIn(row["source_path"], delta.old_atoms)
            self.assertNotIn(row["source_path"], delta.new_atoms)
            target = next(item for item in rows if item["ref"] == "CA-P-100")
            self.assertEqual([], target["relation_edges_json"])

    def test_relation_cache_keeps_other_children_until_last_delete(self):
        sources = declarations() + [atom("CA-P-100")]
        _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(sources, [])
        children = [atom(f"CA-P-{number}", relation={"IS_CONTAINED_BY": ["CA-P-100"]}) for number in range(200, 203)]
        for child in children:
            sources.append(child)
            _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(
                sources, [], state, {child["source_path"]: child},
            )
        for index, child in enumerate(children):
            sources.remove(child)
            rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(
                sources, [], state, {child["source_path"]: None},
            )
            target = next(item for item in rows if item["ref"] == "CA-P-100")
            self.assertEqual(2 - index, len(target["relation_edges_json"]))
            self.assertTrue(all(state.outgoing.values()))
        self.assertEqual({}, state.outgoing)

    def test_change_updates_source_and_inverse_neighbours_only(self):
        old = atom("CA-P-1")
        new = atom("CA-P-3")
        task = atom("CA-P-2", relation={"is_contained_by": ["CA-P-1"]})
        rows, _scopes, _registered, _inverse, state, delta = materialize_delta(declarations() + [old, task, new], [])
        self.assertIsNone(delta)
        changed = atom("CA-P-2", relation={"is_contained_by": ["CA-P-3"]})
        rows, _scopes, _registered, _inverse, state, delta = materialize_delta(
            declarations() + [old, changed, new], [], state, {"CA-P-2.md": changed},
        )
        self.assertEqual({"CA-P-1.md", "CA-P-2.md", "CA-P-3.md"}, set(delta.old_atoms))
        self.assertEqual(set(delta.old_atoms), set(delta.new_atoms))
        by_ref = {row["ref"]: row for row in rows}
        self.assertEqual([], by_ref["CA-P-1"]["relation_edges_json"])
        self.assertEqual("CONTAINS", by_ref["CA-P-3"]["relation_edges_json"][0]["relation_type"])

    def test_legacy_inverse_writing_contributes_the_one_canonical_fact(self):
        parent = atom("CA-P-1", relation={"CONTAINS": ["CA-P-2"]})
        child = atom("CA-P-2", relation={"IS_CONTAINED_BY": ["CA-P-1"]})
        rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(
            declarations() + [parent, child], [],
        )
        by_ref = {row["ref"]: row for row in rows}
        self.assertEqual(1, len(by_ref["CA-P-2"]["relation_edges_json"]))
        self.assertEqual("IS_CONTAINED_BY", by_ref["CA-P-2"]["relation_edges_json"][0]["relation_type"])
        self.assertEqual(1, len(by_ref["CA-P-1"]["relation_edges_json"]))
        self.assertEqual("CONTAINS", by_ref["CA-P-1"]["relation_edges_json"][0]["relation_type"])

        rows, _scopes, _registered, _inverse, _state, delta = materialize_delta(
            declarations() + [child], [], state, {parent["source_path"]: None},
        )
        self.assertIn(child["source_path"], delta.new_atoms)
        self.assertIn(
            "IS_CONTAINED_BY",
            {edge["relation_type"]
             for edge in next(row for row in rows if row["ref"] == "CA-P-2")["relation_edges_json"]},
        )

    def test_dangling_inverse_edge_survives_target_delete_and_reappearance(self):
        for authored_relation in ("IS_CONTAINED_BY", "CONTAINS"):
            with self.subTest(authored_relation=authored_relation):
                source = atom("CA-P-1", relation={authored_relation: ["CA-P-2"]})
                target = atom("CA-P-2")
                initial = declarations() + [source, target]
                _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(initial, [])

                rows, _scopes, _registered, _inverse, state, delta = materialize_delta(
                    declarations() + [source], [], state, {target["source_path"]: None},
                )
                self.assertIn(source["source_path"], delta.new_atoms)
                self.assertEqual(
                    {("IS_CONTAINED_BY", False), ("CONTAINS", True)},
                    {(edge["relation_type"], edge["derived"])
                     for edge in next(row for row in rows if row["ref"] == "CA-P-1")["relation_edges_json"]},
                )

                restored = dict(target, version=2)
                expected, _scopes, _registered, _inverse, _state, _delta = materialize_delta(
                    declarations() + [source, restored], [],
                )
                rows, _scopes, _registered, _inverse, _state, delta = materialize_delta(
                    declarations() + [source, restored], [], state, {restored["source_path"]: restored},
                )
                self.assertEqual(expected, rows)
                self.assertEqual({source["source_path"], restored["source_path"]}, set(delta.new_atoms))

    def test_delete_returns_old_row_and_prunes_state(self):
        source = atom("CA-P-1")
        rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(declarations() + [source], [])
        rows, _scopes, _registered, _inverse, state, delta = materialize_delta(
            declarations(), [], state, {"CA-P-1.md": None},
        )
        self.assertIn("CA-P-1.md", delta.old_atoms)
        self.assertNotIn("CA-P-1.md", delta.new_atoms)
        self.assertNotIn("CA-P-1.md", state.raw_by_path)
        self.assertNotIn("CA-P-1", [row["ref"] for row in rows])

    def test_relation_registry_change_uses_full_boundary(self):
        source = atom("CA-P-1")
        metadata = declarations()
        _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(metadata + [source], [])
        changed = dict(metadata[0], content_markdown="## Claim\n", header_json={"relations": {}})
        _rows, _scopes, _registered, _inverse, _state, delta = materialize_delta(
            [changed, metadata[1], source], [], state, {changed["source_path"]: changed},
        )
        self.assertIsNone(delta)

    def test_registry_source_prose_change_keeps_incremental_delta(self):
        metadata = declarations()
        source = atom("CA-P-1")
        _rows, _scopes, _registered, _inverse, state, _delta = materialize_delta(metadata + [source], [])
        changed = dict(metadata[0], content_markdown=metadata[0]["content_markdown"] + "\nProse only.\n")
        _rows, _scopes, _registered, _inverse, _state, delta = materialize_delta(
            [changed, metadata[1], source], [], state, {changed["source_path"]: changed},
        )
        self.assertIsNotNone(delta)

    def test_ordinary_change_parses_only_the_changed_source(self):
        untouched = _RelationReadProbe(relations={})
        first, second = atom("CA-P-1"), dict(atom("CA-P-2"), header_json=untouched)
        metadata = declarations()
        _, _, _, _, state, _ = materialize_delta(metadata + [first, second], [])
        self.assertGreater(untouched.reads, 0)
        untouched.reads = 0
        changed = _RelationReadProbe(relations={})
        first_changed = dict(first, header_json=changed, content_markdown="## Claim\nChanged.\n")

        _, _, _, _, _, delta = materialize_delta(
            metadata + [first_changed, second], [], state, {"CA-P-1.md": first_changed},
        )

        self.assertGreater(changed.reads, 0)
        self.assertEqual(0, untouched.reads)
        self.assertEqual({"CA-P-1.md"}, set(delta.new_atoms))

