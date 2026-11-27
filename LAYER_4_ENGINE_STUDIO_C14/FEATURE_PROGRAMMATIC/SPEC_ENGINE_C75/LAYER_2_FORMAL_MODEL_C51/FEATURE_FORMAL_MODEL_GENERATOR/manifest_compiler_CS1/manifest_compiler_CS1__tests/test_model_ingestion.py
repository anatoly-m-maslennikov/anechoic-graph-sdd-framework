"""Exercise ingested Model compilation through the compiler CLI."""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import NonCallableMock
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1 import model_ingestion

ENGINE = Path(__file__).resolve().parents[6]
COMPILER = 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub'
COMPILER_SHA256 = 'a' * 64


def compile_structure(selection, model):
    return {}


def project(directory):
    root = Path(directory).resolve() / 'project'
    (root / '_anechoic_anechoic').mkdir(parents=True)
    manifest = root / 'AN-S-1-SPEC-PROJECT_MANIFEST--declare-anechoic.md'
    manifest.write_text(
        '---\natom_family: SPEC\natom_id: AN-S-1\ncontainer:\n  component: C00\ntier: -1\n'
        "context:\n  template: project_manifest\n  lens: SPEC\nstate:\n  status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nAnechoic\n\n"
        '## Claim\n\n### Formal Claim\n\n```python\nfrom anechoic.formal_claims import declare_entity\n'
        'from anechoic.model import ProjectManifest\n'
        "declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Anechoic', prefix='AN'))\n```\n")
    return root, sha256(manifest.read_bytes()).hexdigest()


def compile_model(root, digest, stage, payload):
    stage = stage.resolve()
    stage.mkdir()
    command = [sys.executable, '-B', '-P', '-m', COMPILER, str(root), '_anechoic_anechoic', digest,
               str(stage), '--ingested-model', '--attest-model']
    return subprocess.run(command, input=json.dumps(payload), text=True, capture_output=True,
                          cwd=ENGINE, env={**os.environ, 'PYTHONPATH': str(ENGINE)}, check=False)


class ModelIngestionTests(unittest.TestCase):
    def test_candidate_admission_failure_restores_accepted_model(self):
        with TemporaryDirectory() as tmp:
            root, digest = project(tmp)
            inputs = {'rows': [], 'has_c9': False, 'issues': [], 'accepted_model': None,
                      'compiler_sha256': COMPILER_SHA256}
            first = Path(tmp) / 'first'
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / 'model.json').read_text())
            stage = (Path(tmp) / 'second').resolve()
            stage.mkdir()
            args = NonCallableMock(
                spec_set=[
                    'generation',
                    'project_root',
                    'control_root',
                    'project_manifest_sha256',
                ],
                generation=stage,
                project_root=root,
                control_root='_anechoic_anechoic',
                project_manifest_sha256=digest)
            open_model = model_ingestion.open_admitted_model
            calls = 0

            def reject_candidate(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise OSError('candidate admission failed')
                return open_model(*args, **kwargs)

            with patch.object(model_ingestion, 'open_admitted_model', side_effect=reject_candidate):
                outcome = model_ingestion.compile_ingested(args, {**inputs, 'accepted_model': accepted, 'force_rebuild': True}, compile_structure)
            self.assertNotIn('error', outcome)
            self.assertEqual(accepted['model_sha256'], json.loads((stage / 'model.json').read_text())['model_sha256'])
            self.assertIn('candidate admission failed', outcome['model_diagnostics'][0]['message'])

            failed_stage = (Path(tmp) / 'third').resolve()
            failed_stage.mkdir()
            args.generation = failed_stage
            with patch.object(model_ingestion, 'open_admitted_model', side_effect=[
                    OSError('candidate admission failed'), KeyError('fallback admission failed')]):
                failure = model_ingestion.compile_ingested(args, {**inputs, 'accepted_model': accepted, 'force_rebuild': True}, compile_structure)
            self.assertIn('fallback admission failed', failure['error']['message'])
            self.assertIn('candidate admission failed', failure['model_diagnostics'][0]['message'])

    def test_identical_inputs_reuse_and_force_rebuild(self):
        with TemporaryDirectory() as tmp:
            root, digest = project(tmp)
            inputs = {'rows': [], 'has_c9': False, 'issues': [], 'accepted_model': None,
                      'compiler_sha256': COMPILER_SHA256}
            first = Path(tmp) / 'first'
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / 'model.json').read_text())
            self.assertIn('model_inputs_sha256', accepted)
            stage = (Path(tmp) / 'second').resolve()
            stage.mkdir()
            args = NonCallableMock(
                spec_set=[
                    'generation',
                    'project_root',
                    'control_root',
                    'project_manifest_sha256',
                ],
                generation=stage,
                project_root=root,
                control_root='_anechoic_anechoic',
                project_manifest_sha256=digest)
            with patch.object(model_ingestion, 'write_model_records', wraps=model_ingestion.write_model_records) as compile_records:
                outcome = model_ingestion.compile_ingested(args, {**inputs, 'accepted_model': accepted}, compile_structure)
                self.assertNotIn('error', outcome)
                compile_records.assert_not_called()
                self.assertIn('structure', outcome)
                args.generation = (Path(tmp) / 'third').resolve()
                args.generation.mkdir()
                outcome = model_ingestion.compile_ingested(args, {**inputs, 'accepted_model': accepted, 'force_rebuild': True}, compile_structure)
                self.assertNotIn('error', outcome)
                compile_records.assert_called_once()

    def test_changed_compiler_fingerprint_rebuilds_identical_rows(self):
        with TemporaryDirectory() as tmp:
            root, digest = project(tmp)
            inputs = {'rows': [], 'has_c9': False, 'issues': [], 'accepted_model': None,
                      'compiler_sha256': COMPILER_SHA256}
            first = Path(tmp) / 'first'
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / 'model.json').read_text())
            second = Path(tmp) / 'second'
            result = compile_model(root, digest, second, {**inputs, 'accepted_model': accepted,
                                                          'compiler_sha256': 'b' * 64})
            self.assertEqual(0, result.returncode, result.stderr)
            rebuilt = json.loads((second / 'model.json').read_text())
            self.assertNotEqual(accepted['model_inputs_sha256'], rebuilt['model_inputs_sha256'])

    def test_incompatible_matching_asset_rebuilds(self):
        with TemporaryDirectory() as tmp:
            root, digest = project(tmp)
            inputs = {'rows': [], 'has_c9': False, 'issues': [], 'accepted_model': None,
                      'compiler_sha256': COMPILER_SHA256}
            first = Path(tmp) / 'first'
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / 'model.json').read_text())
            accepted['class_modules']['MissingModelType'] = next(iter(accepted['class_modules'].values()))
            second = Path(tmp) / 'second'
            result = compile_model(root, digest, second, {**inputs, 'accepted_model': accepted})
            self.assertEqual(0, result.returncode, result.stderr)
            rebuilt = json.loads((second / 'model.json').read_text())
            self.assertNotIn('MissingModelType', rebuilt['class_modules'])
            self.assertEqual(accepted['model_inputs_sha256'], rebuilt['model_inputs_sha256'])

    def test_sticky_fallback_and_tampered_rejection(self):
        with TemporaryDirectory() as tmp:
            root, digest = project(tmp)
            inputs = {'rows': [], 'has_c9': False, 'issues': [], 'accepted_model': None,
                      'compiler_sha256': COMPILER_SHA256}
            first = Path(tmp) / 'first'
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / 'model.json').read_text())
            second = Path(tmp) / 'second'
            result = compile_model(root, digest, second, {**inputs, 'has_c9': True, 'accepted_model': accepted})
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(accepted['model_sha256'], json.loads((second / 'model.json').read_text())['model_sha256'])
            self.assertEqual(accepted['model_inputs_sha256'], json.loads((second / 'model.json').read_text())['model_inputs_sha256'])
            self.assertIn('No active Model Claims', json.loads(result.stdout)['model_diagnostics'][0]['message'])
            accepted['module_sources']['__init__.py'] = 'tampered'
            result = compile_model(root, digest, Path(tmp) / 'third',
                                   {**inputs, 'has_c9': True, 'accepted_model': accepted})
            self.assertNotEqual(0, result.returncode)
            failure = json.loads(result.stderr)
            self.assertIn('hash mismatch', failure['error']['message'])
            self.assertEqual(1, len(failure['model_diagnostics']))

    def test_incompatible_fallback_keeps_the_candidate_diagnostic(self):
        with TemporaryDirectory() as tmp:
            root, digest = project(tmp)
            inputs = {'rows': [], 'has_c9': False, 'issues': [], 'accepted_model': None,
                      'compiler_sha256': COMPILER_SHA256}
            first = Path(tmp) / 'first'
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / 'model.json').read_text())
            accepted['class_modules']['MissingModelType'] = next(iter(accepted['class_modules'].values()))
            failed = compile_model(root, digest, Path(tmp) / 'failed',
                                   {**inputs, 'has_c9': True, 'accepted_model': accepted})
            self.assertNotEqual(0, failed.returncode)
            failure = json.loads(failed.stderr)
            self.assertIn('MissingModelType', failure['error']['message'])
            self.assertIn('No active Model Claims', failure['model_diagnostics'][0]['message'])

    def test_invalid_envelope_rejected(self):
        with TemporaryDirectory() as tmp:
            root, digest = project(tmp)
            result = compile_model(root, digest, Path(tmp) / 'stage', {'rows': []})
            self.assertNotEqual(0, result.returncode)
            self.assertEqual([], json.loads(result.stderr)['model_diagnostics'])
