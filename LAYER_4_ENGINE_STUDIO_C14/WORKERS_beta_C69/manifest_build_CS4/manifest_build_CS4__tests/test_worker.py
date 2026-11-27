import tempfile
import unittest
from hashlib import sha256
from unittest.mock import patch

from ..manifest_build_CS4__shared import (
    _COMPILER_SOURCE_DIRECTORIES,
    _REVIEWED_CLAIMS,
    _compiler_sha256,
    manifest_input_signature,
)
from ._manifest_build_cases import ManifestBuildCases
from .manifest_build_CS4__tests__shared import WORKER_MODULE, fixture


class BuildTests(ManifestBuildCases, unittest.TestCase):
    pass


class InputSignatureTests(unittest.TestCase):
    def setUp(self):
        temporary = self.enterContext(tempfile.TemporaryDirectory())
        self.binding, _, self.manifest = fixture(temporary)
        self.control = self.manifest.parent
        self.root = self.control.parent

    def signature(self):
        return manifest_input_signature(self.binding)

    def test_ticket_tree_changes_preserve_the_signature(self):
        before = self.signature()
        self.assertIsNotNone(before)
        ticket = (
            self.control / "__TICKETS/TASKS/EPIC_C123/AN-T-1-TASK--change.md"
        )
        ticket.parent.mkdir(parents=True)
        ticket.write_text("Created")
        self.assertEqual(before, self.signature())
        ticket.write_text("Edited")
        self.assertEqual(before, self.signature())
        ticket = ticket.rename(ticket.with_name("AN-T-1-TASK--renamed.md"))
        self.assertEqual(before, self.signature())
        ticket.unlink()
        self.assertEqual(before, self.signature())

    def test_candidate_content_and_component_topology_affect_the_signature(
        self,
    ):
        sources = (
            "LAYER_1_META_ONTOLOGY_C9/_SPEC/model.md",
            "ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9/_DES/model.md",
            "ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9/_DOM/CONT/model.md",
            "__PROJECT_CONFIG/CUSTOM_MODEL/config.md",
            "002_PROJECT_CONFIG/CUSTOM_MODEL/compatibility.md",
            "LAYER_C3/CHILD_C4/_SPEC/AN-S-1-canonical-component.md",
            "LAYER_C3/CHILD_C4/AN-S-2-SPEC-COMPONENT_SEED_MANIFEST--seed.md",
            "LAYER_C3/01_OTHER_ARCHITECTURE/"
            "AN-S-3-SPEC-COMPONENT_MANIFEST--component.md",
        )
        for source in sources:
            with self.subTest(source=source):
                candidate = self.control / source
                candidate.parent.mkdir(parents=True, exist_ok=True)
                before = self.signature()
                self.assertIsNotNone(before)
                candidate.write_text("First")
                added = self.signature()
                self.assertNotEqual(before, added)
                candidate.write_text("Other")
                edited = self.signature()
                self.assertNotEqual(added, edited)
                moved = candidate.rename(
                    candidate.with_name(candidate.stem + "-renamed.md")
                )
                self.assertNotEqual(edited, self.signature())
                moved.unlink()
                self.assertEqual(before, self.signature())
        before = self.signature()
        empty = self.control / "LAYER_C3/EMPTY_C5"
        empty.mkdir()
        self.assertNotEqual(before, self.signature())
        empty.rmdir()
        self.assertEqual(before, self.signature())

    def test_tier_one_changes_affect_signature_with_configured_layout(self):
        for folder in ("01_TIER_1_ARCHITECTURE", "01_CUSTOM_ARCHITECTURE"):
            with self.subTest(folder=folder):
                if folder != "01_TIER_1_ARCHITECTURE":
                    text = self.manifest.read_text().replace(
                        "lens_whitelist=['SPEC']",
                        "lens_whitelist=['SPEC'], "
                        "parameters={'project': {'folder_layout': "
                        "{'active_spec_by_tier': {'0': '.', "
                        "'1': '01_CUSTOM_ARCHITECTURE', "
                        "'2+': '_{lens}/{sublenses}'}}}}",
                    )
                    self.manifest.write_text(text)
                    self.binding["manifest_sha256"] = sha256(
                        self.manifest.read_bytes()
                    ).hexdigest()
                for owner in (self.control, self.control / "LAYER_C3"):
                    directory = owner / folder
                    directory.mkdir(parents=True, exist_ok=True)
                    candidate = (
                        directory
                        / "AN-S-2-SPEC-COMPONENT_MANIFEST--component.md"
                    )
                    before = self.signature()
                    self.assertIsNotNone(before)
                    candidate.write_text("Before edit")
                    added = self.signature()
                    self.assertNotEqual(before, added)
                    candidate.write_text("After edit")
                    self.assertNotEqual(added, self.signature())
                    candidate.unlink()
                    self.assertEqual(before, self.signature())

    def test_project_selection_precedence_and_pin(self):
        shadow = self.control / "alternate.md"
        before = self.signature()
        shadow.write_text(
            "A native Project Manifest could use this compatibility path"
        )
        self.assertNotEqual(before, self.signature())
        root_manifest = self.root / self.manifest.name
        self.manifest.rename(root_manifest)
        before = self.signature()
        self.assertIsNotNone(before)
        shadow.write_text("A root Manifest takes precedence over this file")
        self.assertEqual(before, self.signature())
        another_root = self.root / "AN-S-2-PROJECT_MANIFEST--alternate.md"
        another_root.write_text("Alternate root candidate")
        self.assertNotEqual(before, self.signature())
        root_manifest.write_text("Changed binding")
        self.assertIsNone(self.signature())

    def _identical_candidate_retains_signature(
        self,
    ):
        candidate = self.control / "AN-S-1-canonical-component.md"
        candidate.write_text("Component")
        before = self.signature()
        self.assertIsNotNone(before)
        replacement = candidate.with_suffix(".tmp")
        replacement.write_bytes(candidate.read_bytes())
        replacement.replace(candidate)
        self.assertEqual(before, self.signature())

    def compiler_sources(self):
        engine = self.root / "engine"
        generator = (
            engine
            / "FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75"
            / "LAYER_2_FORMAL_MODEL_C51"
            / "FEATURE_FORMAL_MODEL_GENERATOR"
        )
        compiler = generator / "manifest_compiler_CS1/compiler.py"
        compiler.parent.mkdir(parents=True)
        compiler.write_text("IMPLEMENTATION = 1")
        coordinator = (
            engine
            / "FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/compile_project__pub.py"
        )
        coordinator.write_text("COORDINATOR = 1")
        structure = (
            engine
            / "FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75"
            / "LAYER_2_PROJECT_STRUCTURE_C93"
            / "LAYER_2_PROJECT_STRUCTURE_C93__shared.py"
        )
        structure.parent.mkdir(parents=True)
        structure.write_text("STRUCTURE = 1")
        for relative in _COMPILER_SOURCE_DIRECTORIES:
            (engine / relative).mkdir(parents=True, exist_ok=True)
        reviewed = engine / "reviewed"
        reviewed.mkdir()
        for name in _REVIEWED_CLAIMS:
            (reviewed / name).write_text("{}")
        return engine, generator, compiler, coordinator, structure, reviewed

    def test_compiler_sources_affect_the_signature_and_tests_do_not(self):
        engine, generator, compiler, coordinator, structure, reviewed = (
            self.compiler_sources()
        )
        with (
            patch(
                f"{WORKER_MODULE}.ENGINE",
                engine,
            ),
            patch(
                f"{WORKER_MODULE}._REVIEWED_MODEL",
                reviewed,
            ),
        ):
            before = self.signature()
            self.assertIsNotNone(before)
            compiler_digest = _compiler_sha256()
            structure.write_text("STRUCTURE = 2")
            self.assertNotEqual(before, self.signature())
            self.assertNotEqual(compiler_digest, _compiler_sha256())
            compiler_digest = _compiler_sha256()
            coordinator.write_text("COORDINATOR = 2")
            self.assertNotEqual(compiler_digest, _compiler_sha256())
            before = self.signature()
            compiler.write_text("IMPLEMENTATION = 2")
            changed = self.signature()
            self.assertIsNotNone(changed)
            self.assertNotEqual(before, changed)
            helper = generator / "manifest_property_fields.py"
            helper.write_text("FIELDS = ()")
            added = self.signature()
            self.assertIsNotNone(added)
            self.assertNotEqual(changed, added)
            suite = compiler.parent / "manifest_compiler_CS1__tests"
            suite.mkdir()
            (suite / "test_compiler.py").write_text("assert False")
            self.assertEqual(added, self.signature())
            compiler.unlink()
            self.assertIsNone(self.signature())
            compiler.write_text("IMPLEMENTATION = 2")
            coordinator.unlink()
            self.assertIsNone(self.signature())

    def test_uncertain_candidates_do_not_admit_reuse(self):
        manifest = self.control / "AN-S-1-canonical-component.md"
        manifest.symlink_to(self.manifest)
        self.assertIsNone(self.signature())
        manifest.unlink()
        manifest.mkdir()
        self.assertIsNone(self.signature())
        manifest.rmdir()

        def change_after_read(path, _limit):
            data = path.read_bytes()
            (self.control / "NEW_C5").mkdir(exist_ok=True)
            return sha256(data).hexdigest(), len(data), ()

        with patch(
            f"{WORKER_MODULE}._read_digest",
            side_effect=change_after_read,
        ):
            self.assertIsNone(self.signature())

    def test_watcher_guarded_signature_samples_once(self):
        expected = self.signature()
        self.assertIsNotNone(expected)
        paths = []

        def read_once(path, _limit):
            self.assertNotIn(path, paths)
            paths.append(path)
            data = path.read_bytes()
            return sha256(data).hexdigest(), len(data), ()

        with patch(
            f"{WORKER_MODULE}._read_digest",
            side_effect=read_once,
        ):
            self.assertEqual(
                expected,
                manifest_input_signature(self.binding, watcher_guarded=True),
            )
        self.assertIn(self.manifest, paths)


setattr(
    InputSignatureTests,
    "test_replacing_a_candidate_with_identical_bytes_preserves_the_signature",
    InputSignatureTests._identical_candidate_retains_signature,
)


if __name__ == "__main__":
    unittest.main()
