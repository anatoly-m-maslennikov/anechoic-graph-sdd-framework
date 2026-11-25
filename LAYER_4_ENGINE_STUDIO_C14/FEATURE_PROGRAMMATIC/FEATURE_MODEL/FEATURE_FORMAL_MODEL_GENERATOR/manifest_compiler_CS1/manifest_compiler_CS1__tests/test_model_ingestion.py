"""Exercise ingested Model compilation through the compiler CLI."""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ENGINE = Path(__file__).resolve().parents[5]
COMPILER = 'FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.compiler'


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
    def test_sticky_fallback_and_tampered_rejection(self):
        with TemporaryDirectory() as tmp:
            root, digest = project(tmp)
            inputs = {'rows': [], 'has_c9': False, 'issues': [], 'accepted_model': None}
            first = Path(tmp) / 'first'
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / 'model.json').read_text())
            second = Path(tmp) / 'second'
            result = compile_model(root, digest, second, {**inputs, 'has_c9': True, 'accepted_model': accepted})
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(accepted['model_sha256'], json.loads((second / 'model.json').read_text())['model_sha256'])
            self.assertIn('No active Model Claims', json.loads(result.stdout)['model_diagnostics'][0]['message'])
            accepted['module_sources']['__init__.py'] = 'tampered'
            result = compile_model(root, digest, Path(tmp) / 'third',
                                   {**inputs, 'has_c9': True, 'accepted_model': accepted})
            self.assertNotEqual(0, result.returncode)
            failure = json.loads(result.stderr)
            self.assertIn('hash mismatch', failure['error']['message'])
            self.assertEqual(1, len(failure['model_diagnostics']))

    def test_invalid_envelope_rejected(self):
        with TemporaryDirectory() as tmp:
            root, digest = project(tmp)
            result = compile_model(root, digest, Path(tmp) / 'stage', {'rows': []})
            self.assertNotEqual(0, result.returncode)
            self.assertEqual([], json.loads(result.stderr)['model_diagnostics'])
