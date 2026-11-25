"""Reference selection updates the declarations that shape the Workbench."""
import unittest

from ._source_reader_fixture import SourceReaderFixture


class ReferenceSelectionTests(SourceReaderFixture, unittest.TestCase):
    def declaration(self, directory, header_field):
        return self._write_atom(
            "MAIN", "04_requirement", "CA-R-805-declaration.md",
            atom_id="CA-R-805", form="Declaration", parts=(directory,),
            body=("## Claim\n\n### Formal Claim\n\n```CFEL\n"
                  f"Atom.Header.{header_field}:: [int]{{::0..1}};\n```\n"),
        )

    def test_authoritative_carrier_selection_updates_after_an_incremental_move(self):
        preferred = self.declaration("b", "Preferred")
        other = self.declaration("z", "Other")
        generated = self.control / "_projection" / "CA-R-805-declaration.md"
        generated.parent.mkdir()
        generated.write_text(preferred.read_text().replace("Preferred", "Generated"))
        preferred_path = preferred.relative_to(self.root).as_posix()
        other_path = other.relative_to(self.root).as_posix()

        rows, _ = self.reader.capture()
        self.assertEqual({preferred_path, other_path},
                         {row["source_path"] for row in rows if row["ref"] == "CA-R-805"})
        self.assertEqual(("header.preferred",), self.reader.header_schema.names)

        moved = other.parent.parent / "a" / other.name
        moved.parent.mkdir()
        other.rename(moved)
        moved_path = moved.relative_to(self.root).as_posix()
        rows, _ = self.reader.capture([{
            "operation": "move", "old_path": other_path, "new_path": moved_path,
        }])

        self.assertEqual({preferred_path, moved_path},
                         {row["source_path"] for row in rows if row["ref"] == "CA-R-805"})
        self.assertEqual(("header.other",), self.reader.header_schema.names)
        self.assertIsNone(self.reader.capture_delta[other_path])
        self.assertEqual("CA-R-805", self.reader.capture_delta[moved_path]["ref"])
        self.assertEqual("CA-R-805", self.reader.capture_delta[preferred_path]["ref"])
