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
  version: 6
  updated_at: '2026-11-22T09:00:09.199236+00:00'
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
                    "structure_snapshot__pub.read_structure",
                    "structure_snapshot__pub.StructureSnapshot",
                ],
                "exports": {
                    "structure_host_CS3__shared": None,
                    "structure_host_CS3__shared.publish_structure": None,
                    "structure_host_CS3__pub": "public",
                    "structure_host_CS3__pub.read_structure": "public",
                    "structure_host_CS3__pub.StructureSnapshot": "public",
                },
            }
        },
    ),
)
```

## Purpose

Provide the current validated Structure to consumers.

## Solution

Expose a read-only snapshot inside the Kernel process. Each operation holds
one snapshot. Validate the Model fingerprint before replacing the snapshot
atomically. Keep the last valid snapshot if compilation or validation fails.
