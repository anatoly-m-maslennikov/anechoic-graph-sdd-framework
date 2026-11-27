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
  version: 5
  updated_at: '2026-11-26T19:48:53.099592+00:00'
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
                    'input': 'pinned Project binding JSON or binding and staged Project Spec rows on stdin',
                    'output': 'Model and Structure artifact hashes as JSON on stdout',
                }},
                'client': {'manifest_compiler': {
                    'transport': 'cli',
                    'runner': 'managed_python',
                    'module': 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub',
                }},
            },
            'state': {'reads': ['staged Project Spec rows and accepted Model for managed builds', 'pinned Project carrier files for offline builds'], 'writes': ['staged generation']},
        },
    ),
)
```

## Purpose

Build compatible Model and Structure artifacts for one pinned Project.

## Solution

Build and attest the artifacts in a private staging directory. Check the
Project Manifest pin against the staged rows for managed builds. Check the
file before and after an offline build. Publish the staged
directory only when both artifacts are complete. Leave activation to Kernel.

The managed build receives the bootstrap Model and the Project Spec rows
read from one DuckDB snapshot. Reuse the accepted Model when its input
witness matches. Compile a new candidate from the snapshot on a miss or
explicit Model rebuild. Validate Structure against the selected Model and
stage both for admission.
