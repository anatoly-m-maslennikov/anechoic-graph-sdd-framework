"""Incremental relation cache cases."""

from unittest.mock import patch

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import compile_registry

from ....FEATURE_IWE_CONSOLE_BACKEND__shared import materialize_delta
from ..relations.test_relations import atom, declarations


class IncrementalRelationCacheCases:
    def test_unique_deleted_sources_leave_no_relation_cache_keys(self):
        sources = declarations() + [atom("CA-P-100")]
        _rows, _scopes, _registered, _inverse, state, _delta = (
            materialize_delta(sources, [])
        )
        baseline = dict(state.outgoing)
        for number in range(200, 220):
            row = atom(
                f"CA-P-{number}", relation={"IS_CONTAINED_BY": ["CA-P-100"]}
            )
            _rows, _scopes, _registered, _inverse, state, _delta = (
                materialize_delta(
                    sources + [row],
                    [],
                    state,
                    {row["source_path"]: row},
                )
            )
            rows, _scopes, _registered, _inverse, state, delta = (
                materialize_delta(
                    sources,
                    [],
                    state,
                    {row["source_path"]: None},
                )
            )
            self.assertEqual(baseline, state.outgoing)
            self.assertIn("CA-P-100.md", delta.new_atoms)
            self.assertIn(row["source_path"], delta.old_atoms)
            self.assertNotIn(row["source_path"], delta.new_atoms)
            target = next(item for item in rows if item["ref"] == "CA-P-100")
            self.assertEqual([], target["relation_edges_json"])

    def test_relation_cache_keeps_other_children_until_last_delete(self):
        sources = declarations() + [atom("CA-P-100")]
        _rows, _scopes, _registered, _inverse, state, _delta = (
            materialize_delta(sources, [])
        )
        children = [
            atom(f"CA-P-{number}", relation={"IS_CONTAINED_BY": ["CA-P-100"]})
            for number in range(200, 203)
        ]
        for child in children:
            sources.append(child)
            _rows, _scopes, _registered, _inverse, state, _delta = (
                materialize_delta(
                    sources,
                    [],
                    state,
                    {child["source_path"]: child},
                )
            )
        for index, child in enumerate(children):
            sources.remove(child)
            rows, _scopes, _registered, _inverse, state, _delta = (
                materialize_delta(
                    sources,
                    [],
                    state,
                    {child["source_path"]: None},
                )
            )
            target = next(item for item in rows if item["ref"] == "CA-P-100")
            self.assertEqual(2 - index, len(target["relation_edges_json"]))
            self.assertTrue(all(state.outgoing.values()))
        self.assertEqual({}, state.outgoing)

    def test_change_updates_source_and_inverse_neighbours_only(self):
        old = atom("CA-P-1")
        new = atom("CA-P-3")
        task = atom("CA-P-2", relation={"is_contained_by": ["CA-P-1"]})
        rows, _scopes, _registered, _inverse, state, delta = materialize_delta(
            declarations() + [old, task, new], []
        )
        self.assertIsNone(delta)
        changed = atom("CA-P-2", relation={"is_contained_by": ["CA-P-3"]})
        rows, _scopes, _registered, _inverse, state, delta = materialize_delta(
            declarations() + [old, changed, new],
            [],
            state,
            {"CA-P-2.md": changed},
        )
        self.assertEqual(
            {"CA-P-1.md", "CA-P-2.md", "CA-P-3.md"}, set(delta.old_atoms)
        )
        self.assertEqual(set(delta.old_atoms), set(delta.new_atoms))
        by_ref = {row["ref"]: row for row in rows}
        self.assertEqual([], by_ref["CA-P-1"]["relation_edges_json"])
        self.assertEqual(
            "CONTAINS",
            by_ref["CA-P-3"]["relation_edges_json"][0]["relation_type"],
        )

    def test_static_registry_survives_changes_and_full_rebuild_without_compilation(
        self,
    ):
        metadata = declarations()
        registry = compile_registry(metadata).registry
        source = atom("CA-P-100")
        changed = atom("CA-P-100", relation={"IS_CONTAINED_BY": ["CA-P-200"]})
        module = (
            "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.incre"
            "mental_relation_state"
        )
        with (
            patch(
                f"{module}.compile_registry",
                side_effect=AssertionError("compiled"),
            ),
            patch(
                f"{module}.registry_contribution",
                side_effect=AssertionError("compiled contribution"),
            ),
        ):
            _, _, _, _, state, _ = materialize_delta(
                metadata + [source], [], registry=registry
            )
            _, _, _, _, state, delta = materialize_delta(
                metadata + [changed],
                [],
                state,
                {source["source_path"]: changed},
            )
            self.assertIsNotNone(delta)
            _, _, names, inverse, state, delta = materialize_delta(
                metadata + [changed], [], state, None
            )
            self.assertIsNone(delta)
            self.assertEqual(registry.names, names)
            self.assertEqual(registry.inverse, inverse)
            self.assertTrue(state.static_registry)
