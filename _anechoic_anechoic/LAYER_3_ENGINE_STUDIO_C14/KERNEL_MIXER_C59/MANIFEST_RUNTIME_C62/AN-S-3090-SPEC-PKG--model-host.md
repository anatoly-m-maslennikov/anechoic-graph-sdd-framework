---
atom_family: SPEC
atom_id: AN-S-3090
structure:
  container:
    component: C62
context:
  template: PKG
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T10:40:29.349219+00:00'
---

## Summary

Model Host

## Purpose

Provide the loaded Model to implementation and validators.

## Contract

Run as a thin, long-lived process. Consumers import only the compiled types and rules they need. Activate a new Model generation by restarting the host and consumers that imported the previous Model.

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import PackageSpec
declare_entity(entity_name="Package Spec", instance=PackageSpec(package_id="pkg2"))
```
