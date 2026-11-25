---
atom_family: SPEC
atom_id: AN-S-2600
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T23:01:36.725119+00:00"
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
