---
atom_family: SPEC
atom_id: AN-S-3062
container:
  component: C24
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:29.888212+00:00"
---

## Summary

Declare AUTONOMOUS_ATOM_REWRITE_PROMPT

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C55',
    name='AUTONOMOUS_ATOM_REWRITE_PROMPT',
    lens_whitelist=['DES'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': []}, 'exports': {}},
 'state': {'reads': [], 'writes': []}}
```

## Boundary scope

This definition covers autonomous_atom_rewrite.prompt.md. The carrier instructs a consumer; it does not perform the described lifecycle calls or state effects.

## Component Contract

### Guide autonomous atom rewrite

#### Guarantee

Guide an agent to rewrite selected Atoms while preserving source meaning, and apply an internal gate before a Draft lifecycle call.
