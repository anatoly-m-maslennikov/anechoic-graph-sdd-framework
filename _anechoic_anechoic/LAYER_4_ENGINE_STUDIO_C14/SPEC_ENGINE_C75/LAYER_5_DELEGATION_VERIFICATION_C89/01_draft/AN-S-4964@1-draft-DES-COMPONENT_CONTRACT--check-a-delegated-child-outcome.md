---
atom_family: SPEC
atom_id: AN-S-4964
container:
  component: C89
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-4936
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:35:58.956802+00:00'
---

## Summary

Check a delegated child or sibling outcome.

## Guarantee

Compare a selected parent workflow effect with the declared and modeled outcome of a pinned child. Check the parent and child relationship and report the comparison, including conflicting and unresolved obligations. 
Compare a selected sibling workflow effect with the declared and modeled outcome of a pinned sibling. Check the declared client, selected interface, provider interface, and sibling relationship. Report conflicting and unresolved obligations.

Reject a request when the selected event, provider Manifest, or explicit provider Contract or Solution binding does not use the requested interface.

Exact call arguments and returned values remain unmodeled.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='check_child_outcome',
    output='compared',
    must_effect=(('C89.child_outcome_comparison', 'reported'),),
)
```

```python trace
declare_trace_contract(
    action='check_sibling_outcome',
    output='compared',
    must_effect=(('C89.sibling_outcome_comparison', 'reported'),),
)
```
