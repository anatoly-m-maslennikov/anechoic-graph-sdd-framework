"""Source reader carrier and status cases."""

from . import test_source_reader as fixtures


class SourceReaderStatusCases:
    def test_status_groups_refs_and_archive_locations(self) -> None:
        sources, archived = self._status_sources()
        atoms, _scopes, stderr = self._capture()
        rows = {row["ref"]: row for row in atoms}

        self.assertEqual(stderr, "")
        self.assertEqual(
            {ref: rows[ref]["status_group"] for ref in sources},
            {
                "CA-R-201": "Current",
                "CA-R-202": "Current",
                "CA-R-203": "Current",
                "CA-R-204@7-draft": "Draft",
            },
        )
        self.assertEqual(
            set(rows),
            set(sources)
            | {"CA-R-205@1", "CA-R-206@1", "CA-R-207@1"}
            | {
                row["ref"]
                for row in atoms
                if row["form"] == "Scope Unit Declaration"
            },
        )
        self.assertEqual(
            {row["source_path"] for row in atoms}
            & {path.relative_to(self.root).as_posix() for path in archived},
            {path.relative_to(self.root).as_posix() for path in archived},
        )
        self.assertTrue(
            all(
                rows[f"CA-R-{number}@1"]["status_group"] == "Archived"
                for number in (205, 206, 207)
            )
        )

    def _status_sources(self):
        sources = {
            "CA-R-201": self._write_atom(
                "MAIN",
                "01_concern",
                "active.md",
                atom_id="CA-R-201",
                status="Active",
            ),
            "CA-R-202": self._write_atom(
                "MAIN",
                "02_analysis",
                "done.md",
                atom_id="CA-R-202",
                status="Done",
            ),
            "CA-R-203": self._write_atom(
                "MAIN",
                "03_plan",
                "canceled.md",
                atom_id="CA-R-203",
                status="Canceled",
            ),
            "CA-R-204@7-draft": self._write_atom(
                "MAIN",
                "04_requirement",
                "draft.md",
                atom_id="CA-R-204@7-draft",
                status="Draft",
                version=7,
                parts=("DRAFT",),
            ),
        }
        return sources, self._archived_sources()

    def _archived_sources(self):
        return (
            self._write_atom(
                "MAIN",
                "05_method",
                "archived-folder.md",
                atom_id="CA-R-205",
                parts=("ARCHIVE",),
            ),
            self._write_atom(
                "MAIN",
                "06_evaluation",
                "archived-nested.md",
                atom_id="CA-R-206",
                parts=("nested", "Archived"),
            ),
            self._write_atom(
                "MAIN",
                "07_delivery",
                "archived-status.md",
                atom_id="CA-R-207",
                status="archived",
            ),
        )

    def test_archived_carrier_keeps_historical_header_and_content_shape(
        self,
    ) -> None:
        self._write_atom(
            "MAIN",
            "04_requirement",
            "CA-R-704-DECLARATION.md",
            atom_id="CA-R-704",
            form="Declaration",
            body="""## Claim

### Formal Claim

```CFEL
Atom.Header.Tier:: [int]{::1};
Atom.Content.Summary{::1}:: {::1};
```
""",
        )
        archived = self._write_atom(
            "MAIN",
            "04_requirement",
            "CA-R-705@2-old.md",
            atom_id="CA-R-705",
            status="Archived",
            version=2,
            parts=("archive",),
            body="## Summary\n\nFirst.\n\n## Summary\n\nSecond.\n",
        )
        archived.write_text(
            archived.read_text().replace(
                "subjects: {}", "tier: principle\nsubjects: {}"
            )
        )
        reader = fixtures.SourceReader(self.root, schema_mode=1)
        rows, _ = reader.capture()
        (row,) = [row for row in rows if row["ref"] == "CA-R-705@2"]
        self.assertEqual("Archived", row["status_group"])
        self.assertEqual("principle", row["header_json"]["tier"])

    def test_implementation_role_accepts_current_and_draft_carriers(
        self,
    ) -> None:
        current = self._write_atom(
            "MAIN",
            "08_implementation",
            "CA-I-801-current.md",
            atom_id="CA-I-801",
        )
        draft = self._write_atom(
            "MAIN",
            "08_implementation",
            "CA-I-draft-next.md",
            atom_id="CA-I-draft",
            status="Draft",
            parts=("draft",),
        )

        atoms, _scopes, stderr = self._capture()
        by_path = {row["source_path"]: row for row in atoms}

        self.assertEqual("", stderr)
        self.assertEqual(
            "Current",
            by_path[current.relative_to(self.root).as_posix()]["status_group"],
        )
        self.assertEqual(
            "Draft",
            by_path[draft.relative_to(self.root).as_posix()]["status_group"],
        )

    def test_role_only_drafts_keep_distinct_technical_references(self) -> None:
        drafts = (
            self._write_atom(
                "MAIN",
                "09_operations",
                "CA-O-draft-first.md",
                atom_id="CA-O-draft",
                status="Draft",
                parts=("draft",),
            ),
            self._write_atom(
                "MAIN",
                "09_operations",
                "CA-O-draft-second.md",
                atom_id="CA-O-draft",
                status="Draft",
                parts=("draft",),
            ),
        )

        atoms, scopes, stderr = self._capture()
        rows = [
            row
            for row in atoms
            if row["source_path"]
            in {path.relative_to(self.root).as_posix() for path in drafts}
        ]
        materialized, _scopes = fixtures.materialize(atoms, scopes)

        self.assertEqual(stderr, "")
        self.assertEqual(
            {row["ref"] for row in rows},
            {
                f"CA-O-draft:{path.relative_to(self.root).as_posix()}"
                for path in drafts
            },
        )
        self.assertEqual(
            {row["source_path"] for row in materialized}
            & {path.relative_to(self.root).as_posix() for path in drafts},
            {path.relative_to(self.root).as_posix() for path in drafts},
        )

    def test_other_project_and_legacy_role_markers_are_not_current_atom_filenames(
        self,
    ) -> None:
        legacy_concern = self._path(
            "fixture", "01_concern", "ANECHOIC-CONC-004--legacy.md"
        )
        legacy_concern.write_text(
            (
                "---\natom_id: ANECHOIC-CONC-004\nversion: 1\n---\n# Legacy "
                "concern\n"
            ),
            encoding="utf-8",
        )
        legacy_analysis = self._path(
            "fixture", "02_analysis", "ANECHOIC-ANRP-003--legacy.md"
        )
        legacy_analysis.write_text(
            (
                "---\natom_id: ANECHOIC-ANRP-003\nversion: 2\n---\n# Legacy "
                "analysis\n"
            ),
            encoding="utf-8",
        )
        draft = self._path(
            "fixture",
            "04_requirement",
            "ANECHOIC-REQU-DRAFT--legacy.md",
            "drafts",
        )
        draft.write_text(
            "---\nversion: 1\n---\n# Legacy draft\n", encoding="utf-8"
        )

        atoms, _scopes, stderr = self._capture()
        paths = {row["source_path"] for row in atoms}

        self.assertEqual(stderr, "")
        self.assertNotIn(
            legacy_concern.relative_to(self.root).as_posix(), paths
        )
        self.assertNotIn(
            legacy_analysis.relative_to(self.root).as_posix(), paths
        )
        self.assertNotIn(draft.relative_to(self.root).as_posix(), paths)
