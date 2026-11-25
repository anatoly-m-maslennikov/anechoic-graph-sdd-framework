import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from ..manifest_build_CS4__shared import manifest_input_signature
from .manifest_build_CS4__tests__shared import fixture, run_worker

ENGINE = Path(__file__).resolve().parents[3]


class BuildTests(unittest.TestCase):
    def test_cli_build_and_verify_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = fixture(directory)
            env = os.environ.copy()
            env['PYTHONPATH'] = str(ENGINE)
            result = subprocess.run([sys.executable, "-B", '-m', 'WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared',
                                     '--output-dir', str(output)], input=json.dumps(binding),
                                    text=True, capture_output=True, env=env, check=False)
            self.assertEqual(0, result.returncode, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(binding['manifest_sha256'], receipt['manifest_sha256'])
            self.assertEqual(receipt['structure_sha256'], sha256((output / 'structure.json').read_bytes()).hexdigest())
            self.assertEqual(binding['manifest_sha256'], json.loads((output / 'structure.json').read_bytes())['project']['sha256'])
            descriptor = (output / 'model.json').read_bytes()
            self.assertEqual(receipt['model_descriptor_sha256'], sha256(descriptor).hexdigest())
            model = json.loads(descriptor)
            self.assertEqual(receipt['model_sha256'], model['model_sha256'])
            for module, digest in model['modules'].items():
                self.assertEqual(digest, sha256((output / 'anechoic_runtime_model' / module).read_bytes()).hexdigest())

    def test_project_root_manifest_uses_project_relative_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = fixture(directory)
            root_manifest = Path(binding['root']) / manifest.name
            manifest.rename(root_manifest)
            binding['manifest_path'] = root_manifest.name
            result = run_worker(binding, output)
            self.assertEqual(0, result.returncode, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(binding['manifest_sha256'], receipt['manifest_sha256'])
            self.assertEqual(binding['manifest_sha256'], json.loads((output / 'structure.json').read_bytes())['project']['sha256'])

    def test_changed_pin_leaves_output_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = fixture(directory)
            env = os.environ.copy()
            env['PYTHONPATH'] = str(ENGINE)
            process = subprocess.Popen([sys.executable, "-B", '-m', 'WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared',
                                        '--output-dir', str(output)], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            process.stdin.write(json.dumps(binding))
            process.stdin.close()
            process.stdin = None
            stopped = None
            deadline = time.monotonic() + 10
            try:
                while time.monotonic() < deadline and process.poll() is None:
                    if list(output.parent.glob('.manifest-build-*')):
                        try:
                            os.kill(process.pid, signal.SIGSTOP)
                            stopped = process.pid
                        except ProcessLookupError:
                            pass
                        break
                    time.sleep(0.001)
                self.assertIsNotNone(stopped, 'Compiler process was not observed')
                manifest.write_bytes(manifest.read_bytes() + b'\n')
                os.kill(stopped, signal.SIGCONT)
                stopped = None
                stdout, stderr = process.communicate(timeout=30)
                self.assertNotEqual(0, process.returncode, stdout + stderr)
            finally:
                if stopped:
                    os.kill(stopped, signal.SIGCONT)
                if process.poll() is None:
                    process.kill()
                    process.communicate()
            self.assertEqual([], list(output.iterdir()))

    def test_rejects_symlinked_manifest_and_control(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = fixture(directory)
            target = manifest.with_suffix('.target')
            manifest.rename(target)
            manifest.symlink_to(target)
            self.assertNotEqual(0, run_worker(binding, output).returncode)
            manifest.unlink()
            target.rename(manifest)
            control = manifest.parent
            moved = control.with_name('moved-control')
            control.rename(moved)
            control.symlink_to(moved, target_is_directory=True)
            self.assertNotEqual(0, run_worker(binding, output).returncode)
            self.assertEqual([], list(output.iterdir()))

    def test_rejects_nonempty_output(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = fixture(directory)
            (output / 'keep').write_text('keep')
            self.assertNotEqual(0, run_worker(binding, output).returncode)
            self.assertEqual('keep', (output / 'keep').read_text())


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
        ticket = self.control / '__TICKETS/TASKS/EPIC_C123/AN-T-1-TASK--change.md'
        ticket.parent.mkdir(parents=True)
        ticket.write_text('Created')
        self.assertEqual(before, self.signature())
        ticket.write_text('Edited')
        self.assertEqual(before, self.signature())
        ticket = ticket.rename(ticket.with_name('AN-T-1-TASK--renamed.md'))
        self.assertEqual(before, self.signature())
        ticket.unlink()
        self.assertEqual(before, self.signature())

    def test_candidate_content_and_component_topology_affect_the_signature(self):
        sources = (
            'LAYER_1_META_ONTOLOGY_C9/_SPEC/model.md',
            'ONTOLOGY_SCORE_C82/CONTINUANT_PITCHFORK_C9/_DES/model.md',
            '__PROJECT_CONFIG/CUSTOM_MODEL/config.md',
            '002_PROJECT_CONFIG/CUSTOM_MODEL/compatibility.md',
            'LAYER_C3/CHILD_C4/_SPEC/AN-S-1-canonical-component.md',
            'LAYER_C3/CHILD_C4/AN-S-2-SPEC-COMPONENT_SEED_MANIFEST--seed.md',
        )
        for source in sources:
            with self.subTest(source=source):
                candidate = self.control / source
                candidate.parent.mkdir(parents=True, exist_ok=True)
                before = self.signature()
                self.assertIsNotNone(before)
                candidate.write_text('First')
                added = self.signature()
                self.assertNotEqual(before, added)
                candidate.write_text('Other')
                edited = self.signature()
                self.assertNotEqual(added, edited)
                moved = candidate.rename(candidate.with_name(candidate.stem + '-renamed.md'))
                self.assertNotEqual(edited, self.signature())
                moved.unlink()
                self.assertEqual(before, self.signature())
        before = self.signature()
        empty = self.control / 'LAYER_C3/EMPTY_C5'
        empty.mkdir()
        self.assertNotEqual(before, self.signature())
        empty.rmdir()
        self.assertEqual(before, self.signature())

    def test_project_selection_precedence_and_pin(self):
        shadow = self.control / 'alternate.md'
        before = self.signature()
        shadow.write_text('A native Project Manifest could use this compatibility path')
        self.assertNotEqual(before, self.signature())
        root_manifest = self.root / self.manifest.name
        self.manifest.rename(root_manifest)
        before = self.signature()
        self.assertIsNotNone(before)
        shadow.write_text('A root Manifest takes precedence over this file')
        self.assertEqual(before, self.signature())
        another_root = self.root / 'AN-S-2-PROJECT_MANIFEST--alternate.md'
        another_root.write_text('Alternate root candidate')
        self.assertNotEqual(before, self.signature())
        root_manifest.write_text('Changed binding')
        self.assertIsNone(self.signature())

    def test_replacing_a_candidate_with_identical_bytes_affects_the_signature(self):
        candidate = self.control / 'AN-S-1-canonical-component.md'
        candidate.write_text('Component')
        before = self.signature()
        self.assertIsNotNone(before)
        replacement = candidate.with_suffix('.tmp')
        replacement.write_bytes(candidate.read_bytes())
        replacement.replace(candidate)
        self.assertNotEqual(before, self.signature())

    def test_compiler_sources_affect_the_signature_and_tests_do_not(self):
        engine = self.root / 'engine'
        generator = engine / 'FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_FORMAL_MODEL_GENERATOR'
        compiler = generator / 'manifest_compiler_CS1/compiler.py'
        compiler.parent.mkdir(parents=True)
        compiler.write_text('IMPLEMENTATION = 1')
        with patch('WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared.ENGINE', engine):
            before = self.signature()
            self.assertIsNotNone(before)
            compiler.write_text('IMPLEMENTATION = 2')
            changed = self.signature()
            self.assertIsNotNone(changed)
            self.assertNotEqual(before, changed)
            helper = generator / 'manifest_property_fields.py'
            helper.write_text('FIELDS = ()')
            added = self.signature()
            self.assertIsNotNone(added)
            self.assertNotEqual(changed, added)
            suite = compiler.parent / 'manifest_compiler_CS1__tests'
            suite.mkdir()
            (suite / 'test_compiler.py').write_text('assert False')
            self.assertEqual(added, self.signature())
            compiler.unlink()
            self.assertIsNone(self.signature())

    def test_uncertain_candidates_do_not_admit_reuse(self):
        manifest = self.control / 'AN-S-1-canonical-component.md'
        manifest.symlink_to(self.manifest)
        self.assertIsNone(self.signature())
        manifest.unlink()
        manifest.mkdir()
        self.assertIsNone(self.signature())
        manifest.rmdir()

        def change_after_read(path, _limit):
            data = path.read_bytes()
            (self.control / 'NEW_C5').mkdir(exist_ok=True)
            return sha256(data).hexdigest(), len(data), ()

        with patch('WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared._read_digest', side_effect=change_after_read):
            self.assertIsNone(self.signature())


if __name__ == '__main__':
    unittest.main()
