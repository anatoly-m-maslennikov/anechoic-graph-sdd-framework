---
atom_family: SPEC
atom_id: AN-S-2136
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 34
  updated_at: '2026-11-12T19:34:39.244837+00:00'
---
## Summary

Materialize Content Role Directories on First Artifact

## Claim

### Prose Claim

Within a Scope Unit, derive the Role folder from the Role Declaration selected by `Header.Context.Role`.

1. Pad its Role Order Number to at least two decimal digits.
2. Encode the canonical Role name in lowercase snake case.
3. Join the two parts with one underscore.

Create the folder when the first Atom needs it. The applicable Status and Container layout determines the remaining placement.

### Formal Claim

```python
placement_rules = ({"kind": "role_root"},)
```
