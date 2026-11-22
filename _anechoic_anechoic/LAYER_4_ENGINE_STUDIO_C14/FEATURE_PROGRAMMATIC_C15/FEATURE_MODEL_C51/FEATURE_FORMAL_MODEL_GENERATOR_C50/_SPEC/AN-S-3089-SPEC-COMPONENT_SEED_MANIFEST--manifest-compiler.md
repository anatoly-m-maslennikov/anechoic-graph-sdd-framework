---
atom_family: SPEC
atom_id: AN-S-3089
container:
  component: C50
tier: 2
context:
  template: component_seed_manifest
  lens: SPEC
state:
  status: active
  version: 4
  updated_at: '2026-11-22T09:00:09.153120+00:00'
---

# Manifest Compiler

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest

declare_entity(
    entity_name="Component Seed Manifest", instance=ComponentSeedManifest(component_seed_id="CS1")
)
```

## Purpose

Compile Active SPEC Manifests and the admitted Model declarations.

## Solution

Run as a short-lived Model Generator worker. Emit Model modules and a JSON descriptor
with admitted bindings, source revisions, and fingerprints. Attest the
descriptor for the launcher. A Structure refresh uses the admitted
descriptor digest and emits a snapshot validated against that Model.

For image admission, compile and verify staged Model sources and return
their fingerprint. With no staged sources, return the reviewed Model
fingerprint.
