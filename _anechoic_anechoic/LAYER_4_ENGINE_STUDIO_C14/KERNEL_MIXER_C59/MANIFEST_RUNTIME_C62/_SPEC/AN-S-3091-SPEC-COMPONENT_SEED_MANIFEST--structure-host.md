---
atom_family: SPEC
atom_id: AN-S-3091
container:
  component: C62
tier: 2
context:
  template: component_seed_manifest
  lens: SPEC
state:
  status: active
  version: 8
  updated_at: "2026-11-22T15:04:56.234992+00:00"
---

# Structure Host

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest

declare_entity(
    entity_name="Component Seed Manifest",
    instance=ComponentSeedManifest(
        component_seed_id="CS3",
        boundaries={
            "code": {
                "imports": [
                    "ADAPTERS_C30__shared.read_structure",
                ],
                "exports": {
                    "structure_host_CS3__shared": None,
                    "structure_host_CS3__shared.publish_structure": None,
                },
            }
        },
    ),
)
```

## Purpose

Provide the current validated Structure to consumers.

## Solution

Publish the Structure snapshot inside the Kernel process. Validate its
Model fingerprint before replacing the snapshot atomically. Keep the last
valid snapshot if compilation or validation fails. Consumers read the
published artifact through the Structure reader owned by Adapters.
