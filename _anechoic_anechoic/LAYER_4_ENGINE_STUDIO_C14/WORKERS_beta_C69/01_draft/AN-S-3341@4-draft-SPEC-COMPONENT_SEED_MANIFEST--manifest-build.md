---
atom_family: SPEC
atom_id: AN-S-3341
container:
  component: C69
tier: 2
context:
  template: component_seed_manifest
  lens: SPEC
state:
  status: draft
  version: 4
  updated_at: '2026-11-24T18:57:03.296698+00:00'
---
# Manifest Build

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest

declare_entity(
    entity_name='Component Seed Manifest',
    instance=ComponentSeedManifest(
        component_seed_id='CS4',
        boundaries={
            'code': {'imports': {'only': []}, 'exports': {
                'manifest_build_CS4__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/manifest_build_CS4/manifest_build_CS4__tests']},
                'manifest_build_CS4__shared.manifest_input_signature': {'shared': ['C69', 'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/manifest_build_CS4/manifest_build_CS4__tests']},
            }},
            'io': {
                'server': {'build': {
                    'transport': 'cli',
                    'runner': 'managed_python',
                    'module': 'WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared',
                    'arguments': ['--output-dir', '<empty-generation-directory>', '[--ingested-model]'],
                    'input': 'pinned Project binding JSON; with --ingested-model, an object containing binding and model_inputs, on stdin',
                    'output': 'Manifest, Model, Model descriptor and Structure hashes as JSON on stdout; ingested builds also return Model diagnostics',
                }},
                'client': {'manifest_compiler': {
                    'transport': 'cli',
                    'runner': 'managed_python',
                    'module': 'FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.compiler',
                }},
            },
            'state': {'reads': ['pinned Project Manifest and active declarations'], 'writes': ['staged generation']},
        },
    ),
)
```

## Purpose

Build compatible Model and Structure artifacts for one pinned Project.

## Solution

Build and attest the artifacts in a private staging directory. Check the
Project Manifest digest before and after compilation. Publish the staged
directory only when both artifacts are complete. Leave activation to Kernel.

For an ingested Model build, pass the supplied Model snapshot to CS1. CS1
selects the candidate or an accepted Model, or the reviewed fallback when no
accepted Model exists. Report diagnostics. CS4 checks the compiled Structure
against the pinned Project binding and returns a failure if compilation fails.
C69 verifies the staged Structure and Model descriptor hashes against the receipt.
