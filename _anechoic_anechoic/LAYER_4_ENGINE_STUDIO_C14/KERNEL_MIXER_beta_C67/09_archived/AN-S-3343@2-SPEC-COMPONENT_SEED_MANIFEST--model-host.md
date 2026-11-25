---
atom_family: SPEC
atom_id: AN-S-3343
container:
  component: C67
tier: 2
context:
  template: component_seed_manifest
  lens: SPEC
state:
  status: archived
  version: 2
  updated_at: "2026-11-22T12:39:43.663007+00:00"
---
# Model Host

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest

declare_entity(
    entity_name='Component Seed Manifest',
    instance=ComponentSeedManifest(
        component_seed_id='CS5',
        boundaries={
            'code': {'imports': {'only': []}, 'exports': {'model_host_CS5__shared.reviewed_native_model': 'shared'}},
            'state': {'reads': ['accepted Kernel generation'], 'writes': []},
        },
    ),
)
```

## Purpose

Expose the accepted Model to the Database Server in the Kernel process.

## Solution

Read the Model bytes and generation ID together from the accepted
database record. Before the first admission, report that no generation
is available.
