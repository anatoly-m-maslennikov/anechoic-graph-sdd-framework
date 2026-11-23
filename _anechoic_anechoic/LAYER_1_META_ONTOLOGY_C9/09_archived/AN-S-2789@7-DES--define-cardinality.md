---
atom_family: SPEC
atom_id: AN-S-2789
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: '2026-11-13T06:26:02.151784+00:00'
---
## Summary

Define Cardinality

## Claim

### Prose Claim


Cardinality is CFEL syntax for expressing the allowed number of direct values,
dependent Properties, Relation instances or contained parts.



The forms are `{:n}`, `{:n+}` and `{:n..m}` with non-negative integer bounds.

### Formal Claim

```python
# model
composition(container='CFEL', parts=('Cardinality',))
```

