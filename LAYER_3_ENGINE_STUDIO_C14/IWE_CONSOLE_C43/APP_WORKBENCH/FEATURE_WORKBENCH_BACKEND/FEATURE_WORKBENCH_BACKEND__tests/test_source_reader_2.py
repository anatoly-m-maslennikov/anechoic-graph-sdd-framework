from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch


APP_ROOT = Path(__file__).resolve().parents[3]
TOOLS_ROOT = APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.markdown_content__pub import source_markdown  # noqa: E402
from KERNEL_MIXER_C59.header_columns import infer_header_schema  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_reader import SourceReader  # noqa: E402




from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests._source_reader_fixture import SourceReaderFixture  # noqa: E402


class SourceReaderTests(SourceReaderFixture, unittest.TestCase):
    def test_unrepresentable_convenience_integer_keeps_the_full_header_value(self) -> None:
        value = 2**100
        source = self._write_atom("MAIN", "04_requirement", "wide.md", atom_id="CA-R-900", version=value)
        source.write_text(source.read_text().replace("subjects: {}", f"tier: {value}\nsubjects: {{}}"))
        atoms, _scopes, stderr = self._capture()
        row = next(row for row in atoms if row["id"] == "CA-R-900")
        self.assertEqual("", stderr)
        self.assertIsNone(row["version"])
        self.assertIsNone(row["tier"])
        self.assertEqual(value, row["header_json"]["version"])
        self.assertEqual(value, row["header_json"]["tier"])


    def test_mode_one_excludes_only_ordinary_declared_header_format_errors(self) -> None:
        declaration = self._write_atom(
            "MAIN", "04_requirement", "CA-R-701-MAIN-DECLARATION--header.md",
            atom_id="CA-R-701", form="Declaration", body="""## Claim

### Formal Claim

~~~CFEL
Atom.Header.Tier:: [int]{::1};
~~~
""",
        )
        bad = self._write_atom("MAIN", "04_requirement", "bad.md", atom_id="CA-R-BAD")
        good = self._write_atom("MAIN", "04_requirement", "good.md", atom_id="CA-R-GOOD")
        for path, value in ((bad, "principle"), (good, "1")):
            path.write_text(
                path.read_text(encoding="utf-8").replace("subjects: {}", f"tier: {value}\nsubjects: {{}}"),
                encoding="utf-8",
            )
        reader = SourceReader(self.root, schema_mode=1)
        stderr = StringIO()
        with redirect_stderr(stderr):
            atoms, _scopes = reader.capture()
        refs = {row["ref"] for row in atoms}
        self.assertIn("CA-R-GOOD", refs)
        self.assertNotIn("CA-R-BAD", refs)
        self.assertIn("header.context.tier requires BIGINT", stderr.getvalue())
        with redirect_stderr(StringIO()) as repeated:
            reader.capture()
        self.assertEqual("", repeated.getvalue())
        declaration.write_text(
            declaration.read_text(encoding="utf-8").replace("subjects: {}", "tier: principle\nsubjects: {}"),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "CA-R-701.*requires BIGINT"):
            reader.capture([{
                "operation": "update", "old_path": None,
                "new_path": declaration.relative_to(self.root).as_posix(),
            }])


    def test_mode_two_header_declaration_shape_change_stays_incremental(self) -> None:
        declaration = self._write_atom(
            "MAIN", "04_requirement", "CA-R-702-MAIN-DECLARATION--header.md",
            atom_id="CA-R-702", form="Declaration", body="""## Claim

### Formal Claim

~~~CFEL
Atom.Header.Tier:: [int]{::1};
~~~
""",
        )
        before, _scopes, _stderr = self._capture()
        before_shape = infer_header_schema(before).shape
        declaration.write_text(
            declaration.read_text(encoding="utf-8").replace(
                "Atom.Header.Tier:: [int]{::1};",
                "Atom.Header.Tier:: [int]{::1};\nAtom.Header.Declared Later:: [string]{::0..1};",
            ),
            encoding="utf-8",
        )
        event = {
            "operation": "update", "old_path": None,
            "new_path": declaration.relative_to(self.root).as_posix(),
        }
        with patch.object(self.reader, "_capture_full", wraps=self.reader._capture_full) as full:
            after, _scopes = self.reader.capture([event])
        self.assertFalse(full.called)
        self.assertEqual(before_shape, infer_header_schema(after).shape)
        self.assertIsNotNone(self.reader.capture_delta)


    def test_ordinary_delta_does_not_copy_or_enumerate_cached_rows(self) -> None:
        sources = [
            self._write_atom("MAIN", "04_requirement", f"ordinary-{index}.md", atom_id=f"CA-R-{710 + index}")
            for index in range(12)
        ]
        self.reader.capture()
        changed = sources[0]
        changed.write_text(changed.read_text(encoding="utf-8").replace("version: 1", "version: 2"), encoding="utf-8")

        class NoEnumeration(dict):
            def keys(self):
                raise AssertionError("incremental capture enumerated the cache")

            def __iter__(self):
                raise AssertionError("incremental capture enumerated the cache")

            def items(self):
                raise AssertionError("incremental capture enumerated the cache")

        self.reader._cached = NoEnumeration(self.reader._cached)
        event = {"operation": "update", "old_path": None, "new_path": changed.relative_to(self.root).as_posix()}
        with patch.object(self.reader, "_cached_rows", side_effect=AssertionError("whole-cache rows")):
            rows, _ = self.reader.capture([event])
        self.assertEqual(2, next(row["version"] for row in rows if row["id"] == "CA-R-710"))
        self.assertEqual({changed.relative_to(self.root).as_posix()}, set(self.reader.capture_delta))


    def test_mode_one_delta_validates_only_changed_header_rows(self) -> None:
        self._write_atom(
            "MAIN", "04_requirement", "CA-R-703-MAIN-DECLARATION--header.md",
            atom_id="CA-R-703", form="Declaration", body="""## Claim

### Formal Claim

~~~CFEL
Atom.Header.Tier:: [int]{::1};
~~~
""",
        )
        sources = [
            self._write_atom("MAIN", "04_requirement", f"ordinary-{index}.md", atom_id=f"CA-R-{710 + index}")
            for index in range(12)
        ]
        for source in sources:
            source.write_text(
                source.read_text(encoding="utf-8").replace("subjects: {}", "tier: 1\nsubjects: {}"),
                encoding="utf-8",
            )
        reader = SourceReader(self.root, schema_mode=1)
        reader.capture()
        changed = sources[0]
        changed.write_text(
            changed.read_text(encoding="utf-8").replace("version: 1", "version: 2"),
            encoding="utf-8",
        )
        event = {"operation": "update", "old_path": None, "new_path": changed.relative_to(self.root).as_posix()}
        with patch.object(
            reader._header_schema, "validation_errors", wraps=reader._header_schema.validation_errors,
        ) as validation:
            reader.capture([event])
        validated = validation.call_args.args[0]
        self.assertEqual(1, validation.call_count)
        self.assertEqual([changed.relative_to(self.root).as_posix()], [row["source_path"] for row in validated])
        self.assertGreater(len(reader._accepted_rows()), len(validated))


    def test_mode_one_validates_newly_admitted_duplicate_partner(self) -> None:
        self._write_atom(
            "MAIN", "04_requirement", "CA-R-704-MAIN-DECLARATION--header.md",
            atom_id="CA-R-704", form="Declaration", body="""## Claim

### Formal Claim

~~~CFEL
Atom.Header.Tier:: [int]{::1};
~~~
""",
        )
        first = self._write_atom("MAIN", "04_requirement", "CA-R-900-one.md", atom_id="CA-R-900")
        survivor = self._write_atom("MAIN", "04_requirement", "CA-R-900-two.md", atom_id="CA-R-900")
        survivor.write_text(
            survivor.read_text(encoding="utf-8").replace("subjects: {}", "tier: principle\nsubjects: {}"),
            encoding="utf-8",
        )
        reader = SourceReader(self.root, schema_mode=1)
        with redirect_stderr(StringIO()) as stderr:
            reader.capture()
        self.assertNotIn(survivor, reader._references.accepted)
        self.assertIn("header.context.tier requires BIGINT", stderr.getvalue())
        first.unlink()
        event = {"operation": "delete", "old_path": first.relative_to(self.root).as_posix(), "new_path": None}
        atoms, _scopes = reader.capture([event])
        self.assertNotIn("CA-R-900", {row["ref"] for row in atoms})


    def test_crlf_body_and_legacy_header_aliases_are_preserved(self) -> None:
        path = self._path("CHILD", "05_method", "aliases.md")
        body = "## Summary\r\n\r\nOriginal CRLF body.\r\n"
        raw = (
            "---\r\n"
            'atom_id: "CA-R-301"\r\n'
            'content_role: "Requirement"\r\n'
            'type: "Method"\r\n'
            'status: "Active"\r\n'
            "version: 4\r\n"
            'updated_at: "2026-11-04 00:00:00 +0000"\r\n'
            "subjects: {}\r\n"
            "relations: {}\r\n"
            "---\r\n"
            + body
        ).encode()
        path.write_bytes(raw)
        before = path.read_bytes()

        atoms, _scopes, stderr = self._capture()
        row = next(row for row in atoms if row["id"] == "CA-R-301")

        self.assertEqual(stderr, "")
        self.assertEqual(row["role"], "Requirement")
        self.assertEqual(row["form"], "Method")
        self.assertNotIn("content_markdown", row)
        self.assertEqual(row["_content_bytes"], body.encode("utf-8"))
        self.assertEqual(source_markdown(row), body)
        self.assertEqual(row["header_json"]["content_role"], "Requirement")
        self.assertEqual(row["header_json"]["type"], "Method")
        self.assertNotIn("role", row["header_json"])
        self.assertNotIn("form", row["header_json"])
        self.assertEqual(path.read_bytes(), before)

        legacy = self._path("CHILD", "05_method", "legacy-carrier.md")
        legacy.write_text(
            "---\nrole: Requirement\nform: Definition\nstatus: Active\nversion: 1\n"
            "updated_at: \"2026-11-04 00:00:00 +0000\"\n---\n# Summary\nLegacy.\n",
            encoding="utf-8",
        )
        atoms, _scopes, stderr = self._capture()
        legacy_row = next(row for row in atoms if row["source_path"] == legacy.relative_to(self.root).as_posix())
        self.assertEqual(stderr, "")
        self.assertIsNone(legacy_row["id"])
        self.assertIsNone(legacy_row["ref"])


    def test_invalid_sources_are_excluded_and_unchanged_failures_are_not_retried(self) -> None:
        valid = self._write_atom("MAIN", "01_concern", "valid.md", atom_id="CA-R-401")
        invalid = self._path("MAIN", "04_requirement", "CA-R-402-bad.md")
        invalid.write_text(
            "---\natom_id: CA-R-402\natom_id: CA-R-403\nrole: Requirement\n"
            "form: Definition\nstatus: Active\nversion: 1\n---\n# Summary\nBad\n",
            encoding="utf-8",
        )

        atoms, _scopes, first_stderr = self._capture()
        self.assertIn(valid.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
        self.assertNotIn(invalid.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
        self.assertIn("duplicate", first_stderr.lower())
        self.assertIn(invalid.relative_to(self.root).as_posix(), first_stderr)
        self.assertEqual(self.reader.excluded_count, 1)



if __name__ == "__main__":
    unittest.main()
