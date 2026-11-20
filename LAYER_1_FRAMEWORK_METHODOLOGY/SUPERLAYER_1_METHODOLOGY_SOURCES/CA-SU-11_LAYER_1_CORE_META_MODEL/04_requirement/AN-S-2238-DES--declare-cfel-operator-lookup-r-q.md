---
identity:
  atom_id: AN-S-2238
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T07:06:14.734281+00:00'
---
## Summary

Declare CFEL operator LOOKUP(R, q)

## Claim

### Prose Claim

`LOOKUP(R, q)` is an existing contextual value expression admitted in a `?==` fallback expression. Starting at the bearer of target Property `p`, follow one existing outgoing link of declared Relation `R` at each step, in R's declared direction. Exclude the starting bearer. Resolve `q` by its full Property declaration identity and effective MODEL applicability. Return the nearest applicable nonempty authored value. Skip inapplicable Properties and empty values. An omitted value, null, or an empty string is empty. At a known end with no applicable authored value, return absence. Do not match by bare name or invent a Property slot.

A nonempty invalid value, unresolved applicability or graph fact, multiple outgoing targets, or revisiting a bearer is an error. Follow only the Relation direction named by R.

### Formal Claim

```python
# model
set_value(address='Operator//Lookup', value='"LOOKUP(R, q)"')
```

## Semantics

`Operator//Lookup` identifies the declared CFEL value-expression operator. The traversal semantics above are its complete existing contract.
