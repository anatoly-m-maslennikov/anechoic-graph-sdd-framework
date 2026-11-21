"""Select active native Methodology Specs for Local Release."""

from hashlib import sha256
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'LAYER_5_FRAMEWORK_DELIVERY/RELEASE_VERSION'),
               str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS'),
               str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC'),
               str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43')]
from release_support import LocalReleaseError, _native_release_sources

MODEL_SOURCES = (
    "LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62."
    "manifest_compiler_pkg1.active_model_sources.read_active_model_sources"
)
ADMIT_MODEL = "FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model.admit_active_model_records"


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
        self.read_model = self.enterContext(patch(MODEL_SOURCES, return_value=()))
        self.enterContext(patch(ADMIT_MODEL))

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
        for directory in ("_PMETA", "__TKT", "000_ANECHOIC_framework", "UNRELATED_C10"):
            self.carrier(self.control / directory / self.source.name)
        self.carrier(self.ontology / "000_draft/AN-S-1@3-draft-DOM--current.md", status="draft", version=3)
        self.carrier(self.ontology / "099_archived/AN-S-2@1-DOM--retired.md",
                     atom_id="AN-S-2", status="archived", version=1)
        for directory in ("01_draft", "02_ready", "09_archived"):
            self.carrier(self.ontology / directory / "AN-S-1-DOM--excluded.md")
        self.assertEqual({p.relative_to(self.control): p for p in (self.source, new)},
                         _native_release_sources(self.selection))
        self.read_model.assert_called_once_with(self.control, self.ontology)

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

    def test_rejects_changed_source_or_membership_after_selection(self):
        def change_source(*_args):
            self.source.write_text(self.source.read_text() + "\nchanged")
            return ()

        def add_source(*_args):
            self.carrier(self.ontology / "AN-S-7-SPEC--new.md", atom_id="AN-S-7")
            return ()

        for change in (change_source, add_source):
            with self.subTest(change=change.__name__):
                self.read_model.side_effect = change
                with self.assertRaisesRegex(LocalReleaseError, "sources changed"):
                    _native_release_sources(self.selection)

    def test_rejects_model_compiler_errors_and_empty_scope(self):
        self.read_model.side_effect = ValueError("invalid Model Claim")
        with self.assertRaisesRegex(LocalReleaseError, "invalid Model Claim"):
            _native_release_sources(self.selection)
        self.source.unlink()
        with self.assertRaisesRegex(LocalReleaseError, "No Active Meta-ontology Specs"):
            _native_release_sources(self.selection)


if __name__ == "__main__":
    unittest.main()
