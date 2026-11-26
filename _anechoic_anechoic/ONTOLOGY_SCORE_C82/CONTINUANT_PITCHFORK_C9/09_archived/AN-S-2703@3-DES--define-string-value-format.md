---
atom_family: SPEC
atom_id: AN-S-2703
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define string Value Format

## Claim

The string Value Format admits textual string values. It does not turn null
into a string or set a property’s cardinality, uniqueness, or carrier
representation.

### Formal claim

```text
CFEL > Format/string
```

## Semantics

string is the value domain selected by a `[string]` annotation on one direct
property value.
