from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from .. import manifest_build_CS4__pub as worker

ENGINE = Path(__file__).resolve().parents[3]
PROJECT = 'AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md'
MANIFEST = '''---
atom_family: SPEC
atom_id: AN-S-3037
container:
  component: C00
tier: -1
context:
  template: project_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: "2026-11-22T10:58:11+00:00"
---

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Anechoic', prefix='AN', lens_whitelist=['SPEC']))
```
'''


class BuildTests(unittest.TestCase):
    def fixture(self, base):
        base = Path(base).resolve()
        root = base / 'project'
        control = root / '_anechoic_anechoic'
        control.mkdir(parents=True)
        manifest = control / PROJECT
        manifest.write_text(MANIFEST)
        output = Path(base) / 'generation'
        output.mkdir()
        binding = {'root': str(root), 'control_root': control.name, 'manifest_path': manifest.name,
                   'manifest_sha256': sha256(manifest.read_bytes()).hexdigest(), 'project_prefix': 'AN'}
        return binding, output, manifest

    def test_cli_build_and_verify_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = self.fixture(directory)
            env = os.environ.copy()
            env['PYTHONPATH'] = str(ENGINE)
            result = subprocess.run([sys.executable, '-m', 'WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__pub',
                                     '--output-dir', str(output)], input=json.dumps(binding),
                                    text=True, capture_output=True, env=env)
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
            binding, output, manifest = self.fixture(directory)
            root_manifest = Path(binding['root']) / manifest.name
            manifest.rename(root_manifest)
            binding['manifest_path'] = root_manifest.name
            receipt = worker.build(binding, output)
            self.assertEqual(binding['manifest_sha256'], receipt['manifest_sha256'])
            self.assertEqual(binding['manifest_sha256'], json.loads((output / 'structure.json').read_bytes())['project']['sha256'])

    def test_changed_pin_leaves_output_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, manifest = self.fixture(directory)
            original = worker.compile_generation
            def mutate(selection, model):
                result = original(selection, model)
                manifest.write_bytes(manifest.read_bytes() + b'\n')
                return result
            with patch.object(worker, 'compile_generation', side_effect=mutate):
                with self.assertRaises(ValueError):
                    worker.build(binding, output)
            self.assertEqual([], list(output.iterdir()))

    def test_rejects_nonempty_output(self):
        with tempfile.TemporaryDirectory() as directory:
            binding, output, _ = self.fixture(directory)
            (output / 'keep').write_text('keep')
            with self.assertRaises(ValueError):
                worker.build(binding, output)
            self.assertEqual('keep', (output / 'keep').read_text())


if __name__ == '__main__':
    unittest.main()
