"""Source-reader content and header cases."""

from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    source_markdown,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import infer_header_schema

TIER_CLAIM = """## Claim

### Formal Claim

~~~python
from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Tier", relation_name="IS_PROPERTY_OF", base_path="Atom.Header",
               value_format=int, value_cardinality=1)
~~~
"""


class SourceReaderIncrementalCases:
    def test_mode_two_header_declaration_shape_change_stays_incremental(
        self,
    ) -> None:
        declaration = self._write_atom(
            "MAIN",
            "04_requirement",
            "CA-R-702-MAIN-DECLARATION--header.md",
            atom_id="CA-R-702",
            form="Declaration",
            body=TIER_CLAIM,
        )
        before, _scopes, _stderr = self._capture()
        before_shape = infer_header_schema(before).shape
        declaration.write_text(
            declaration.read_text(encoding="utf-8")
            + """
~~~python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name="Declared Later", relation_name="IS_PROPERTY_OF", base_path="Atom.Header",
               value_format=str, value_cardinality=Cardinality(minimum=0, maximum=1))
~~~
""",
            encoding="utf-8",
        )
        event = {
            "operation": "update",
            "old_path": None,
            "new_path": declaration.relative_to(self.root).as_posix(),
        }
        with patch.object(
            self.reader, "_capture_full", wraps=self.reader._capture_full
        ) as full:
            after, _scopes = self.reader.capture([event])
        self.assertFalse(full.called)
        self.assertEqual(before_shape, infer_header_schema(after).shape)
        self.assertIsNotNone(self.reader.capture_delta)

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
            "---\r\n" + body
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
            'updated_at: "2026-11-04 00:00:00 +0000"\n---\n# Summary\nLegacy.\n',
            encoding="utf-8",
        )
        atoms, _scopes, stderr = self._capture()
        legacy_row = next(
            row
            for row in atoms
            if row["source_path"] == legacy.relative_to(self.root).as_posix()
        )
        self.assertEqual(stderr, "")
        self.assertIsNone(legacy_row["id"])
        self.assertIsNone(legacy_row["ref"])
