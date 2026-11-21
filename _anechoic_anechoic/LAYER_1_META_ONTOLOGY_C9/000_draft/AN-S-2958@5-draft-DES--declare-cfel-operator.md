---
atom_family: SPEC
atom_id: AN-S-2958
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T07:05:38.647579+00:00'
---

## Summary

Declare CFEL operator $

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//InstanceBinding', value='"$"')
```

## Semantics

Bind an existing selected instance or read its bound Property; it creates nothing. A variable introduced by a standalone typed instance selector such as `Kind//$x;` remains in scope for following statements in the same CFEL fenced block. A variable introduced in an IF condition is in scope within that condition and its matching THEN group only; it is not in scope in following statements. If an outer variable is already bound, a new binding inside IF must use a different variable name; references to the outer variable retain its existing identity.
