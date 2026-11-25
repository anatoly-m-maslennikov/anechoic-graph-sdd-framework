"""Standalone current Topics readers and seven views need no legacy runtime."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL), str(TOOL.parent)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import read_current_carriers  # noqa: E402


def run_projection(repository, source, view):
    return subprocess.run(
        [sys.executable, "-B", str(TOOL / "render_subject_projections.py"), source,
         "--repository", str(repository), "--view", view],
        text=True, capture_output=True, timeout=30,
    )


def write_atom(folder, number, subject, claim, *, dependencies=()):
    metadata = {
        "identity": {"atom_id": f"CA-R-{number}"},
        "context": {"role": "Requirement", "form": "Declaration",
                    "topics": {"main_subject": subject, "dependencies": list(dependencies)}},
        "state": {"status": "Active", "version": 7},
    }
    path = folder / f"CA-R-{number}.md"
    path.write_text("---\n" + yaml.safe_dump(metadata) + "---\n\n## Claim\n\n" + claim + "\n")
    return path


class RenderSubjectProjectionsTests(unittest.TestCase):
    def test_all_seven_views_read_current_nested_topics_and_preserve_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            sources = root / "sources"
            sources.mkdir()
            write_atom(sources, 9001, "ANECHOIC <+ MODEL <+ Node", "Node declaration.",
                       dependencies=["ANECHOIC <+ MODEL <+ Missing", "ANECHOIC <+ STRUCTURE <+ Project"])
            write_atom(sources, 9002, "ANECHOIC <+ MODEL <+ Node/Child", "Child declaration.")
            write_atom(sources, 9003, "ANECHOIC <+ MODEL <+ Node.Name", "```CFEL\nNode.Name: [string]{:1};\n```")
            drafts = sources / "draft"
            drafts.mkdir()
            write_atom(drafts, 9004, "ANECHOIC <+ MODEL <+ Hidden", "Excluded.")
            before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(3, len(read_current_carriers(sources, root)))
            expected = {
                "primary-tree": "Node",
                "direct-properties": "Node.Name",
                "inherited-contracts": "Node/Child",
                "formal-claims": "Node.Name: [string]{:1};",
                "passive-only-subjects": "Missing",
                "subjects-without-declarations": "CA-R-9001@7",
                "entity-definition-coverage": "| `Missing` | primary_node | missing | missing |",
            }
            for view, golden in expected.items():
                with self.subTest(view=view):
                    result = run_projection(root, "sources", view)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn(golden, result.stdout)
                    self.assertNotIn("Hidden", result.stdout)
                    self.assertNotIn("STRUCTURE", result.stdout)
            self.assertEqual(before, {path: path.read_bytes() for path in root.rglob("*") if path.is_file()})

    def test_source_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            project = root / "project"
            project.mkdir()
            result = run_projection(project, "..", "primary-tree")
            self.assertEqual(1, result.returncode)
            self.assertIn("inside the selected repository", result.stderr)


if __name__ == "__main__":
    unittest.main()
