---
atom_family: SPEC
atom_id: AN-S-3394
container:
  component: C73
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-23T04:32:26.395669+00:00'
---
## Summary

Declare Code-to-Lean

## Purpose

Derive bounded Lean models from authored implementation and Realization Graph facts, including code units, calls, conditions, and effects. Keep source references and report unresolved coverage. Compare with the Lean model supplied by Spec Engine when a matching Spec exists.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C74',
        name='Code-to-Lean',
        lens_whitelist=['DES', 'SPEC'],
    ),
)
```
