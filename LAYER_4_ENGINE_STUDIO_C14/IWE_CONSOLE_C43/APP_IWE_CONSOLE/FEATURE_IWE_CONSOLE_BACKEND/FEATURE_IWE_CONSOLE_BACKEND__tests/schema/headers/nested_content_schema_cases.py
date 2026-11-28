"""Content schema cases for nested header reading."""

from unittest import mock

from KERNEL_MIXER_C59 import content_schema as content_schema_module

SUMMARY_RULE = 'property_rule(address="Atom.Content.Summary", occurrences="1", values="1")'


class NestedContentSchemaCases:
    def test_declared_content_duplicates_are_excluded_but_arbitrary_headings_remain_raw(
        self,
    ) -> None:
        self._model_declaration("content-model.md", "CA-R-401", SUMMARY_RULE)
        self._nested(
            "valid.md",
            "CA-R-402",
            body="# Summary\n\nOne\n\n## Arbitrary heading\n\nTwo\n",
        )
        self._nested(
            "duplicate.md",
            "CA-R-403",
            body="# Summary\n\nOne\n\n# Summary\n\nTwo\n",
        )

        atoms, _scopes = self.reader.capture()

        ids = {row["id"] for row in atoms}
        self.assertIn("CA-R-401", ids)
        self.assertIn("CA-R-402", ids)
        self.assertNotIn("CA-R-403", ids)
        self.assertEqual(
            ("content.summary",), self.reader._content_schema.schema.names
        )
        self.assertEqual(1, self.reader.excluded_count)

    def test_content_model_change_rebuilds_the_cached_schema(self) -> None:
        declaration = self._model_declaration(
            "content-model.md", "CA-R-404", SUMMARY_RULE
        )
        self._nested(
            "duplicate.md",
            "CA-R-405",
            body="# Summary\n\nOne\n\n# Summary\n\nTwo\n",
        )
        first, _scopes = self.reader.capture()
        self.assertNotIn("CA-R-405", {row["id"] for row in first})
        self._model_declaration(
            "content-model.md",
            "CA-R-404",
            'property_rule(address="Atom.Content.Title", occurrences="1", values="1")',
        )

        atoms, _scopes = self.reader.capture(
            [
                {
                    "operation": "update",
                    "old_path": None,
                    "new_path": declaration.relative_to(self.root).as_posix(),
                }
            ]
        )

        self.assertEqual(
            ("content.title",), self.reader._content_schema.schema.names
        )
        self.assertIn("CA-R-405", {row["id"] for row in atoms})

    def test_ordinary_update_uses_the_cached_content_schema(self) -> None:
        source = self._nested("ordinary.md", "CA-R-406")
        self.reader.capture()
        self._nested("ordinary.md", "CA-R-406", body="# Summary\n\nUpdated.\n")

        with (
            mock.patch.object(
                self.reader,
                "_capture_full",
                side_effect=AssertionError("full capture"),
            ),
            mock.patch.object(
                content_schema_module,
                "compile_content_schema",
                side_effect=AssertionError("all source compile"),
            ),
        ):
            atoms, _scopes = self.reader.capture(
                [
                    {
                        "operation": "update",
                        "old_path": None,
                        "new_path": source.relative_to(self.root).as_posix(),
                    }
                ]
            )

        self.assertIn("CA-R-406", {row["id"] for row in atoms})
        self.assertEqual(
            "CA-R-406",
            self.reader.capture_delta[
                source.relative_to(self.root).as_posix()
            ]["id"],
        )

    def test_same_shape_declaration_update_refreshes_schema_provenance_without_full_capture(
        self,
    ) -> None:
        declaration = self._model_declaration(
            "content-model.md", "CA-R-407", SUMMARY_RULE
        )
        self.reader.capture()
        declaration.write_text(
            declaration.read_text(encoding="utf-8").replace(
                "version: 3", "version: 4"
            ),
            encoding="utf-8",
        )

        with mock.patch.object(
            self.reader,
            "_capture_full",
            side_effect=AssertionError("full capture"),
        ):
            self.reader.capture(
                [
                    {
                        "operation": "update",
                        "old_path": None,
                        "new_path": declaration.relative_to(
                            self.root
                        ).as_posix(),
                    }
                ]
            )

        source = next(
            item
            for item in self.reader.content_schema.sources
            if item.reference == "CA-R-407"
        )
        self.assertEqual(4, source.version)

    def test_role_filter_change_and_declaration_removal_rebuild_content_schema(
        self,
    ) -> None:
        declaration = self._model_declaration(
            "content-model.md", "CA-R-408", SUMMARY_RULE
        )
        self.reader.capture()
        self._model_declaration(
            "content-model.md",
            "CA-R-408",
            'property_rule(address="Atom/(.Header.Role := Plan).Content.Summary", occurrences="1", values="1")',
        )

        with mock.patch.object(
            self.reader, "_capture_full", wraps=self.reader._capture_full
        ) as full:
            self.reader.capture(
                [
                    {
                        "operation": "update",
                        "old_path": None,
                        "new_path": declaration.relative_to(
                            self.root
                        ).as_posix(),
                    }
                ]
            )
        self.assertEqual(1, full.call_count)
        declaration.unlink()
        with mock.patch.object(
            self.reader, "_capture_full", wraps=self.reader._capture_full
        ) as full:
            self.reader.capture(
                [
                    {
                        "operation": "remove",
                        "old_path": declaration.relative_to(
                            self.root
                        ).as_posix(),
                        "new_path": None,
                    }
                ]
            )
        self.assertEqual(1, full.call_count)

    def test_invalid_incremental_source_has_a_none_delta_entry(self) -> None:
        self._model_declaration("content-model.md", "CA-R-409", SUMMARY_RULE)
        source = self._nested("invalid.md", "CA-R-410")
        self.reader.capture()
        self._nested(
            "invalid.md",
            "CA-R-410",
            body="# Summary\n\nOne\n\n# Summary\n\nTwo\n",
        )

        self.reader.capture(
            [
                {
                    "operation": "update",
                    "old_path": None,
                    "new_path": source.relative_to(self.root).as_posix(),
                }
            ]
        )

        self.assertIsNone(
            self.reader.capture_delta[source.relative_to(self.root).as_posix()]
        )

    def test_duplicate_model_definition_keeps_first_and_admits_repaired_copy(
        self,
    ) -> None:
        first = self._model_declaration(
            "first-model.md", "CA-R-411", SUMMARY_RULE
        )
        duplicate = self._model_declaration(
            "duplicate-model.md", "CA-R-411", SUMMARY_RULE
        )
        self.reader.capture()
        self.assertEqual(
            ("content.summary",), self.reader.content_schema.names
        )
        self.assertEqual(1, len(self.reader.content_schema.sources))
        duplicate.write_text(
            duplicate.read_text(encoding="utf-8").replace(
                "CA-R-411", "CA-R-412"
            ),
            encoding="utf-8",
        )

        with mock.patch.object(
            self.reader, "_capture_full", wraps=self.reader._capture_full
        ) as full:
            self.reader.capture(
                [
                    {
                        "operation": "update",
                        "old_path": None,
                        "new_path": duplicate.relative_to(
                            self.root
                        ).as_posix(),
                    }
                ]
            )

        self.assertEqual(0, full.call_count)
        self.assertEqual(
            ("content.summary",), self.reader.content_schema.names
        )
        self.assertEqual(2, len(self.reader.content_schema.sources))
        self.assertTrue(first.is_file())
