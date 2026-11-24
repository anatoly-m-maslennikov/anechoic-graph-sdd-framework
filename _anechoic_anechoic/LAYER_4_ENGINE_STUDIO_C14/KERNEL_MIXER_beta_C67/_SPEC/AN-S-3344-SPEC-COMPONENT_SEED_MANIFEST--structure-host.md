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
  status: active
  version: 2
  updated_at: "2026-11-22T12:39:43.763843+00:00"
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

Read the Structure bytes and generation ID together from the accepted
database record. Before the first admission, report that no generation
is available.
