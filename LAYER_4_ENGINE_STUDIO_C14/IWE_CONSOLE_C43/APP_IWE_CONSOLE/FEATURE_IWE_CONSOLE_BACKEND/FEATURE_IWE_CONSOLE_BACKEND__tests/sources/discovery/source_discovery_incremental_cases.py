"""Source discovery incremental test cases."""

from unittest.mock import patch


class SourceDiscoveryIncrementalCases:
    def test_generated_copies_stay_excluded_during_incremental_changes(self):
        source = self.source("loose/current.md", "CA-R-789")
        self.fixture._capture()
        for directory in ("000_ANECHOIC_framework", "_projection"):
            copy = self.control / directory / "nested" / source.name
            copy.parent.mkdir(parents=True, exist_ok=True)
            copy.write_bytes(source.read_bytes())
            for changed in (copy, copy.parent):
                rows, _ = self.reader.capture(
                    [
                        {
                            "operation": "create",
                            "old_path": None,
                            "new_path": changed.relative_to(
                                self.root
                            ).as_posix(),
                        }
                    ]
                )
                self.assertEqual(
                    [source.relative_to(self.root).as_posix()],
                    [
                        row["source_path"]
                        for row in rows
                        if row["ref"] == "CA-R-789"
                    ],
                )
        rows, _, _ = self.fixture._capture()
        self.assertEqual(
            [source.relative_to(self.root).as_posix()],
            [row["source_path"] for row in rows if row["ref"] == "CA-R-789"],
        )

    def test_orphan_source_lifecycle_does_not_rescan_scope_or_atom_inventory(
        self,
    ):
        self.source("loose/seed.md", "CA-R-790")
        self.fixture._capture()
        source = self.source("new-owner/entry.md", "CA-R-791")
        with (
            patch.object(
                self.reader,
                "_inventory_paths",
                side_effect=AssertionError("unexpected full scan"),
            ),
            self.fixture.source_reads() as reads,
        ):
            self.assertIn(
                "CA-R-791",
                {
                    row["id"]
                    for row in self._capture_change("create", new=source)
                },
            )
            source.write_text(
                source.read_text().replace("version: 1", "version: 2")
            )
            rows = self._capture_change("update", new=source)
            self.assertEqual(
                2,
                next(row for row in rows if row["id"] == "CA-R-791")[
                    "version"
                ],
            )
            self._move_and_remove_orphan(source)
        self.assertTrue(self.fixture.declaration_paths().isdisjoint(reads))

    def _move_and_remove_orphan(self, source):
        renamed = source.with_name("CA-R-791-renamed.md")
        source.rename(renamed)
        rows = self._capture_change("rename", source, renamed)
        moved = self.control / "other-owner" / renamed.name
        moved.parent.mkdir()
        renamed.rename(moved)
        rows = self._capture_change("move", renamed, moved)
        self.assertIn(
            moved.relative_to(self.root).as_posix(),
            {row["source_path"] for row in rows},
        )
        self.assertNotIn(
            source.relative_to(self.root).as_posix(),
            {row["source_path"] for row in rows},
        )
        moved.unlink()
        self.assertNotIn(
            "CA-R-791",
            {row["id"] for row in self._capture_change("remove", old=moved)},
        )
        self._capture_change("create", new=self.root / "outside.md")
        self.assertFalse(self.reader.capture_changed)

    def _capture_change(self, operation, old=None, new=None):
        return self.reader.capture(
            [
                {
                    "operation": operation,
                    "old_path": old.relative_to(self.root).as_posix()
                    if old
                    else None,
                    "new_path": new.relative_to(self.root).as_posix()
                    if new
                    else None,
                }
            ]
        )[0]

    def test_archiving_and_duplicate_deltas_keep_each_carrier(self):
        original = self.source("loose/current.md", "CA-R-790")
        duplicate = self.source("copy/current.md", "CA-R-790")
        ordered = self.source("ordered/entry.md", "CA-R-792")
        numbered = ordered.with_name("3-" + ordered.name)
        ordered.rename(numbered)
        rows, _, _ = self.fixture._capture()
        self.assertEqual(2, sum(row["ref"] == "CA-R-790" for row in rows))
        self.assertIn(
            numbered.relative_to(self.root).as_posix(),
            {row["source_path"] for row in rows},
        )

        archive = self.control / "loose" / "099_archived" / "CA-R-790@1-old.md"
        archive.parent.mkdir()
        original.write_text(
            original.read_text().replace(
                'status: "Active"', 'status: "Archived"'
            )
        )
        original.rename(archive)
        rows, _ = self.reader.capture(
            [
                {
                    "operation": "move",
                    "old_path": original.relative_to(self.root).as_posix(),
                    "new_path": archive.relative_to(self.root).as_posix(),
                }
            ]
        )
        self._assert_archived_carriers(rows, original, duplicate, archive)

    def _assert_archived_carriers(self, rows, original, duplicate, archive):
        selected = {
            row["source_path"]: row for row in rows if row["id"] == "CA-R-790"
        }
        self.assertEqual(
            {
                duplicate.relative_to(self.root).as_posix(),
                archive.relative_to(self.root).as_posix(),
            },
            set(selected),
        )
        self.assertEqual(
            "CA-R-790@1",
            selected[archive.relative_to(self.root).as_posix()]["ref"],
        )
        self.assertEqual(
            "Archived",
            selected[archive.relative_to(self.root).as_posix()][
                "status_group"
            ],
        )
        self.assertIsNone(
            self.reader.capture_delta[
                original.relative_to(self.root).as_posix()
            ]
        )
        self.assertEqual(
            "CA-R-790@1",
            self.reader.capture_delta[
                archive.relative_to(self.root).as_posix()
            ]["ref"],
        )

    def test_filename_marker_defines_atoms_instead_of_yaml_or_role_folder(
        self,
    ):
        current = self.source("02_analysis/record.md", "CA-R-798")
        plain = current.with_name("ordinary.md")
        plain.write_bytes(
            current.read_bytes().replace(b"CA-R-798", b"CA-R-799")
        )
        foreign = current.with_name("OTHER-R-800-record.md")
        foreign.write_bytes(
            current.read_bytes().replace(b"CA-R-798", b"OTHER-R-800")
        )
        broken = current.with_name("CA-R-801-broken.md")
        broken.write_text("---\nrole: [invalid\n---\n")
        atoms, _, diagnostics = self.fixture._capture()
        self.assertIn(
            current.relative_to(self.root).as_posix(),
            {row["source_path"] for row in atoms},
        )
        self.assertNotIn("CA-R-799", {row["id"] for row in atoms})
        self.assertNotIn("OTHER-R-800", {row["id"] for row in atoms})
        self.assertIn(str(broken), diagnostics)

    def test_new_method_delegation_refreshes_the_structural_source_pins(self):
        self.fixture._capture()
        parent = self.reader._declarations.by_name["MAIN"]
        source = self.fixture._write_atom(
            "MAIN",
            "05_method",
            "CA-M-803-delegation.md",
            atom_id="CA-M-803",
            form="Scope Delegation",
            body="## Claim\n\n### Prose Claim\n\nDeliver the child capability.\n",
        )
        raw = source.read_text().replace(
            'role: "Requirement"', 'role: "Method"'
        )
        raw = raw.replace(
            "subjects: {}",
            f"container:\n  scope_unit: {parent.scope_unit_id}\n"
            "topics:\n  main_subject: Scope Unit//CHILD",
        )
        source.write_text(raw)
        atoms, scopes = self.reader.capture(
            [
                {
                    "operation": "create",
                    "old_path": None,
                    "new_path": source.relative_to(self.root).as_posix(),
                }
            ]
        )
        self.assertIn("CA-M-803", {row["id"] for row in atoms})
        self.assertEqual(
            {"fixture", "MAIN", "CHILD"}, {row["name"] for row in scopes}
        )
        self.assertEqual(
            [source.resolve()],
            [
                item.source
                for item in self.reader._declarations.by_name[
                    "CHILD"
                ].delegations
            ],
        )
        self._assert_delegation_pin(source)

    def _assert_delegation_pin(self, source):
        self.assertIn(
            source.relative_to(self.root).as_posix(),
            self.reader._declarations.source_pins,
        )
