---
atom_family: SPEC
atom_id: AN-S-4960
container:
  component: C86
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-4933
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:35:58.956802+00:00'
---

## Summary

Validate the Lean translation.

## Guarantee

Compare emitted Lean declarations with the normalized source and check executable shape metadata. Check framing with finite byte witnesses and report the witness bounds. Passing those witnesses does not establish unbounded framing equivalence. Report conflicting and unverified expectations.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='validate_translation',
    output='matched',
    must_effect=(('C86.lean_declarations', 'validated'),),
    forbid_effect=('C86.translation_findings',),
)
```

```python trace
declare_trace_contract(
    action='validate_translation',
    output='conflicting',
    must_effect=(('C86.translation_findings', 'reported'),),
)
```

```python trace
declare_trace_contract(
    action='validate_translation',
    output='unresolved',
    must_effect=(('C86.translation_findings', 'reported'),),
)
```
