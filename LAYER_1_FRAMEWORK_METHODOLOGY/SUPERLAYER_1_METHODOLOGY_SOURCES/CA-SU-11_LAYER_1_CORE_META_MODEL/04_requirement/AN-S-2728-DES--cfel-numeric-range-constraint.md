---
atom_family: SPEC
atom_id: AN-S-2728
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-13T05:35:43.598645+00:00'
---
## Summary

CFEL numeric range constraint

## Claim

### Prose Claim

Inside a square-bracket value Format annotation, `lower..upper` is a closed numeric interval: both endpoints are included. It constrains each direct Property value and does not state Property occurrence or value cardinality. This square-bracket value constraint is distinct from the existing curly-brace cardinality range `{:n..m}`.

## Details

```text
p:: [0..100]{:value count}
```
