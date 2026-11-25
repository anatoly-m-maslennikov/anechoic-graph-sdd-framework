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
  version: 3
  updated_at: "2026-11-24T23:12:55.813309+00:00"
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
            'code': {'imports': {'only': []}},
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
