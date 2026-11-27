"""Check compiled Structure purposes and pinned formal boundaries."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import verify_formal_chain
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_1_SOURCE_ADAPTERS_C95._package__shared import SpecSnapshot

ROOT = next(path for path in Path(__file__).resolve().parents if (path / '_anechoic_anechoic').is_dir())
PINS = ({'path': '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15/SPEC_ENGINE_C75/01_draft/AN-S-5018@5-draft-SPEC-COMPONENT_MANIFEST--declare-project-structure.md', 'atom_id': 'AN-S-5018', 'version': 5, 'status': 'draft', 'container_component': 'C75'}, {'path': '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15/SPEC_ENGINE_C75/LAYER_2_PROJECT_STRUCTURE_C93/01_draft/AN-S-5019@3-draft-DES-SOLUTION--compile-a-project-structure-snapshot.md', 'atom_id': 'AN-S-5019', 'version': 3, 'status': 'draft', 'container_component': 'C93'})


def rows():
    result = []
    for pin in PINS:
        path = ROOT / pin['path']
        raw = path.read_bytes()
        carrier = parse_carrier(raw, path)
        result.append({'source_path': pin['path'], 'exact_ref': f"{pin['atom_id']}@{pin['version']}-draft",
                       'metadata': carrier.metadata, 'body': carrier.body, 'sha256': hashlib.sha256(raw).hexdigest()})
    return result


class FormalCandidateTest(unittest.TestCase):
    def test_pinned_contract_keeps_unobserved_bound_effects_unresolved(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean is unavailable')
        sources = rows()
        result = verify_formal_chain(SpecSnapshot(sources), 'C93', PINS[0], solution=PINS[1], action='compile_project_structure', lean=lean)
        self.assertEqual('compared', result['outcome'], result)
        effect, = (fact for fact in result['evidence']['coverage'] if fact['key'] == 'must_effect')
        self.assertEqual('unresolved', effect['status'])
        original = "'target': 'C93.structure_snapshot', 'outcome': 'ready'"
        contrary = original.replace('ready', 'generated_contrary')
        self.assertGreaterEqual(sources[1]['body'].count(original), 1)
        body = sources[1]['body'].replace(original, contrary, 1)
        sources[1] = {**sources[1], 'body': body, 'sha256': hashlib.sha256(body.encode()).hexdigest()}
        result = verify_formal_chain(SpecSnapshot(sources), 'C93', PINS[0], solution=PINS[1], action='compile_project_structure', lean=lean)
        self.assertEqual('compared', result['outcome'], result)
        effect, = (fact for fact in result['evidence']['coverage'] if fact['key'] == 'must_effect')
        self.assertEqual('unresolved', effect['status'])


PROJECT = ROOT / 'AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md'

LEGACY_COMPONENT = '''---
atom_family: SPEC
atom_id: AN-S-3039
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 4
  updated_at: '2026-11-23T13:46:18.273025+00:00'
---

## Summary

Declare Engine Studio

## Purpose

Consume Environments. DevOps builds Engine Studio.

This Component delegates implementation to its child Components.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C14',
        name='Engine Studio',
        layer=4,
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={'code': {'imports': [], 'exports': {}}},
    ),
)
```
'''


def compile_project(root, control, manifest):
    stage = root / 'stage'
    stage.mkdir()
    engine = ROOT / 'LAYER_4_ENGINE_STUDIO_C14'
    digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    process = subprocess.run(
        [sys.executable, '-B', '-P', '-m', 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub',
         str(root), control.name, digest, str(stage), '--build-model'],
        cwd=engine, env={**os.environ, 'PYTHONPATH': str(engine)}, text=True,
        capture_output=True, timeout=60,
    )
    if process.returncode:
        raise AssertionError(process.stderr)
    return json.loads(process.stdout)


class StructurePurposeTest(unittest.TestCase):
    def test_component_and_seed_purposes_survive_compilation(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        control = root / '_anechoic_anechoic'
        (control / '_SPEC').mkdir(parents=True)
        project = root / PROJECT.name
        shutil.copyfile(PROJECT, project)
        (control / '_SPEC' / 'AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md').write_text(LEGACY_COMPONENT)
        seed = control / '_SPEC/AN-S-4000-SPEC-COMPONENT_SEED_MANIFEST--test.md'
        seed.write_text("""---
atom_family: SPEC
atom_id: AN-S-4000
container: {component: C00}
tier: 2
context: {template: component_seed_manifest, lens: SPEC}
state: {status: active, version: 1, updated_at: '2026-11-20T00:00:00Z'}
---
# Seed

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest
declare_entity(entity_name='Component Seed Manifest', instance=ComponentSeedManifest(component_seed_id='CS4000'))
```

## Purpose

Build the Seed.
""")
        snapshot = compile_project(root, control, project)
        self.assertEqual('Consume Environments. DevOps builds Engine Studio.\n\n'
                         'This Component delegates implementation to its child Components.',
                         snapshot['components']['C14']['purpose'])
        self.assertEqual('Build the Seed.', snapshot['packages']['CS4000']['fields']['purpose'])
