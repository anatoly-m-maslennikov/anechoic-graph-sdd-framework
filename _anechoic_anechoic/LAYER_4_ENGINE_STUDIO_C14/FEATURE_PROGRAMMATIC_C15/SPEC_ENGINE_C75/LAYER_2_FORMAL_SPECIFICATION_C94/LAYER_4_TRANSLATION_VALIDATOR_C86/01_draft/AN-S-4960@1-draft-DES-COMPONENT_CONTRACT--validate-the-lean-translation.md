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

Compare emitted Lean declarations with the normalized source and check
applicable executable shapes. Report conflicts and unresolved expectations.
If the framing witnesses pass on the default path, report the witness count
and leave framing equivalence unresolved.

On a bounded framing request, return `bounded_match` when the declaration
checks and the finite byte witnesses for both framing roles pass and no issue
or unresolved translation finding remains. Report the witness input bytes,
the results for both roles, and unresolved coverage. Unbounded framing
equivalence remains unresolved.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='validate_translation',
    output='matched',
    must_effect=(('C86.lean_declarations', 'validated', {'model': 'request_normalized_model'}),),
    forbid_effect=('C86.translation_findings',),
)
```

```python trace
declare_trace_contract(
    action='validate_translation',
    output='bounded_match',
    must_effect=(('C86.framing_comparison', 'reported'),),
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
