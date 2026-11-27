"""Current Atom folder selection and Subject syntax, without migration \
profiles."""

import hashlib
import json
from importlib import import_module
from pathlib import Path
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]
_adapter = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
)
_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_cases = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests._current_entity_cases"
)
CEILINGS = _adapter.CEILINGS
read_current_carriers = _adapter.read_current_carriers
read_current_model_carriers = _adapter.read_current_model_carriers
CarrierError = _adapter.CarrierError
compose_current_graph = _graph.compose_current_graph

TEST_TEMP_ROOT = Path.cwd() / ".anechoic_tmp/tests/test_current_entity_sources"


class CurrentEntitySourcesTests(_cases.CurrentEntityCases, unittest.TestCase):
    def setUp(self):
        TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(
            dir=TEST_TEMP_ROOT, ignore_cleanup_errors=True
        )
        self.addCleanup(self.temporary.cleanup)
        self.repository = Path(self.temporary.name)
        self.selected = self.repository / "sources"
        self.selected.mkdir()

    def write(
        self,
        atom_id,
        subject,
        *,
        version=1,
        status="Active",
        folder="",
        dependencies=(),
    ):
        path = self.selected / folder / f"{atom_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\natom_id: {atom_id}\nversion: {version}\nstatus: {status}\n"
            "content_role: Requirement\nsubjects:\n"
            f"  governs: {json.dumps(subject)}\n"
            f"  depends_on: {json.dumps(dependencies)}\n"
            "---\n# Source\n\nSource content does not classify edges.\n",
            encoding="utf-8",
        )
        return path

    def build(self, selected=None):
        source = self.selected if selected is None else selected
        return compose_current_graph(
            read_current_carriers(source, self.repository)
        )

    def test_folder_selection_excludes_draft_archived_paths_but_not_status(
        self,
    ):
        self.write(
            "CA-R-9001", "Done Entity", status="Done", folder="020_done"
        )
        self.write(
            "CA-R-9002",
            "Backlog Entity",
            status="Backlog",
            folder="001_backlog",
        )
        excluded = (
            "draft",
            "drafts",
            "archive",
            "archived",
            "000_draft",
            "099_archived",
        )
        for index, folder in enumerate(excluded, 3):
            self.write(
                f"CA-R-900{index}", "Excluded", folder=f"nested/{folder}/deep"
            )
        graph, provenance = self.build()
        self.assertEqual(
            {"Done Entity", "Backlog Entity"},
            {row["identity"] for row in graph["nodes"]},
        )
        self.assertEqual(
            {"CA-R-9001", "CA-R-9002"},
            {row["source"]["atom_id"] for row in provenance["owners"]},
        )
        for folder in excluded:
            with self.subTest(selected=folder):
                selected = self.selected / "nested" / folder / "deep"
                self.assertEqual([], self.build(selected)[0]["nodes"])

    def test_reader_returns_exact_source_bytes_metadata_and_body(self):
        path = self.write("CA-R-9001", "Current Entity")
        raw = path.read_bytes()

        carriers = read_current_carriers(self.selected, self.repository)

        self.assertEqual(1, len(carriers))
        carrier = carriers[0]
        self.assertEqual(
            {
                "atom_id": "CA-R-9001",
                "version": 1,
                "path": "sources/CA-R-9001.md",
                "sha256": hashlib.sha256(raw).hexdigest(),
            },
            carrier["source"],
        )
        self.assertEqual("Current Entity", carrier["subjects"]["governs"])
        self.assertEqual("Requirement", carrier["metadata"]["content_role"])
        self.assertIn("# Source", carrier["body"])
        self.assertEqual(raw, carrier["raw"])

    def _reader_line_endings(
        self,
    ):
        path = self.selected / "CA-R-9001.md"
        body = "# Rule\r\n\r\n```yaml\nrule: keep\r\n```\n"
        raw = (
            "---\r\natom_id: CA-R-9001\nversion: 1\r\nstatus: Active\n"
            "content_role: Requirement\r\nsubjects:\n  governs: Current\r\n"
            "---\r\n" + body
        ).encode("utf-8")
        path.write_bytes(raw)

        carrier = read_current_carriers(self.selected, self.repository)[0]

        self.assertEqual(body, carrier["raw_body"])
        self.assertNotEqual(body, carrier["body"])
        self.assertEqual(raw, carrier["raw"])

    locals()[
        (
            "test_reader_preserves_exact_body_lin"
            "e_endings_separately_from_parsed_body"
        )
    ] = _reader_line_endings

    def test_enriched_reader_keeps_existing_graph_and_provenance_unchanged(
        self,
    ):
        self.write("CA-R-9001", "Shared")
        self.write("CA-R-9002", "Shared", version=2)
        carriers = read_current_carriers(self.selected, self.repository)
        expected = compose_current_graph(
            [
                {"source": row["source"], "subjects": row["subjects"]}
                for row in carriers
            ]
        )

        self.assertEqual(expected, self.build())

    def test_explicit_draft_and_archived_statuses_are_not_current(self):
        draft = self.write("CA-R-9001", "Draft", status="Active")
        archived = self.write("CA-R-9002", "Archived", status="Active")
        self.write("CA-R-9003", "Current")
        draft.write_text(
            draft.read_text(encoding="utf-8").replace(
                "status: Active", "status: Draft"
            ),
            encoding="utf-8",
        )
        archived.write_text(
            archived.read_text(encoding="utf-8").replace(
                "status: Active", "status: Archived"
            ),
            encoding="utf-8",
        )

        carriers = read_current_carriers(self.selected, self.repository)

        self.assertEqual(
            ["CA-R-9003"], [row["source"]["atom_id"] for row in carriers]
        )
        self.assertEqual(
            ["Current"], [row["identity"] for row in self.build()[0]["nodes"]]
        )

    def test_malformed_atom_is_rejected_instead_of_silently_omitted(self):
        self.write("CA-R-9001", "Valid")
        malformed = self.selected / "CA-R-9002.md"
        malformed.write_text(
            "---\natom_id: [broken\n---\n# Broken\n", encoding="utf-8"
        )

        with self.assertRaises(CarrierError):
            read_current_carriers(self.selected, self.repository)

    def test_model_reads_requirements_without_parsing_known_other_roles(self):
        declaration = self.write("CA-R-9001", "Declared Entity")
        declaration.write_text(
            declaration.read_text().replace(
                "content_role: Requirement\n",
                "content_role: Requirement\nform: Declaration\n",
            )
        )
        (self.selected / "CA-D-9002.md").write_text(
            "---\natom_id: CA-D-9002\nrole: Delivery\n"
            "subjects:\n  active: Old\n"
            "topics:\n  main_subject: New\n---\n## Summary\n\nDelivery\n"
        )
        carriers = read_current_model_carriers(self.selected, self.repository)
        self.assertEqual(
            ["CA-R-9001"], [row["source"]["atom_id"] for row in carriers]
        )
        with self.assertRaises(CarrierError):
            read_current_carriers(self.selected, self.repository)
        (self.selected / "CA-R-9003.md").write_text(
            "---\natom_id: [broken\n---\n"
        )
        with self.assertRaises(CarrierError):
            read_current_model_carriers(self.selected, self.repository)


if __name__ == "__main__":
    unittest.main()
