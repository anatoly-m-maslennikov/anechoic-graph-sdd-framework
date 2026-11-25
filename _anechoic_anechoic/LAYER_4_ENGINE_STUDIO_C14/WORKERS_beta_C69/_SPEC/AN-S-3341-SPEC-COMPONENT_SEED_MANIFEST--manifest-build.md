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
  status: active
  version: 4
  updated_at: "2026-11-25T10:31:29.590036+00:00"
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
                    'arguments': ['--output-dir', '<empty-generation-directory>'],
                    'optional_arguments': ['--ingested-model'],
                    'input': 'pinned Project binding JSON or binding and captured Model sources on stdin',
                    'output': 'Model and Structure artifact hashes as JSON on stdout',
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
