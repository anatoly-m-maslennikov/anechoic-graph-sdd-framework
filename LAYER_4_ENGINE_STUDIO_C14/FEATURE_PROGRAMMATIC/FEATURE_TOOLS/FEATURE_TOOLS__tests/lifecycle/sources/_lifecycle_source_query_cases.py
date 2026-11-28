"""Lifecycle source selection scenarios."""

import os
from pathlib import Path
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources import (
    source__shared as source_module,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.source__shared import (
    select_source,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.source_binding import (
    SourceSelectionError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.placement._placement_paths import (
    _predecessor_status,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.placement.placement__shared import (
    _role_root,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.units.scope_unit_declarations__pub import (
    read_scope_unit_declarations,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_read__pub import (
    parse_carrier,
)


class IndexedReader:
    def __init__(self, selection, rows):
        self.rows = rows
        self.declarations = read_scope_unit_declarations(
            selection.root, selection.control_relative
        )
        self.calls = []

    def lifecycle_candidates(
        self, selection, *, atom_ids=(), prefix=None, under=None, references=()
    ):
        self.calls.append((atom_ids, prefix, under, references))
        return [
            (atom_id, path)
            for atom_id, path in self.rows
            if (not atom_ids or atom_id in atom_ids)
            and (prefix is None or atom_id.startswith(prefix))
            and (under is None or path.is_relative_to(under))
        ]

    def lifecycle_read(self, path, *, descriptor=None):
        if descriptor is not None:
            return os.pread(descriptor, os.fstat(descriptor).st_size, 0)
        return path.read_bytes()

    def lifecycle_contexts(self, selection, ref_id):
        contexts = []
        for identity, path in self.rows:
            if identity == ref_id:
                parse_carrier(path.read_bytes(), path)
        return contexts

    def lifecycle_last_id(self, selection, prefix, *, ceiling=None):
        ids = (
            atom_id
            for atom_id, _ in self.lifecycle_candidates(
                selection, prefix=prefix
            )
        )
        return max(
            (
                atom_id
                for atom_id in ids
                if ceiling is None or int(atom_id[len(prefix) :]) <= ceiling
            ),
            key=lambda atom_id: int(atom_id[len(prefix) :]),
            default=None,
        )

    def lifecycle_declarations(self):
        return self.declarations


class QueryCases:
    def test_query_reader_binds_exact_and_batch_sources_without_inventory(
        self,
    ):
        current = self.carrier("CA-R-10-example.md", version=2)
        archived = self.carrier("CA-R-10@1-example.md", status="Archived")
        draft = self.carrier(
            "CA-R-11@3-draft-example.md",
            identity="CA-R-11",
            version=3,
            status="Draft",
        )
        indexed = IndexedReader(
            self.selection,
            [("CA-R-10", current), ("CA-R-10", archived), ("CA-R-11", draft)],
        )
        with (
            source_module.bind_query_reader(indexed),
            patch.object(
                source_module,
                "_inventory_paths",
                side_effect=AssertionError("unexpected scan"),
            ),
            patch.object(
                source_module,
                "read_scope_unit_declarations",
                side_effect=AssertionError("unexpected read"),
            ),
        ):
            self.assertEqual(
                select_source(self.selection, "CA-R-10").path, current
            )
            pins = source_module.select_sources(
                self.selection, ["CA-R-10@1", "CA-R-11@3-draft"]
            )
            self.assertEqual(
                (pins["CA-R-10@1"].path, pins["CA-R-11@3-draft"].path),
                (archived, draft),
            )
            self.assertEqual(
                _predecessor_status(current, "CA-R-10", 2), "active"
            )
            _role_root(self.selection, "Requirement", "TEST")
        self.assertIsNone(source_module.query_reader())

    def test_query_reader_rejects_outside_paths(self):
        indexed = IndexedReader(
            self.selection, [("CA-R-10", Path("/outside/CA-R-10-example.md"))]
        )
        with (
            source_module.bind_query_reader(indexed),
            self.assertRaises(SourceSelectionError),
        ):
            select_source(self.selection, "CA-R-10")

    def test_query_reader_requests_exact_references_for_single_and_batch_reads(
        self,
    ):
        current = self.carrier("CA-R-10-current.md", version=2)
        archived = self.carrier(
            "CA-R-10@1-archive.md",
            status="Archived",
            folder=self.folder / "099_archived",
        )
        misleading = self.carrier(
            "CA-R-10-old.md",
            status="Active",
            folder=self.folder / "099_archived",
        )
        indexed = IndexedReader(
            self.selection,
            [("CA-R-10", path) for path in (current, archived, misleading)],
        )
        queries = []

        def exact(selection, *, atom_ids=(), references=()):
            queries.append((atom_ids, references))
            paths = {"CA-R-10": current, "CA-R-10@1": archived}
            return [("CA-R-10", paths[reference]) for reference in references]

        indexed.lifecycle_candidates = exact
        with source_module.bind_query_reader(indexed):
            self.assertEqual(
                current, select_source(self.selection, "CA-R-10").path
            )
            pins = source_module.select_sources(
                self.selection, ["CA-R-10", "CA-R-10@1"]
            )
        self.assertEqual(current, pins["CA-R-10"].path)
        self.assertEqual(archived, pins["CA-R-10@1"].path)
        self.assertEqual(
            [
                (("CA-R-10",), ("CA-R-10",)),
                (("CA-R-10",), ("CA-R-10",)),
                (("CA-R-10",), ("CA-R-10@1",)),
            ],
            queries,
        )

    def _competing_index(self):
        current = self.carrier("CA-R-10-a.md", version=1)
        duplicate = self.carrier("CA-R-10-b.md", version=2)
        archived = self.carrier("CA-R-10@1-a.md", status="Archived")
        archived_copy = self.carrier("CA-R-10@1-b.md", status="Archived")
        draft = self.carrier("CA-R-10@3-draft-a.md", version=3, status="Draft")
        draft_copy = self.carrier(
            "CA-R-10@3-draft-b.md", version=3, status="Draft"
        )
        indexed = IndexedReader(
            self.selection,
            [
                ("CA-R-10", path)
                for path in (
                    current,
                    duplicate,
                    archived,
                    archived_copy,
                    draft,
                    draft_copy,
                )
            ],
        )
        return indexed

    def test_query_reader_rejects_competing_carriers_before_read(self):
        indexed = self._competing_index()
        with (
            source_module.bind_query_reader(indexed),
            patch.object(
                indexed,
                "lifecycle_read",
                side_effect=AssertionError("unexpected read"),
            ),
        ):
            for ref, version in [
                ("CA-R-10", None),
                ("CA-R-10", 2),
                ("CA-R-10@1", None),
                ("CA-R-10@3-draft", None),
            ]:
                with (
                    self.subTest(ref=ref, version=version),
                    self.assertRaisesRegex(SourceSelectionError, "ambiguous"),
                ):
                    select_source(
                        self.selection, ref, expected_version=version
                    )
            with self.assertRaisesRegex(SourceSelectionError, "ambiguous"):
                source_module.select_sources(
                    self.selection, ["CA-R-10@1", "CA-R-10@3-draft"]
                )

    def test_query_reader_does_not_skip_stale_selected_carrier(self):
        current = self.carrier("CA-R-10-a.md", identity="CA-R-11")
        indexed = IndexedReader(self.selection, [("CA-R-10", current)])
        with (
            source_module.bind_query_reader(indexed),
            patch.object(
                indexed, "lifecycle_read", wraps=indexed.lifecycle_read
            ) as read,
        ):
            with self.assertRaises(SourceSelectionError):
                select_source(self.selection, "CA-R-10")
            self.assertEqual(1, read.call_count)
