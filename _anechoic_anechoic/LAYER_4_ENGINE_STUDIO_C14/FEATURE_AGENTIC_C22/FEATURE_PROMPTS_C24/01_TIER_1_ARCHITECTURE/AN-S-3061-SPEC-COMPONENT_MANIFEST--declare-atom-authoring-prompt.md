---
atom_family: SPEC
atom_id: AN-S-3061
container:
  component: C24
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:29.876615+00:00"
---

## Summary

Declare ATOM_AUTHORING_PROMPT

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C54',
    name='ATOM_AUTHORING_PROMPT',
    lens_whitelist=['DES'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': []}, 'exports': {}},
 'state': {'reads': [], 'writes': []}}
```

## Boundary scope

This definition covers atom_authoring.prompt.md. The carrier instructs a consumer; it does not perform the described lifecycle calls or state effects.

## Component Contract

### Guide atom authoring

#### Guarantee

Guide creation or update of an Atom from Actor input, with source and model review and an internal gate before a Draft lifecycle call.
