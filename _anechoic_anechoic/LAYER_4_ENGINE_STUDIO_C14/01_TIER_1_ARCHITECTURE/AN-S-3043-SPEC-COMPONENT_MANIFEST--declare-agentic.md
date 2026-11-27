---
atom_family: SPEC
atom_id: AN-S-3043
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:25.675819+00:00"
---

## Summary

Declare AGENTIC

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C22',
    name='AGENTIC',
    lens_whitelist=['DES', 'DevOps', 'SPEC', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': [], 'exports': {}},
 'state': {'reads': [], 'writes': []}}
```

## Boundary scope

This definition delegates prompt guidance to C24 and skill guidance to C23. Its direct definition has no executable imports, exports, reads, or writes. The delegated Components retain their own boundaries.

## Component Contract

### Supply agent guidance

#### Guarantee

Supply prompt and skill guidance for agent work. The guidance is consumed by an agent and does not itself execute an operation.
