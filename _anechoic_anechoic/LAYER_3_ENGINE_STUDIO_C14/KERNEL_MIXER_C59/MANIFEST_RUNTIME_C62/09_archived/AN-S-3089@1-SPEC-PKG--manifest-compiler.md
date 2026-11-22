---
atom_family: SPEC
atom_id: AN-S-3089
container:
  component: C62
tier: 2
context:
  template: PKG
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T02:04:08.430229+00:00"
---

## Summary

Manifest Compiler

## Purpose

Compile Active SPEC Manifests and the admitted Model declarations.

## Contract

Run in a short-lived process triggered through the existing source watcher. Emit complete local Model modules and a Structure snapshot validated against that Model. Record the source revisions and Model fingerprint before publication.

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import PackageSpec
declare_entity(entity_name="Package Spec", instance=PackageSpec(package_id="pkg1"))
```
