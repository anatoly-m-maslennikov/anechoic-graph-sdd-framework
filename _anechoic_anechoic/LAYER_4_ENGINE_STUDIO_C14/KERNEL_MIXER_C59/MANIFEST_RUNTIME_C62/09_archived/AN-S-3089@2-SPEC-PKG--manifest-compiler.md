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
  version: 2
  updated_at: "2026-11-22T03:41:35.584627+00:00"
---

## Summary

Manifest Compiler

## Purpose

Compile Active SPEC Manifests and the admitted Model declarations.

## Contract

Run in a short-lived process. Emit Model modules and a JSON descriptor
with admitted bindings, source revisions, and fingerprints. Attest the
descriptor for the launcher. A Structure refresh uses the admitted
descriptor digest and emits a snapshot validated against that Model.

For image admission, compile and verify staged Model sources and return
their fingerprint. With no staged sources, return the reviewed Model
fingerprint.

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import PackageSpec
declare_entity(entity_name="Package Spec", instance=PackageSpec(package_id="pkg1"))
```
