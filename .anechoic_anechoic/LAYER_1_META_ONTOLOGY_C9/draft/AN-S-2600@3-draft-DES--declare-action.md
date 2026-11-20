---
identity:
  atom_id: AN-S-2600
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 3
  updated_at: 2026-11-05 02:11:07 +0400
---

## Summary

Declare Action

## Claim

### Formal Claim

```python
# model
subject_path(address='Atom/(.Header.Context.Role in (Operations))/Action')
relation(source='Action', name='NARROWER_THAN', target='Atom/(.Header.Context.Role in (Operations))')
# instances
relation(source='Action//$action', name='IS_RUN_BY', target='Step//$step', source_count='0+')
relation(source='Action//$definition', name='HAS_EXECUTION', target='Action Run//$run', source_count='0+')
```

## Semantics

An Action is a reusable operational building block. Its boundary reflects one modeled responsibility.
