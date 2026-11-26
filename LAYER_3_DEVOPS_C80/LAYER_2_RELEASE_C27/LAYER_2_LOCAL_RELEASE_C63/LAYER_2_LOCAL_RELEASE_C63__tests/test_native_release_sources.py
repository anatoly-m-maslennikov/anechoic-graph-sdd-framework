"""Select active native Methodology Specs for Local Release."""

from hashlib import sha256
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import LocalReleaseError, _native_release_sources


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

    def carrier(self, path, *, atom_id="AN-S-1", status="active", version=2, component="C9", template=""):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"""---
atom_family: SPEC
atom_id: {atom_id}
container:
  component: {component}
tier: 1
context:
  lens: DES/DOM
  template: {template}
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

    def test_resolves_nested_components_and_keeps_delivery_names(self):
        parent = self.control / "ONTOLOGY_SCORE_C82"
        parent.mkdir()
        self.ontology.rename(parent / "CONTINUANT_PITCHFORK_C9")
        self.source = parent / "CONTINUANT_PITCHFORK_C9/__DES/__DOM/AN-S-1-DOM--current.md"
        c58 = parent / "OCCURRENT_METRONOME_C58"
        c58.mkdir()
        selected = _native_release_sources(self.selection)
        self.assertEqual({Path("LAYER_1_META_ONTOLOGY_C9/__DES/__DOM/AN-S-1-DOM--current.md"): self.source}, selected)
        method = c58 / "AN-S-2-SPEC--method.md"
        self.carrier(method, atom_id="AN-S-2", component="C58")
        self.assertEqual(method, _native_release_sources(self.selection)[Path("LAYER_2_META_METHODOLOGY_C58") / method.name])

    def test_component_resolution_excludes_non_component_parents_and_rejects_links(self):
        for parent in ("099_archived", "_projection", "arbitrary"):
            self.carrier(self.control / parent / "OTHER_C9/AN-S-2-SPEC--ignored.md", atom_id="AN-S-2")
        self.assertEqual({self.source}, set(_native_release_sources(self.selection).values()))
        link = self.control / "PARENT_C82"
        link.symlink_to(self.control / "arbitrary", target_is_directory=True)
        with self.assertRaises(LocalReleaseError):
            _native_release_sources(self.selection)

    def test_rejects_ambiguous_component_sources(self):
        self.carrier(self.control / "PARENT_C82/OTHER_C9/AN-S-2-SPEC--other.md", atom_id="AN-S-2")
        with self.assertRaisesRegex(LocalReleaseError, "Multiple delivery source Components for C9"):
            _native_release_sources(self.selection)

    def test_selects_methodology_and_environment_owned_active_specs(self):
        c58 = self.control / "LAYER_2_META_METHODOLOGY_C58"
        c72 = self.control / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72"
        paths = [
            (c58 / "__DES/AN-S-20-DES--method.md", "AN-S-20", "C58"),
            (self.control / "AN-S-21-SPEC--axiom.md", "AN-S-21", "C00"),
            (self.control / "_QA/AN-S-22-QA--project-goal-guidance.md", "AN-S-22", "C00"),
            (self.control / "01_TIER_1_ARCHITECTURE/AN-S-29-SPEC--architecture.md", "AN-S-29", "C00"),
            (self.control / "_DES/DOM/AN-S-30-DOM--design.md", "AN-S-30", "C00"),
            (self.control / "_CUSTOM/AN-S-31-CUSTOM--custom.md", "AN-S-31", "C00"),
            (c72 / "__DEVOPS/AN-S-23-DEVOPS--environment.md", "AN-S-23", "C72"),
        ]
        for path, atom_id, component in paths:
            self.carrier(path, atom_id=atom_id, component=component)
        self.carrier(self.control / "AN-S-24-SPEC-PROJECT_CONTRACT--exclude.md", atom_id="AN-S-24", component="C00", template="project_contract")
        self.carrier(self.control / "__QA/AN-S-28-SPEC--objective.md", atom_id="AN-S-28", component="C00", template="project_goal")
        self.carrier(self.control / "__QA/AN-S-25-QA--other-component.md", atom_id="AN-S-25", component="C9")
        self.carrier(c72 / "AN-S-26-SPEC--other-component.md", atom_id="AN-S-26", component="C00")
        self.carrier(c58 / "01_draft/AN-S-27-SPEC--draft.md", atom_id="AN-S-27", component="C58")
        selected = _native_release_sources(self.selection)
        self.assertEqual({self.source, *(path for path, _, _ in paths)}, set(selected.values()))
        self.assertIn(Path("LAYER_2_META_METHODOLOGY_C58/_QA/AN-S-22-QA--project-goal-guidance.md"), selected)
        self.assertIn(Path("LAYER_2_META_METHODOLOGY_C58/__DEVOPS/AN-S-23-DEVOPS--environment.md"), selected)

    def test_uses_manifest_tier_one_directory_for_project_specs(self):
        self.selection.parameters = {"project": {"folder_layout": {"active_spec_by_tier": {
            "0": ".", "1": "01_PROJECT_DESIGN", "2+": "_{lens}/{sublenses}",
        }}}}
        selected = self.control / "01_PROJECT_DESIGN/AN-S-2-DES--selected.md"
        default = self.control / "01_TIER_1_ARCHITECTURE/AN-S-3-DES--default.md"
        self.carrier(selected, atom_id="AN-S-2", component="C00")
        self.carrier(default, atom_id="AN-S-3", component="C00")
        self.assertEqual({self.source, selected}, set(_native_release_sources(self.selection).values()))

    def test_rejects_tier_one_directories_that_are_unsafe_or_reserved(self):
        for name in ("../outside", "01_DRAFT", "01_DESIGN_C72"):
            with self.subTest(name=name):
                self.selection.parameters = {"project": {"folder_layout": {"active_spec_by_tier": {
                    "0": ".", "1": name, "2+": "_{lens}/{sublenses}",
                }}}}
                with self.assertRaisesRegex(LocalReleaseError, "Invalid Tier 1 SPEC folder"):
                    _native_release_sources(self.selection)

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
