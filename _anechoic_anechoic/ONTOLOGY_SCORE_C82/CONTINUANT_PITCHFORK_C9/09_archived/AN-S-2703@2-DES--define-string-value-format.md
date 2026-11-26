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
  version: 2
  updated_at: 2026-10-29 09:46:50 +0400
---
## Summary

Define string Value Format

## Claim

The string Value Format admits textual string values. It does not turn null
into a string or set a property’s cardinality, uniqueness, or carrier
representation.

### Formal claim

```text
Entity/Graph Syntax > Format/string
```

## Semantics

string is the value domain selected by a `[string]` annotation on one direct
property value.
