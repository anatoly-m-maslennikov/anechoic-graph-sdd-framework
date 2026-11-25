---
atom_family: SPEC
atom_id: AN-S-3344
container:
  component: C67
tier: 2
context:
  template: component_seed_manifest
  lens: SPEC
state:
  status: draft
  version: 3
  updated_at: '2026-11-24T17:29:29+00:00'
---
# Structure Host

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest

declare_entity(
    entity_name='Component Seed Manifest',
    instance=ComponentSeedManifest(
        component_seed_id='CS6',
        boundaries={
            'code': {'imports': {'only': []}, 'exports': {'structure_host_CS6__shared.read_structure': 'shared'}},
            'state': {'reads': ['accepted Kernel generation'], 'writes': []},
        },
    ),
)
```

## Purpose

Expose the accepted Structure to the Database Server in the Kernel process.

## Solution

Query `mrt_project_structure` for the accepted generation. Render JSON transiently when the caller requires it, and return the generation ID with the Structure. Before the first admission, report that no generation is available.
