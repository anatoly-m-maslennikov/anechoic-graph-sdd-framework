---
atom_family: SPEC
atom_id: AN-S-3091
container:
  component: C62
tier: 2
context:
  template: PKG
  lens: SPEC
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-22T09:00:09.206620+00:00"
---

## Summary

Structure Host

## Purpose

Provide the current validated Structure to consumers.

## Contract

Expose a read-only snapshot inside the Kernel process. Each operation holds
one snapshot. Validate the Model fingerprint before replacing the snapshot
atomically. Keep the last valid snapshot if compilation or validation fails.

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import PackageSpec
declare_entity(
    entity_name="Package Spec",
    instance=PackageSpec(
        package_id="pkg3",
        boundaries={"code": {"imports": [
            "structure_snapshot__pub.read_structure",
            "structure_snapshot__pub.StructureSnapshot",
        ], "exports": {
            "structure_host_pkg3__shared": None,
            "structure_host_pkg3__shared.publish_structure": None,
            "structure_host_pkg3__pub": "public",
            "structure_host_pkg3__pub.read_structure": "public",
            "structure_host_pkg3__pub.StructureSnapshot": "public",
        }}},
    ),
)
```
