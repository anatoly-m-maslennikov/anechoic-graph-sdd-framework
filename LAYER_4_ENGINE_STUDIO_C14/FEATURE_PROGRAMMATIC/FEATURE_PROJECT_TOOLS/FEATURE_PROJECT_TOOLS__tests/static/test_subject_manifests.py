"""Verify Subject Manifest content and parent graph checks."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.subject_manifests import (
    findings,
)


class SubjectManifestTests(unittest.TestCase):
    def test_structure_and_parentage(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            control = root / "_anechoic_test"
            control.mkdir()

            def write(number, body, status="active"):
                (control / f"{number}.md").write_text(
                    "---\n"
                    f"atom_id: AN-S-{number}\n"
                    "context:\n  template: subject_manifest\n"
                    f"state:\n  status: {status}\n---\n\n{body}"
                )

            base = "## Summary\n\nSubject\n\n## Scope\n\nScope\n"
            write(1, base)
            write(2, base + "\n## Parent Subject\n\nAN-S-1\n")
            write(3, base)
            self.assertEqual([], findings(root))
            write(1, base + "\n## Parent Subject\n\nAN-S-2\n")
            self.assertTrue(any("cyclic" in e for e in findings(root)))
            write(1, "## Summary\n\n\n## Scope\n\nScope\n")
            self.assertTrue(any("summary" in e for e in findings(root)))
            write(1, base, "draft")
            self.assertTrue(
                any("inactive parent" in e for e in findings(root))
            )
            write(2, base + "\n## Parent Subject\n\nAN-S-1\nAN-S-3\n")
            self.assertTrue(any("invalid" in e for e in findings(root)))
            write(2, base + "\n## Parent Subject\n\nAN-S-3\n"
                  "\n## Parent Subject\n\nAN-S-3\n")
            self.assertTrue(any("cannot read" in e for e in findings(root)))

    def test_dot_control_nested_sources_and_excluded_copies(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            control = root / ".anechoic_project"
            nested = control / ".anechoic_project" / "component" / "_SPEC"
            nested.mkdir(parents=True)
            manifest = (
                "---\natom_id: AN-S-1\ncontext:\n"
                "  template: subject_manifest\n"
                "state:\n  status: active\n---\n\n"
                "## Summary\n\nSubject\n\n## Scope\n\nScope\n"
            )
            (nested / "subject.md").write_text(manifest)
            for name in ("09_archived", "000_ANECHOIC_framework"):
                folder = control / name
                folder.mkdir()
                (folder / "copy.md").write_text(manifest)
            self.assertEqual([], findings(root))
            (nested / "subject.md").write_text(
                manifest.replace("\n\nScope\n", "\n\n")
            )
            self.assertTrue(any("scope" in e for e in findings(root)))
