"""Select active native Methodology Specs for Local Release."""

from hashlib import sha256
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from RELEASE_VERSION.release_support import LocalReleaseError, _native_release_sources


class NativeReleaseSourcesTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.control = self.root / ".anechoic_fixture"
        self.ontology = self.control / "LAYER_1_META_ONTOLOGY_C9"
        manifest = self.control / "manifest.md"
        manifest.parent.mkdir()
        manifest.write_bytes(b"manifest")
        self.selection = SimpleNamespace(root=self.root, control_root=self.control, manifest_path=manifest,
                                         manifest_sha256=sha256(b"manifest").hexdigest(), project_prefix="AN")
        self.source = self.ontology / "__DES/__DOM/AN-S-1-DOM--current.md"
        self.carrier(self.source)

    def carrier(self, path, *, atom_id="AN-S-1", status="active", version=2):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"""---
atom_family: SPEC
atom_id: {atom_id}
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES/DOM
state:
  status: {status}
  version: {version}
  updated_at: '2026-11-21T00:00:00Z'
---
## Summary

Native Spec.
""")

    def test_uses_native_paths_and_includes_specs_without_migration_entries(self):
        new = self.ontology / "AN-S-7-SPEC--new.md"
        self.carrier(new, atom_id="AN-S-7")
        for directory in ("_PMETA", "002_PROJECT_CONFIG", "__TKT", "000_ANECHOIC_framework", "UNRELATED_C10"):
            self.carrier(self.control / directory / self.source.name)
        self.carrier(self.ontology / "000_draft/AN-S-1@3-draft-DOM--current.md", status="draft", version=3)
        self.carrier(self.ontology / "099_archived/AN-S-2@1-DOM--retired.md",
                     atom_id="AN-S-2", status="archived", version=1)
        for directory in ("01_draft", "02_ready", "09_archived"):
            self.carrier(self.ontology / directory / "AN-S-1-DOM--excluded.md")
        self.carrier(self.ontology / "AN-S-8-SPEC--retired.md", atom_id="AN-S-8", status="retired")
        self.assertEqual({p.relative_to(self.control): p for p in (self.source, new)},
                         _native_release_sources(self.selection))

    def test_rejects_duplicate_current_identity_in_the_component(self):
        self.carrier(self.ontology / "AN-S-1-DOM--duplicate.md")
        with self.assertRaisesRegex(LocalReleaseError, "duplicate Current identity"):
            _native_release_sources(self.selection)

    def test_rejects_linked_carrier_and_linked_component(self):
        other = self.ontology / "AN-S-2-DOM--link.md"
        other.symlink_to(self.source)
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)
        other.unlink()
        moved = self.root / "moved"
        self.ontology.rename(moved)
        self.ontology.symlink_to(moved)
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)

    def test_rejects_changed_manifest(self):
        self.selection.manifest_path.write_bytes(b"changed")
        with self.assertRaisesRegex(LocalReleaseError, "Manifest changed"):
            _native_release_sources(self.selection)

    def test_rejects_linked_manifest(self):
        manifest = self.selection.manifest_path
        manifest.unlink()
        external = self.root / "manifest.md"
        external.write_bytes(b"manifest")
        manifest.symlink_to(external)
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)

    def test_rejects_malformed_headers(self):
        for header in ("no header", "---\natom_family: [\n---\n", "---\natom_family: TASK\n---\n",
                       "---\natom_family: SPEC\nstate: {}\n---\n"):
            with self.subTest(header=header):
                self.source.write_text(header)
                with self.assertRaises(LocalReleaseError):
                    _native_release_sources(self.selection)

    def test_rejects_mismatched_current_filename(self):
        self.carrier(self.source, atom_id="AN-S-2")
        with self.assertRaisesRegex(LocalReleaseError, "mismatched Spec filename"):
            _native_release_sources(self.selection)

    def test_rejects_empty_scope(self):
        self.source.unlink()
        with self.assertRaisesRegex(LocalReleaseError, "No Active Meta-ontology Specs"):
            _native_release_sources(self.selection)


if __name__ == "__main__":
    unittest.main()
