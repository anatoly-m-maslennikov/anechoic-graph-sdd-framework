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
  version: 4
  updated_at: "2026-11-22T07:51:44.870908+00:00"
---

## Summary

Structure Host

## Purpose

Provide the current validated Structure to consumers.

## Contract

Run as a thin, long-lived process. Publish a read-only snapshot API. Each operation holds one snapshot. Atomically replace it on successful compilation and retain the last valid snapshot on failure.

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
            "structure_host_pkg3__shared.main": None,
            "structure_host_pkg3__pub": "public",
            "structure_host_pkg3__pub.read_structure": "public",
            "structure_host_pkg3__pub.StructureSnapshot": "public",
        }}},
    ),
)
```
